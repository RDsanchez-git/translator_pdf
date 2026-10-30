import os
import time
import uuid
import random
import logging
import threading

from core.utils.telemetry import setup_distributed_logger
from core.execution.exceptions import OptimisticLockError

from infra.db.connection import get_connection
from infra.db.control_repo import ControlPlaneRepository
from infra.db.assembly_recovery import AssemblyLeaseRepository
from infra.db.materialized_repo import MaterializedPlaneRepository
from infra.db.fsm_repository import FSMRepository
from core.ast.registry import ASTRegistry
from apps.compiler.tectonic_runner import HostTectonicRunner
from core.compiler.rendering.models import RenderGeometry, AssetReference


from core.execution.handlers import DocumentCommandHandler
from core.execution.state import FailDocumentCommand

from core.compiler.service import CompilationService
from core.compiler.context_resolver import CQRSAssemblyContextResolver
from core.compiler.assembler import DocumentAssembler, AssemblyPolicy
from core.compiler.rendering.mapper import DefaultRenderUnitMapper
from infra.db.profile_store import SQLiteProfileStore
from infra.db.document_repository import SQLiteDocumentRepository


setup_distributed_logger()
logger = logging.getLogger("worker_assembler")

class AssemblerWorkerDaemon:
    """
    SOTA: Orquestador físico del Worker Assembler (CPU/IO Bound).
    Espera la tarea trigger, recolecta las proyecciones y compila Tectonic.
    """
    def __init__(self, control_repo, fsm_repo, cmd_handler, mat_repo, ast_registry,
                 runner, compilation_service, context_resolver):
        self.control = control_repo
        self.fsm = fsm_repo
        self.cmd_handler = cmd_handler
        self.materialized = mat_repo
        self.ast_registry = ast_registry
        self.runner = runner
        self.compilation_service = compilation_service
        self.context_resolver = context_resolver

        self.node_id = f"assembler_{uuid.uuid4().hex[:8]}"
        self.worker_type = "ASSEMBLER"
        self.base_sleep = 2.0
        self.max_sleep = 8.0

    def run(self):
        logger.info(f"Iniciando Assembler Worker Daemon [{self.node_id}] - FSM Driven (CPU/IO Bound)")
        consecutive_idle = 0
        
        while True:
            try:
                next_doc = self.fsm.find_next_ready_for_assembly()
                
                if not next_doc:
                    consecutive_idle += 1
                    sleep_time = min(self.base_sleep * (1.2 ** consecutive_idle), self.max_sleep)
                    time.sleep(sleep_time + random.uniform(0.0, 1.0))
                    continue
                
                consecutive_idle = 0
                doc_id, ast_hash = next_doc
                
                try:
                    self._process_assembly_task(doc_id, ast_hash)
                except OptimisticLockError:
                    logger.warning(f"TOCTOU Evitado: El documento {doc_id[:8]} ya fue tomado por otro nodo.")
                    continue
                
                time.sleep(random.uniform(0.5, 1.0))
                
            except Exception as e:
                logger.exception(f"Error crítico en Assembler Worker loop: {e}")
                time.sleep(self.max_sleep)

    def _fail_document_safely(self, doc_id: str, ast_hash: str, current_version: int | None, reason: str):
        """Intenta marcar el documento como fallido en FSM para evitar estados colgados."""
        if current_version is None:
            try:
                status = self.fsm.get_status(doc_id, ast_hash)
                if status:
                    current_version = status.state_version
            except Exception as read_err:
                logger.error(f"No se pudo recuperar la versión del FSM durante mitigación de desastre: {read_err}")
        
        if current_version is not None:
            try:
                cmd_fail = FailDocumentCommand(doc_id, ast_hash, self.node_id, current_version, reason=reason)
                self.cmd_handler.handle(cmd_fail)
                logger.info(f"Documento {doc_id[:8]} marcado como FAILED en FSM de forma segura.")
            except Exception as fsm_err:
                logger.critical(f"DOOMSDAY: No se pudo abortar el documento en la FSM: {fsm_err}")

    def _process_assembly_task(self, doc_id: str, ast_hash: str):
        """Lease-fenced assembly and private PDF promotion (G5/2)."""
        leases = AssemblyLeaseRepository(self.control.conn)
        lease = leases.claim(doc_id, ast_hash, self.node_id)
        if lease is None:  # Another assembler already claimed this generation.
            return

        start_assembly = time.perf_counter()
        stop_heartbeat = threading.Event()
        lease_lost = threading.Event()
        staged_pdf = None

        def heartbeat():
            # The heartbeat MUST own a separate thread-confined SQLite connection.
            connection = None
            try:
                connection = get_connection(os.getenv("QUEUE_DB_PATH", "infra/db/queue.db"), timeout=30)
                renewal = AssemblyLeaseRepository(connection)
                while not stop_heartbeat.wait(30.0):
                    if not renewal.renew(lease):
                        lease_lost.set()
                        return
            except Exception:
                logger.exception("G5_ASSEMBLER_HEARTBEAT_FAILED")
                lease_lost.set()
            finally:
                if connection is not None:
                    connection.close()

        thread = threading.Thread(target=heartbeat, name="assembler_lease_heartbeat", daemon=True)
        thread.start()
        try:
            context = self.context_resolver.resolve(
                document_id=doc_id, ast_hash=ast_hash, projection_version=1,
            )
            tex_content = self.compilation_service.compile_document(context)
            if lease_lost.is_set() or not leases.advance(lease, "ASSEMBLING", "READY_FOR_COMPILATION"):
                raise OptimisticLockError("G5_ASSEMBLER_AUTHORITY_LOST_BEFORE_COMPILATION")
            if lease_lost.is_set() or not leases.advance(lease, "READY_FOR_COMPILATION", "COMPILING"):
                raise OptimisticLockError("G5_ASSEMBLER_AUTHORITY_LOST_AT_COMPILATION")

            output_dir = os.getenv("COMPILER_OUTPUT_DIR", "output")
            os.makedirs(output_dir, exist_ok=True)
            # Tectonic may only copy to this execution-private name.
            staged_pdf = os.path.join(output_dir, f".assembly_{uuid.uuid4().hex}.pdf")
            self.runner.compile(
                tex_content, output_dir=output_dir,
                output_filename=os.path.basename(staged_pdf),
            )
            final_pdf = os.path.join(output_dir, f"translated_{doc_id}.pdf")
            if lease_lost.is_set() or not leases.publish(lease, staged_pdf, final_pdf):
                raise OptimisticLockError("G5_ASSEMBLER_STALE_PDF_PROMOTION_REJECTED")
            logger.info("G5_ASSEMBLER_PDF_PUBLISHED", extra={"extra_data": {
                "document_id": doc_id, "latency": time.perf_counter() - start_assembly,
            }})
        except Exception as error:
            # A stale owner must never mark another owner's generation FAILED.
            try:
                leases.fail_authorized(lease, str(error))
            except Exception:
                logger.exception("G5_ASSEMBLER_FAILURE_RECORDING_FAILED")
            raise
        finally:
            stop_heartbeat.set()
            thread.join(timeout=2.0)
            # Never remove another attempt's artifacts, including the final PDF.
            if staged_pdf and os.path.isfile(staged_pdf):
                os.unlink(staged_pdf)

class RenderGeometryAdapter:
    """Extrae RenderGeometry desde ASTNode.metadata.bboxes para el compiler."""
    _FALLBACK_PAGE_WIDTH = 612.0
    _FALLBACK_PAGE_HEIGHT = 792.0

    def extract(self, node) -> RenderGeometry | None:
        metadata = getattr(node, "metadata", None)
        if not metadata:
            return None
        bboxes = getattr(metadata, "bboxes", None)
        if not bboxes or len(bboxes) == 0:
            return None
        primary_bbox = bboxes[0]
        x0 = getattr(primary_bbox, "x0", None)
        y0 = getattr(primary_bbox, "y0", None)
        x1 = getattr(primary_bbox, "x1", None)
        y1 = getattr(primary_bbox, "y1", None)
        if x0 is None or y0 is None or x1 is None or y1 is None:
            return None
        pages = getattr(metadata, "pages", None)
        page_number = pages[0] if pages else 0
        return RenderGeometry(
            relative_x=x0 / self._FALLBACK_PAGE_WIDTH,
            relative_y=y0 / self._FALLBACK_PAGE_HEIGHT,
            relative_width=(x1 - x0) / self._FALLBACK_PAGE_WIDTH,
            relative_height=(y1 - y0) / self._FALLBACK_PAGE_HEIGHT,
            page_number=page_number,
        )


class RenderAssetAdapter:
    """Extrae AssetReference desde ImagePayload para el compiler."""

    def extract(self, node) -> AssetReference | None:
        from core.ast.enums import ContentNodeType
        if node.node_type != ContentNodeType.IMAGE:
            return None
        payload = node.payload
        asset_path = getattr(payload, "asset_path", None)
        if not asset_path:
            return None
        alt_text = getattr(payload, "alt_text", None)
        return AssetReference(
            path=asset_path,
            alt_text=alt_text,
            label=None,
            mime_type="image/png",
        )

if __name__ == "__main__":
    FSM_DB_PATH = os.getenv("FSM_DB_PATH", "infra/db/fsm.db")
    QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", "infra/db/queue.db")
    MAT_DB_PATH = os.getenv("MAT_DB_PATH", "infra/db/materialized.db")

    fsm_conn = get_connection(FSM_DB_PATH)
    queue_conn = get_connection(QUEUE_DB_PATH)
    mat_conn = get_connection(MAT_DB_PATH)

    for conn in (fsm_conn, queue_conn, mat_conn):
        conn.execute("PRAGMA busy_timeout=30000")

    control_repo = ControlPlaneRepository(queue_conn)
    mat_repo = MaterializedPlaneRepository(mat_conn)
    fsm_repo = FSMRepository(fsm_conn)
    cmd_handler = DocumentCommandHandler(fsm_repo, task_repo=control_repo)
    ast_registry = ASTRegistry()

    # NADR-06 §5.3: Composition root del worker de ensamblado
    doc_conn = get_connection("infra/db/documents.db", timeout=30)
    document_repository = SQLiteDocumentRepository(doc_conn)

    assembly_policy = AssemblyPolicy(
        tolerance_ratio=0.05,
        allow_fallback=True,
        degradable_failures=frozenset()
    )
    assembler = DocumentAssembler(
        repository=document_repository,
        separator="\n\n",
        policy=assembly_policy
    )

    geom_adapter = RenderGeometryAdapter()
    asset_adapter = RenderAssetAdapter()
    mapper = DefaultRenderUnitMapper(geom_adapter, asset_adapter)

    profile_store = SQLiteProfileStore(doc_conn)

    compilation_service = CompilationService(
        assembler=assembler,
        payload_repository=document_repository,
        profile_store=profile_store,
        mapper=mapper
    )

    context_resolver = CQRSAssemblyContextResolver(
        ast_provider=ast_registry,
        materialized_plane=mat_repo
    )

    runner = HostTectonicRunner()

    daemon = AssemblerWorkerDaemon(
        control_repo=control_repo,
        fsm_repo=fsm_repo,
        cmd_handler=cmd_handler,
        mat_repo=mat_repo,
        ast_registry=ast_registry,
        runner=runner,
        compilation_service=compilation_service,
        context_resolver=context_resolver
    )
    daemon.run()
