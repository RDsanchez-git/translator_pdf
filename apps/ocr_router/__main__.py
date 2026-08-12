import os
import time
import uuid
import shutil
import hashlib
import json
import traceback
import logging
from pathlib import Path

from core.utils.telemetry import setup_distributed_logger
from infra.db.connection import get_connection
from infra.db.fsm_repository import FSMRepository
from infra.db.control_repo import ControlPlaneRepository
from core.execution.handlers import DocumentCommandHandler
from core.execution.state import StartParsingCommand, StartProcessingCommand, DocumentState
from core.ast.registry import ASTRegistry
from core.ast.hashing import compute_ast_hash

from core.pipeline.orchestrator import ParserProtocol
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from core.validation.estimators import ExactBPEEstimator
from core.document_profile.models import ProfileInput
from core.document_profile.profiler import HeuristicDocumentProfiler
from apps.bootstrap.pipeline_factory import build_document_profiler


# 1. Importaciones actualizadas
from core.document_profile.ports import ProfileStore
from infra.db.profile_store import InMemoryProfileStore

setup_distributed_logger()
logger = logging.getLogger("ocr_router")

class OCRRouterDaemon:
    def __init__(self, fsm_repo: FSMRepository, task_repo: ControlPlaneRepository, 
                 cmd_handler: DocumentCommandHandler, ast_registry: ASTRegistry, 
                 document_profiler: 'HeuristicDocumentProfiler',
                 profile_store: ProfileStore, parser: ParserProtocol,  # NUEVO: inyectado por constructor
                 workspace_dir: str = "."):
        self.fsm = fsm_repo
        self.task_repo = task_repo
        self.cmd_handler = cmd_handler
        self.ast_registry = ast_registry
        self.document_profiler = document_profiler # <--- Asignación
        self.profile_store = profile_store
        self.parser = parser  # NUEVO
        self.owner_id = f"router_{uuid.uuid4().hex[:8]}"
        
        self.inbox_dir = Path(workspace_dir) / "data" / "inbox"
        self.archive_dir = Path(workspace_dir) / "data" / "archive"
        self.error_dir = Path(workspace_dir) / "data" / "error"
        
        for d in [self.inbox_dir, self.archive_dir, self.error_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def run(self):
        logger.info(f"Iniciando OCR Router Daemon [{self.owner_id}] - Vigilando: {self.inbox_dir}")
        
        while True:
            try:
                target_pdf = next(self.inbox_dir.glob("*.pdf"), None)
                if not target_pdf:
                    time.sleep(5.0)
                    continue
                
                logger.info(f"Ingesta detectada: {target_pdf.name}")
                self._process_document(target_pdf)
                
            except Exception as e:
                logger.exception(f"Error crítico en el loop del OCR Router: {e}")
                time.sleep(10.0)

    def _process_document(self, pdf_path: Path):
        start_time = time.perf_counter()
        document_id = None
        ast_hash = None

        with open(pdf_path, "rb") as f:
            document_id = hashlib.sha256(f.read()).hexdigest()
            
        logger.info("Validando estado previo de ingesta...", extra={"extra_data": {"doc_id": document_id[:8]}})
        
        # SOTA: Cortocircuito defensivo en el segundo cero.
        # Verifica duplicados por ID documental antes de instanciar los modelos de Marker.
        try:
            # Reutilizamos un método genérico o directo para leer registros existentes por ID
            is_active_or_completed = self.fsm.is_document_already_processed(document_id)
            if is_active_or_completed:
                logger.warning(f"Cortocircuito Activo: Documento {document_id[:8]} ya procesado o en cola activa. Evitando Marker.")
                # Mover de inmediato al archivo con prefijo de duplicado sin gastar CPU
                shutil.move(str(pdf_path), str(self.archive_dir / f"DUP_SHORT_{document_id[:8]}_{pdf_path.name}"))
                return
        except Exception as db_err:
            logger.error(f"Error consultando cortocircuito en FSM: {db_err}. Continuando por vía lenta de seguridad.")

        try:
            raw_ast = self.parser.parse(str(pdf_path))
            
            # SOTA Hito 3B: Inferencia y persistencia asíncrona temporal
            profile_input = ProfileInput(nodes=raw_ast)
            profiling_result = self.document_profiler.profile(profile_input)
            self.profile_store.save(document_id, profiling_result.profile)
            
            logger.info(
                f"Perfil inferido para {document_id[:8]}: "
                f"Layout={profiling_result.profile.layout}, "
                f"Tipo={profiling_result.profile.document_type}"
            )
            # NOTA DE INTEGRACIÓN: Como el Router no maneja SQLiteDocumentRepository,
            # el 'profiling_result.profile' debe guardarse junto al AST o pasarse 
            # como metadata a self.ast_registry.register_ast(...) para que el 
            # Assembler lo consuma aguas abajo.
            # =================================================================
            
            ast_hash = compute_ast_hash(raw_ast)
            
            # Instanciación de la estrategia de empaquetado semántico por tokens
            estimator = ExactBPEEstimator()
            
            # SOTA FIX: Desempaquetado estricto de la tupla (Unidades, Telemetría)
            translation_units, chunking_report = build_semantic_chunks_as_units(raw_ast, estimator)
            
            # Iteración O(N) directa sobre la colección materializada List[TranslationUnit]
            ordered_chunk_ids = [u.chunk_id for u in translation_units]
            
            # 2. Persistencia del AST Base estructural
            self.ast_registry.register_ast(document_id, ast_hash, raw_ast)

            self.ast_registry.register_ast(document_id, ast_hash, raw_ast)
            
            # 3. Control de Idempotencia de Reingesta via DTO
            self.fsm.initialize_document(document_id, ast_hash)
            status = self.fsm.get_status(document_id, ast_hash)
            
            if status and status.current_state == DocumentState.PROCESSING.value:
                logger.warning(f"Documento {document_id[:8]} ya se encuentra en procesamiento activo. Saltando transiciones.")
                shutil.move(str(pdf_path), str(self.archive_dir / f"DUP_{document_id[:8]}_{pdf_path.name}"))
                return

            # 4. Coreografía CQRS gobernada por CAS Duro sin Lease Documental
            status = self.fsm.get_status(document_id, ast_hash)
            if not status:
                raise ValueError("Fallo crítico al recuperar el DTO de inicialización en la FSM.")
                
            current_version = status.state_version
            
            cmd_parse = StartParsingCommand(document_id, ast_hash, self.owner_id, current_version)
            current_version = self.cmd_handler.handle(cmd_parse)
            
            # Inyección atómica masiva de identificadores únicos deterministas en queue.db
            self.task_repo.enqueue_tasks(document_id, ast_hash, ordered_chunk_ids)
            
            # Hot-fetch: Sincronización estricta de versión pre-comando de procesamiento
            status = self.fsm.get_status(document_id, ast_hash)
            if not status:
                raise ValueError("Desincronización de la FSM previo a la transición a PROCESSING.")
                
            cmd_process = StartProcessingCommand(document_id, ast_hash, self.owner_id, status.state_version)
            self.cmd_handler.handle(cmd_process)
            
            # 5. Archivo Histórico
            shutil.move(str(pdf_path), str(self.archive_dir / f"{document_id[:8]}_{pdf_path.name}"))
            
            latency = time.perf_counter() - start_time
            logger.info("Documento enrutado exitosamente a PROCESSING.", 
                        extra={"extra_data": {"chunks": len(ordered_chunk_ids), "latency_sec": round(latency, 1)}})
            
        except Exception as e:
            error_token = uuid.uuid4().hex[:6]
            logger.error(f"Fallo en la ingesta del documento [{error_token}] {pdf_path.name}: {e}")
            
            if document_id is not None and ast_hash is not None:
                assert isinstance(document_id, str)
                assert isinstance(ast_hash, str)
                # El control de fallas ahora es atómico por CAS; sin operaciones de liberación pendientes
                
            # Mover PDF corrupto a cuarentena
            failed_pdf_name = f"FAILED_{error_token}_{pdf_path.name}"
            if pdf_path.exists():
                shutil.move(str(pdf_path), str(self.error_dir / failed_pdf_name))
            
            # Volcado de metadatos del crash para troubleshooting sin fricción
            meta_err = {
                "timestamp": time.time(),
                "error_token": error_token,
                "file_name": pdf_path.name,
                "document_id": document_id,
                "ast_hash": ast_hash,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            with open(self.error_dir / f"FAILED_{error_token}_reason.json", "w", encoding="utf-8") as f:
                json.dump(meta_err, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    FSM_DB_PATH = os.getenv("FSM_DB_PATH", "infra/db/fsm.db")
    QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", "infra/db/queue.db")
    
    fsm_conn = get_connection(FSM_DB_PATH)
    queue_conn = get_connection(QUEUE_DB_PATH)
    
    for conn in (fsm_conn, queue_conn):
        conn.execute("PRAGMA busy_timeout=30000")

    ast_registry = ASTRegistry()
    
    # SOTA: Inyección de Profiler y Store
    profiler = build_document_profiler()
    profile_store = InMemoryProfileStore()
    
    fsm_repo = FSMRepository(fsm_conn)
    task_repo = ControlPlaneRepository(queue_conn)
    cmd_handler = DocumentCommandHandler(fsm_repo, task_repo=task_repo)
    ast_registry = ASTRegistry()
    
    # SOTA: Ensamblaje del profiler desde el Composition Root oficial
    profiler = build_document_profiler()

    # NADR-11 §5.1 R1: El Composition Root construye el parser
    from apps.bootstrap.pipeline_factory import build_extraction_pipeline
    parser = build_extraction_pipeline()
    
    daemon = OCRRouterDaemon(
        fsm_repo=fsm_repo, 
        task_repo=task_repo, 
        cmd_handler=cmd_handler, 
        ast_registry=ast_registry,
        document_profiler=profiler,
        profile_store=profile_store,
        parser=parser, 
    )
    daemon.run()