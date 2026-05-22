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

from core.ast.parser import parse_pdf
from core.ast.hashing import compute_ast_hash, build_semantic_chunks

setup_distributed_logger()
logger = logging.getLogger("ocr_router")

class OCRRouterDaemon:
    """
    SOTA Pragmática: Ingestion Gateway con tolerancia a fallos.
    Vigila el Inbox físico, procesa PyTorch/Marker, gestiona la idempotencia del FSM
    y genera telemetría de cuarentena ante PDFs corruptos.
    """
    def __init__(self, fsm_repo: FSMRepository, task_repo: ControlPlaneRepository, 
                 cmd_handler: DocumentCommandHandler, ast_registry: ASTRegistry, 
                 workspace_dir: str = "."):
        self.fsm = fsm_repo
        self.task_repo = task_repo
        self.cmd_handler = cmd_handler
        self.ast_registry = ast_registry
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
        
        try:
            # 1. Pipeline de Inferencia Puro
            raw_ast = parse_pdf(str(pdf_path))
            ast = build_semantic_chunks(raw_ast)
            ast_hash = compute_ast_hash(ast)
            ordered_node_ids = [n.node_id for n in ast]
            
            # 2. Persistencia del AST
            self.ast_registry.register_ast(document_id, ast_hash, ast)
            
            # 3. Control de Idempotencia de Reingesta (Problema 2)
            self.fsm.initialize_document(document_id, ast_hash)
            status = self.fsm.get_status(document_id, ast_hash)
            
            if status and status.get("state") == DocumentState.PROCESSING.value:
                logger.warning(f"Documento {document_id[:8]} ya se encuentra en procesamiento activo. Saltando transiciones.")
                shutil.move(str(pdf_path), str(self.archive_dir / f"DUP_{document_id[:8]}_{pdf_path.name}"))
                return

            # 4. Coreografía CQRS con Transiciones Legales (Problema 1 resuelto por diseño nativo)
            current_version = self.fsm.acquire_lease(document_id, ast_hash, self.owner_id, ttl_sec=300)
            
            cmd_parse = StartParsingCommand(document_id, ast_hash, self.owner_id, current_version)
            current_version = self.cmd_handler.handle(cmd_parse)
            
            self.task_repo.enqueue_tasks(document_id, ast_hash, ordered_node_ids)
            
            cmd_process = StartProcessingCommand(document_id, ast_hash, self.owner_id, current_version)
            self.cmd_handler.handle(cmd_process)
            
            self.fsm.release_lease(document_id, ast_hash, self.owner_id)
            
            # 5. Archivo Histórico
            shutil.move(str(pdf_path), str(self.archive_dir / f"{document_id[:8]}_{pdf_path.name}"))
            
            latency = time.perf_counter() - start_time
            logger.info("Documento enrutado exitosamente a PROCESSING.", 
                        extra={"extra_data": {"chunks": len(ordered_node_ids), "latency_sec": round(latency, 1)}})
            
        except Exception as e:
            error_token = uuid.uuid4().hex[:6]
            logger.error(f"Fallo en la ingesta del documento [{error_token}] {pdf_path.name}: {e}")
            
            # SOTA: Guardia lógica con aserción explícita para el linter (Pylance Safe)
            if document_id is not None and ast_hash is not None:
                assert isinstance(document_id, str)
                assert isinstance(ast_hash, str)
                try:
                    self.fsm.release_lease(document_id, ast_hash, self.owner_id)
                except Exception:
                    pass
                
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
    CONTROL_DB_PATH = os.getenv("CONTROL_DB_PATH", "infra/db/control.db")
    ctrl_conn = get_connection(CONTROL_DB_PATH)
    
    fsm_repo = FSMRepository(ctrl_conn)
    task_repo = ControlPlaneRepository(ctrl_conn)
    cmd_handler = DocumentCommandHandler(fsm_repo, task_repo=task_repo)
    ast_registry = ASTRegistry()
    
    daemon = OCRRouterDaemon(fsm_repo, task_repo, cmd_handler, ast_registry)
    daemon.run()