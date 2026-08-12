import os
import time
import uuid
import random
import logging

from core.utils.telemetry import setup_distributed_logger
from core.execution.exceptions import OptimisticLockError

from infra.db.connection import get_connection
from infra.db.control_repo import ControlPlaneRepository
from infra.db.materialized_repo import MaterializedPlaneRepository
from infra.db.fsm_repository import FSMRepository
from core.ast.registry import ASTRegistry
from apps.compiler.tectonic_runner import HostTectonicRunner
from core.compiler.rendering.models import RenderGeometry, AssetReference


from core.execution.handlers import DocumentCommandHandler
from core.execution.state import (
    DocumentState,
    StartAssemblyCommand,
    MarkCompilationReadyCommand,
    StartCompilationCommand,
    CompleteDocumentCommand,
    FailDocumentCommand
) 

from core.compiler.service import CompilationService
from core.compiler.context_resolver import CQRSAssemblyContextResolver
from core.compiler.assembler import DocumentAssembler, AssemblyPolicy
from core.compiler.rendering.mapper import DefaultRenderUnitMapper
from infra.db.profile_store import InMemoryProfileStore
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
        """
        NADR-06 §5.3 R9-R12: Procesamiento gobernado por CompilationService.
        El daemon orquesta FSM, no ensambla.
        """
        start_assembly = time.perf_counter()
        logger.info("Iniciando compilación del documento...", extra={"extra_data": {"doc": doc_id}})

        current_version = None
        try:
            status = self.fsm.get_status(doc_id, ast_hash)
            if not status:
                raise ValueError("No se encontró el estado del documento en la FSM.")

            current_version = status.state_version

            if status.current_state == DocumentState.READY_FOR_ASSEMBLY.value:
                cmd_start = StartAssemblyCommand(doc_id, ast_hash, self.node_id, current_version)
                current_version = self.cmd_handler.handle(cmd_start)

            # Resolver contexto desde Execution Plane
            context = self.context_resolver.resolve(
                document_id=doc_id,
                ast_hash=ast_hash,
                projection_version=1
            )

            # Compilar vía servicio canónico
            tex_content = self.compilation_service.compile_document(context)

            # Transiciones FSM y compilación física
            status = self.fsm.get_status(doc_id, ast_hash)
            if not status:
                raise ValueError("FSM desincronizada antes de empaquetar TeX.")

            cmd_ready = MarkCompilationReadyCommand(doc_id, ast_hash, self.node_id, status.state_version)
            current_version = self.cmd_handler.handle(cmd_ready)

            status = self.fsm.get_status(doc_id, ast_hash)
            if not status:
                raise ValueError("FSM desincronizada antes de compilar PDF.")

            cmd_compile = StartCompilationCommand(doc_id, ast_hash, self.node_id, status.state_version)
            current_version = self.cmd_handler.handle(cmd_compile)

            output_filename = f"translated_{doc_id}.pdf"
            output_dir = os.getenv("COMPILER_OUTPUT_DIR", "output")
            os.makedirs(output_dir, exist_ok=True)

            final_pdf_path = self.runner.compile(
                tex_content,
                output_dir=output_dir,
                output_filename=output_filename
            )

            logger.info(f"Compilación exitosa: {final_pdf_path}",
                         extra={"extra_data": {"latency": time.perf_counter() - start_assembly}})

            status = self.fsm.get_status(doc_id, ast_hash)
            if not status:
                raise ValueError("FSM desincronizada en fase final de guardado.")

            cmd_complete = CompleteDocumentCommand(doc_id, ast_hash, self.node_id, status.state_version)
            self.cmd_handler.handle(cmd_complete)

        except Exception as err:
            logger.error(f"Fallo crítico durante el ensamblado/compilación para {doc_id}: {err}")
            self._fail_document_safely(doc_id, ast_hash, current_version, str(err)[:250])
            raise err
            
        finally:
            pass

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

    profile_store = InMemoryProfileStore()

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