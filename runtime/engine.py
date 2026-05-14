import os
import sys
import json
import hashlib
import time
import uuid
import random
import sqlite3
import logging
from pathlib import Path
from core.ast.parser import parse_pdf

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ast.models import ASTNode, NodeType
from apps.llm_workers.gemini_client import GeminiClient
from apps.llm_workers.chunk_processor import ChunkProcessor
from apps.compiler.tex_builder import TexBuilder
from apps.compiler.docker_runner import DockerRunner
from core.utils.logger import setup_logger
from core.metrics.metrics import Metrics

from infra.db.chunk_task_repository import ChunkTaskRepository
from infra.db.repository import DocumentRepository
from infra.db.fsm_repository import FSMRepository
from core.execution.exceptions import PipelineIntegrityError, OptimisticLockError
from core.execution.state import (
    DocumentState, TERMINAL_STATES,
    StartParsingCommand, StartProcessingCommand, MarkAssemblyReadyCommand,
    StartAssemblyCommand, MarkCompilationReadyCommand, StartCompilationCommand,
    CompleteDocumentCommand, FailDocumentCommand
)
from core.execution.handlers import DocumentCommandHandler

setup_logger()
metrics = Metrics()
logger = logging.getLogger(__name__)

DB_PATH = "infra/db/document_engine.db"

def compute_ast_hash(ast: list[ASTNode]) -> str:
    def serialize_node(n: ASTNode) -> dict:
        return {
            "node_id": n.node_id,
            "type": str(n.type),
            "content": n.content,
            "latex": getattr(n, "latex", None),
            "children": [serialize_node(c) for c in getattr(n, "children", [])] if getattr(n, "children", None) else []
        }
        
    raw = json.dumps(
        [serialize_node(n) for n in ast], 
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _build_semantic_chunks(ast: list[ASTNode]) -> list[ASTNode]:
    macro_nodes = []
    current_content = []
    current_len = 0
    chunk_idx = 1
    boundaries = {NodeType.SECTION}

    for node in ast:
        content = node.content or ""
        if content is None:
            continue
            
        is_boundary = node.type in boundaries
        if is_boundary and current_len > 800:
            macro_nodes.append(ASTNode(node_id=f"macro_{chunk_idx}", type=NodeType.MACRO_CHUNK, content="\n\n".join(current_content)))
            chunk_idx += 1
            current_content = []
            current_len = 0
            
        current_content.append(content)
        current_len += len(content)
        
        if current_len > 4000:
            macro_nodes.append(ASTNode(node_id=f"macro_{chunk_idx}", type=NodeType.MACRO_CHUNK, content="\n\n".join(current_content)))
            chunk_idx += 1
            current_content = []
            current_len = 0
            
    if current_content:
        macro_nodes.append(ASTNode(node_id=f"macro_{chunk_idx}", type=NodeType.MACRO_CHUNK, content="\n\n".join(current_content)))
        
    logger.info("macro_chunks_built", extra={"extra_data": {"count": len(macro_nodes)}})
    return macro_nodes

def run_pipeline(pdf_input_path: str = "input.pdf", pdf_output_name: str = "MVP_traduccion.pdf") -> dict:
    pipeline_start = time.time()
    
    with open(pdf_input_path, "rb") as f:
        document_id = hashlib.sha256(f.read()).hexdigest()
        
    logger.info(f"Procesando Documento [ID: {document_id[:8]}]")
    
    raw_ast = parse_pdf(pdf_input_path)
    ast = _build_semantic_chunks(raw_ast)
    ast_hash = compute_ast_hash(ast)
    
    # Bootstrap de Infraestructura FSM
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db_conn = sqlite3.connect(DB_PATH, timeout=30) # timeout=30 es equivalente a busy_timeout=30000
    db_conn.execute("PRAGMA journal_mode=WAL")
    db_conn.execute("PRAGMA synchronous=NORMAL")
    db_conn.execute("PRAGMA busy_timeout=30000") # SOTA: Fencing explícito contra SQLITE_BUSY
    
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "infra", "db", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        db_conn.executescript(f.read())
        
    # Repositorios
    repo = DocumentRepository(db_conn)
    fsm_repo = FSMRepository(db_conn)
    task_repo = ChunkTaskRepository(db_conn) # Nuevo
    cmd_handler = DocumentCommandHandler(fsm_repo)
    
    client = GeminiClient()
    processor = ChunkProcessor(client, metrics, DB_PATH)

    owner_id = f"orchestrator_{uuid.uuid4().hex[:8]}"
    fsm_repo.initialize_document(document_id, ast_hash)

    retry_attempt = 0 
    output_path_obj = Path(pdf_output_name)
    tex_path = str(output_path_obj.parent / f"debug_{output_path_obj.stem}.tex")

    current_state = None # SOTA: Pre-asignación para evitar UnboundLocalError en crash prematuro

    # --- SOTA: BUCLE DE ORQUESTACIÓN DETERMINISTA (DURABLE RUNTIME) ---
    while True:
        try:
            # 1. Extracción de Proyección FSM
            doc_status = fsm_repo.get_status(document_id, ast_hash)
            if not doc_status:
                logger.critical("Documento perdido en la capa FSM.")
                break
                
            current_state = DocumentState(doc_status["state"])
            current_version = doc_status["version"]
            
            if current_state in TERMINAL_STATES:
                logger.info("PIPELINE_TERMINATED", extra={"extra_data": {"final_state": current_state.value}})
                break

            # 2. Gestión Transaccional de Leases
            now = time.time()
            lease_owner = doc_status.get("lease_owner")
            lease_expires = doc_status.get("lease_expires_at") or 0
            
            if lease_owner != owner_id or now > lease_expires:
                current_version = fsm_repo.acquire_lease(document_id, ast_hash, owner_id, ttl_sec=600)
            else:
                fsm_repo.renew_lease(document_id, ast_hash, owner_id, ttl_sec=600)

            # 3. State-Driven Execution (Sin Estado en RAM)
            if current_state == DocumentState.CREATED:
                cmd = StartParsingCommand(document_id, ast_hash, owner_id, current_version)
                cmd_handler.handle(cmd)
                retry_attempt = 0
                
            elif current_state == DocumentState.PARSING:
                cmd = StartProcessingCommand(document_id, ast_hash, owner_id, current_version)
                cmd_handler.handle(cmd)
                retry_attempt = 0
                
            elif current_state == DocumentState.PROCESSING:
                ordered_node_ids = [n.node_id for n in ast]
                
                # 1. Encolado Idempotente (Solo inserta si no existen)
                task_repo.enqueue_tasks(document_id, ast_hash, ordered_node_ids)
                
                # SOTA: Optimización O(1) de Indexación en Memoria (Evita escaneo lineal O(N) por chunk)
                ast_index = {n.node_id: n for n in ast}
                
                # 2. SOTA: El Worker Loop Durable
                while True:
                    # Liveness Guarantee: El orquestador defiende la propiedad del documento global
                    fsm_repo.renew_lease(document_id, ast_hash, owner_id, ttl_sec=600)
                    
                    # Adquisición Atómica (Task Leasing)
                    task = task_repo.pick_task(owner_id, document_id, ast_hash)
                    if not task:
                        break # Cola drenada localmente. Salimos a validar integridad.
                        
                    task_id = task["task_id"]
                    node_id = task["node_id"]
                    
                    try:
                        # Extracción O(1) del payload inmutable
                        target_node = ast_index[node_id]
                        
                        # Side-Effect: Procesamiento e Inserción CQRS (Próximo refactor: Desacoplar I/O de DB)
                        processor.process_and_commit(target_node, document_id, ast_hash, 1, len(ast))
                        
                        # Fencing de Finalización (Libera el lease granular)
                        task_repo.complete_task(task_id, owner_id)
                        logger.debug("task_completed", extra={"extra_data": {"node_id": node_id[:8]}})
                        
                    except Exception as e:
                        logger.error("TASK_EXECUTION_FAILED", extra={"extra_data": {"node_id": node_id[:8], "error": str(e)[:250]}})
                        task_repo.fail_task(task_id, owner_id, str(e))
                
                # 3. Barrera de Integridad CQRS Estricta
                valid_chunks_data = repo.get_assemblable_chunks(document_id, ast_hash, ordered_node_ids)
                returned_ids = [n[0] for n in valid_chunks_data]
                set_expected = set(ordered_node_ids)
                set_returned = set(returned_ids)
                
                if len(returned_ids) != len(set_returned):
                    raise PipelineIntegrityError("CRÍTICO: El Query Model devolvió IDs duplicados.")
                
                unexpected = set_returned - set_expected
                if unexpected:
                    raise PipelineIntegrityError(f"CRÍTICO: Nodos fantasma inyectados: {list(unexpected)}")
                
                if set_expected == set_returned:
                    # Transición Segura
                    cmd = MarkAssemblyReadyCommand(document_id, ast_hash, owner_id, current_version)
                    cmd_handler.handle(cmd)
                    retry_attempt = 0
                else:
                    # Backoff Exponencial Activo (Esperando Workers Paralelos o Recovery)
                    sleep_sec = min(30.0, 2.0 * (1.5 ** retry_attempt)) + random.uniform(0.1, 1.0)
                    missing_count = len(set_expected - set_returned)
                    logger.info("assembly_barrier_waiting", extra={"extra_data": {"missing_chunks": missing_count, "sleep_sec": round(sleep_sec, 2)}})
                    time.sleep(sleep_sec)
                    retry_attempt += 1
                    
            elif current_state == DocumentState.READY_FOR_ASSEMBLY:
                cmd = StartAssemblyCommand(document_id, ast_hash, owner_id, current_version)
                cmd_handler.handle(cmd)
                retry_attempt = 0
                
            elif current_state == DocumentState.ASSEMBLING:
                # Recuperar del disco/CQRS. Nada en RAM global.
                ordered_node_ids = [n.node_id for n in ast]
                valid_chunks_data = repo.get_assemblable_chunks(document_id, ast_hash, ordered_node_ids)
                
                builder = TexBuilder()
                tex_document = builder.build(valid_chunks_data)
                
                Path(tex_path).parent.mkdir(parents=True, exist_ok=True)
                with open(tex_path, "w", encoding="utf-8") as f:
                    f.write(tex_document)
                
                # Destruimos tex_document de la RAM explícitamente
                del tex_document 
                    
                cmd = MarkCompilationReadyCommand(document_id, ast_hash, owner_id, current_version)
                cmd_handler.handle(cmd)
                retry_attempt = 0
                
            elif current_state == DocumentState.READY_FOR_COMPILATION:
                cmd = StartCompilationCommand(document_id, ast_hash, owner_id, current_version)
                cmd_handler.handle(cmd)
                retry_attempt = 0
                
            elif current_state == DocumentState.COMPILING:
                # SOTA: Ejecución Stateless. El compilador lee directo del disco.
                if not os.path.exists(tex_path):
                    raise PipelineIntegrityError(f"Artefacto intermedio perdido: {tex_path}")
                    
                runner = DockerRunner()
                
                # Leemos estrictamente para inyectar al runner (si el runner no acepta Path directo)
                # SOTA: Se asume que el runner internamente manejará los volúmenes Docker
                with open(tex_path, "r", encoding="utf-8") as f:
                    tex_payload = f.read()
                    
                t_comp_start = time.perf_counter()
                pdf_path = runner.compile(tex_payload, output_filename=pdf_output_name)
                metrics.observe("compile_sec", time.perf_counter() - t_comp_start)
                
                # SOTA: Observabilidad del artefacto físico final antes de la transición
                logger.info("artifact_compiled", extra={"extra_data": {"pdf_path": str(pdf_path)}})
                
                cmd = CompleteDocumentCommand(document_id, ast_hash, owner_id, current_version)
                cmd_handler.handle(cmd)
                retry_attempt = 0
                
        except OptimisticLockError as e:
            logger.warning(f"Lease perdido/expirado o lock conflict. Abortando orquestador local: {e}")
            break
            
        except Exception as e:
            # SOTA: Extracción segura del valor por si current_state sigue siendo None
            state_val = current_state.value if current_state else "UNKNOWN"
            logger.error("STATE_EXECUTION_FAILURE", extra={"extra_data": {"state": state_val, "error": str(e)[:250]}})
            try:
                doc_status = fsm_repo.get_status(document_id, ast_hash)
                # Si falla antes de tener versión, intentamos usar 0 o la de la DB
                safe_version = doc_status.get("version", 0) if doc_status else 0
                fail_cmd = FailDocumentCommand(document_id, ast_hash, owner_id, safe_version, reason=str(e)[:250])
                cmd_handler.handle(fail_cmd)
            except Exception as fsm_err:
                logger.critical(f"DOOMSDAY: No se pudo persistir FAILED. Lock Roto permanentemente. {fsm_err}")
            break

    try:
        fsm_repo.release_lease(document_id, ast_hash, owner_id)
    except Exception:
        pass
        
    db_conn.close()
    
    total_time = time.time() - pipeline_start
    final_state_val = current_state.value if current_state else "UNKNOWN"
    
    logger.info("pipeline_complete", extra={"extra_data": {
        "status": "success" if current_state == DocumentState.COMPLETED else "failed",
        "total_time_sec": round(total_time, 2)
    }})
    
    return {"status": "terminal_reached", "final_state": final_state_val}

if __name__ == "__main__":
    run_pipeline()