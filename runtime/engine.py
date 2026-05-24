import os
import sys
import hashlib
import time
import uuid
import random
import logging
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from apps.llm_workers.gemini_client import GeminiClient
from apps.llm_workers.chunk_processor import ChunkProcessor
from apps.compiler.tex_builder import TexBuilder
from apps.compiler.docker_runner import DockerRunner
from core.metrics.metrics import Metrics

from infra.db.fsm_repository import FSMRepository
from core.execution.exceptions import PipelineIntegrityError, OptimisticLockError
from core.execution.state import (
    DocumentState, TERMINAL_STATES, MarkAssemblyReadyCommand,
    StartAssemblyCommand, MarkCompilationReadyCommand, StartCompilationCommand,
    CompleteDocumentCommand
)
from core.execution.handlers import DocumentCommandHandler
from infra.db.control_repo import ControlPlaneRepository
from infra.db.materialized_repo import MaterializedPlaneRepository
from infra.db.event_repo import EventPlaneRepository

from core.utils.telemetry import (
    setup_distributed_logger, 
    ctx_execution_id, ctx_worker_id, ctx_task_id, ctx_node_id
)

from core.execution.exceptions import CircuitTripError, CircuitOpenError

import threading
from core.execution.exceptions import LeaseExpiredError
from infra.db.connection import get_connection
from core.normalization.normalizer import TextNormalizer
from core.execution.ports import EventLifecycle
from core.ast.registry import ASTRegistry

def heartbeat_daemon(doc_id: str, ast_hash: str, owner_id: str, stop_event: threading.Event, cancel_event: threading.Event, db_path: str):
    """SOTA: Demonio de liveness con conexión SQLite 100% aislada (Thread-Safe)."""
    # 1. Instanciación exclusiva para este hilo
    # 1. Instanciación exclusiva para este hilo
    conn = get_connection(db_path, timeout=30)
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    
    daemon_repo = FSMRepository(conn)
    
    try:
        while not stop_event.wait(timeout=15.0):
            try:
                daemon_repo.renew_lease(doc_id, ast_hash, owner_id, ttl_sec=60)
            except LeaseExpiredError:
                logger.error(f"CRÍTICO: Lease expirado para {doc_id}. Fencing Cooperativo activado.")
                cancel_event.set()
                break
            except Exception as e:
                logger.warning(f"SRE: Fallo temporal en heartbeat: {e}")
    finally:
        # 2. Limpieza estricta de descriptores de archivo
        conn.close()


logger = logging.getLogger(__name__)

CONTROL_DB_PATH = "infra/db/control.db"
EVENT_DB_PATH = "infra/db/event.db"
MAT_DB_PATH = "infra/db/materialized.db"

# ... Todos tus imports originales, heartbeat_daemon y setup se mantienen EXACTAMENTE IGUAL ...

def run_pipeline(document_id: str, ast_hash: str, pdf_output_name: str = "MVP_traduccion.pdf") -> dict:
    pipeline_start = time.time()
    
    logger.info(f"Orquestador de Runtime acoplado al Documento [ID: {document_id[:8]}]")
    
    # Bootstrap de Infraestructura TPS (Triple Plane Split)
    ctrl_conn = get_connection(CONTROL_DB_PATH, timeout=30)
    evt_conn = get_connection(EVENT_DB_PATH, timeout=30)
    mat_conn = get_connection(MAT_DB_PATH, timeout=30)
    
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "infra", "db", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    for conn in (ctrl_conn, evt_conn, mat_conn):
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=30000")
        conn.executescript(schema_sql)

    # Repositorios Especializados
    mat_repo = MaterializedPlaneRepository(mat_conn)
    event_repo = EventPlaneRepository(evt_conn)
    fsm_repo = FSMRepository(ctrl_conn)
    task_repo = ControlPlaneRepository(ctrl_conn)
    cmd_handler = DocumentCommandHandler(fsm_repo, task_repo=task_repo)
    ast_registry = ASTRegistry()
    
    client = GeminiClient()
    processor = ChunkProcessor(client, metrics)
    owner_id = f"orchestrator_{uuid.uuid4().hex[:8]}"

    # SOTA: Lazy Loading del AST guardado por el OCR Router de forma atómica en disco
    cache_key = (document_id, ast_hash)
    if cache_key not in ast_registry._cache:
        ast_registry._load_document(document_id, ast_hash)
        
    doc_nodes = ast_registry._cache.get(cache_key, {})
    if not doc_nodes:
        raise PipelineIntegrityError(f"Error crítico: El AST cacheado por el OCR Router no existe en disco para {document_id[:8]}")

    # Reconstrucción del mapa lineal de Chunks usando el caché de disco cargado
    ordered_node_ids = list(doc_nodes.keys())

    retry_attempt = 0 
    output_path_obj = Path(pdf_output_name)
    tex_path = str(output_path_obj.parent / f"debug_{output_path_obj.stem}.tex")

    current_state = None

    # --- SOTA: BUCLE DE ORQUESTACIÓN DETERMINISTA (MANTENIDO) ---
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

            # 3. State-Driven Execution (Removidos CREATED y PARSING. El Router inicia en PROCESSING)
            if current_state == DocumentState.PROCESSING:

                ast_index = doc_nodes
                
                # SOTA: Iniciar Heartbeat Asíncrono para proteger I/O largo (Gemini)
                stop_event = threading.Event()
                cancel_event = threading.Event()

                hb_thread = threading.Thread(
                    target=heartbeat_daemon,
                    args=(document_id, ast_hash, owner_id, stop_event, cancel_event, CONTROL_DB_PATH),
                    daemon=True
                )
                hb_thread.start()
                
                try:
                    # 2. SOTA: El Worker Loop Durable Integrado
                    while True:
                        if cancel_event.is_set():
                            raise LeaseExpiredError("Cancelación cooperativa disparada por pérdida de lease.")
                            
                        task = task_repo.pick_task(owner_id, document_id, ast_hash)
                        if not task:
                            break # Cola drenada localmente.
                            
                        task_id = task.task_id
                        node_id = task.node_id

                        if os.getenv("ENABLE_CHAOS_TEST") == "1":
                            logger.warning(f"CHAOS TEST: Procesando {node_id}")
                            time.sleep(15)

                        t_exec = ctx_execution_id.set(task.execution_id)
                        t_work = ctx_worker_id.set(owner_id)
                        t_task = ctx_task_id.set(task_id)
                        t_node = ctx_node_id.set(node_id)
                        
                        try:
                            target_node = ast_index[node_id]
                            
                            raw_response = processor.execute(target_node)
                            
                            event_repo.append_wal(
                                task.execution_id, document_id, node_id, 
                                hashlib.sha256(target_node.content.encode('utf-8')).hexdigest(), 
                                raw_response, processor.prompt_v, processor.model_v, 
                                processor.projection_v, EventLifecycle.GENERATED
                            )
                            
                            normalized = TextNormalizer.normalize(raw_response) if getattr(target_node, 'type', None) != 'EQUATION' else raw_response
                            normalized_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
                            
                            mat_repo.upsert_projection(
                                document_id, ast_hash, node_id, 
                                hashlib.sha256(target_node.content.encode('utf-8')).hexdigest(), 
                                normalized, normalized_hash, processor.projection_v
                            )
                            
                            task_repo.acknowledge_execution(task_id, owner_id)
                            logger.info("Chunk procesado, registrado en WAL y materializado exitosamente.")
                            
                        except CircuitTripError as e:
                            logger.critical(f"CIRCUIT TRIPPED! {e} Liberando tarea intacta y durmiendo...")
                            task_repo.release_task_untouched(task_id, owner_id)
                            stop_event.wait(timeout=30.0)
                            
                        except CircuitOpenError as e:
                            logger.warning(f"Circuito bloqueado. Durmiendo {e.cooldown_remaining:.1f}s")
                            task_repo.release_task_untouched(task_id, owner_id)
                            stop_event.wait(timeout=min(e.cooldown_remaining, 30.0))

                        except Exception as e:
                            state_val = current_state.value if current_state else "UNKNOWN"
                            logger.error("STATE_EXECUTION_FAILURE", extra={"extra_data": {"state": state_val, "error": str(e)[:250]}})
                            
                            try:
                                ctrl_conn.execute("BEGIN IMMEDIATE")
                                try:
                                    ctrl_conn.execute("UPDATE document_fsm SET retry_count = retry_count + 1 WHERE document_id = ?", (document_id,))
                                    cursor = ctrl_conn.execute("SELECT retry_count FROM document_fsm WHERE document_id = ?", (document_id,))
                                    row = cursor.fetchone()
                                    ctrl_conn.execute("COMMIT")
                                except Exception as inner_db_err:
                                    ctrl_conn.execute("ROLLBACK")
                                    raise inner_db_err
                                
                                current_retries = row[0] if row else 1
                                target_state = DocumentState.FAILED_FATAL if current_retries >= 3 else DocumentState.FAILED_RETRYABLE
                                
                                if current_retries >= 3:
                                    logger.critical(f"POISON_PILL DETECTADO: Doc {document_id} superó {current_retries} retries. Promoviendo a FAILED_FATAL.")

                                doc_status = fsm_repo.get_status(document_id, ast_hash)
                                safe_version = doc_status.get("version", 0) if doc_status else 0
                                
                                fsm_repo.transition_to(
                                    document_id, ast_hash, current_state.value, target_state.value,
                                    safe_version, owner_id, is_terminal=(target_state == DocumentState.FAILED_FATAL), failure_reason=str(e)[:250]
                                )
                            except Exception as fsm_err:
                                logger.critical(f"DOOMSDAY: Falla catastrófica persistiendo FAILED_*. {fsm_err}")
                            break 

                        finally:
                            ctx_execution_id.reset(t_exec)
                            ctx_worker_id.reset(t_work)
                            ctx_task_id.reset(t_task)
                            ctx_node_id.reset(t_node)
                finally:
                    stop_event.set()
                    hb_thread.join(timeout=2.0)
                
                # 3. Barrera de Integridad CQRS Estricta
                valid_chunks_data = mat_repo.get_assemblable_chunks(
                    document_id, ast_hash, ordered_node_ids, required_projection_v=1
                )
                returned_ids = [n.node_id for n in valid_chunks_data]
                set_expected = set(ordered_node_ids)
                set_returned = set(returned_ids)
                
                if len(returned_ids) != len(set_returned):
                    raise PipelineIntegrityError("CRÍTICO: El Query Model devolvió IDs duplicados.")
                
                unexpected = set_returned - set_expected
                if unexpected:
                    raise PipelineIntegrityError(f"CRÍTICO: Nodos fantasma inyectados: {list(unexpected)}")
                
                if set_expected == set_returned:
                    cmd = MarkAssemblyReadyCommand(document_id, ast_hash, owner_id, current_version)
                    cmd_handler.handle(cmd)
                    retry_attempt = 0
                else:
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
                # Se mantiene tu lógica original de lectura desde doc_nodes y compilación en memoria
                valid_chunks_data = mat_repo.get_assemblable_chunks(
                    document_id, ast_hash, ordered_node_ids, required_projection_v=1
                )
                
                builder = TexBuilder()
                legacy_chunks_format = [(p.node_id, p.normalized_response) for p in valid_chunks_data]
                tex_document = builder.build(legacy_chunks_format)
                
                Path(tex_path).parent.mkdir(parents=True, exist_ok=True)
                with open(tex_path, "w", encoding="utf-8") as f:
                    f.write(tex_document)
                    
                cmd = MarkCompilationReadyCommand(document_id, ast_hash, owner_id, current_version)
                cmd_handler.handle(cmd)
                retry_attempt = 0
                
            elif current_state == DocumentState.READY_FOR_COMPILATION:
                cmd = StartCompilationCommand(document_id, ast_hash, owner_id, current_version)
                cmd_handler.handle(cmd)
                retry_attempt = 0
                
            elif current_state == DocumentState.COMPILING:
                if not os.path.exists(tex_path):
                    raise PipelineIntegrityError(f"Artefacto intermedio perdido: {tex_path}")
                    
                runner = DockerRunner()
                with open(tex_path, "r", encoding="utf-8") as f:
                    tex_payload = f.read()
                    
                t_comp_start = time.perf_counter()
                pdf_path = runner.compile(tex_payload, output_filename=pdf_output_name)
                metrics.observe("compile_sec", time.perf_counter() - t_comp_start)
                
                logger.info("artifact_compiled", extra={"extra_data": {"pdf_path": str(pdf_path)}})
                
                cmd = CompleteDocumentCommand(document_id, ast_hash, owner_id, current_version)
                cmd_handler.handle(cmd)
                retry_attempt = 0
                
        except OptimisticLockError as e:
            logger.warning(f"Lease perdido/expirado o lock conflict. Abortando orquestador local: {e}")
            break
            
        except Exception as e:
            state_val = current_state.value if current_state is not None else "UNKNOWN"
            logger.error("STATE_EXECUTION_FAILURE", extra={"extra_data": {"state": state_val, "error": str(e)[:250]}})
            
            try:
                ctrl_conn.execute("BEGIN IMMEDIATE")
                try:
                    ctrl_conn.execute("UPDATE document_fsm SET retry_count = retry_count + 1 WHERE document_id = ?", (document_id,))
                    cursor = ctrl_conn.execute("SELECT retry_count FROM document_fsm WHERE document_id = ?", (document_id,))
                    row = cursor.fetchone()
                    ctrl_conn.execute("COMMIT")
                except Exception as inner_db_err:
                    ctrl_conn.execute("ROLLBACK")
                    raise inner_db_err
                
                current_retries = row[0] if row else 1
                target_state = DocumentState.FAILED_FATAL if current_retries >= 3 else DocumentState.FAILED_RETRYABLE
                
                # SOTA: Recuperar la última versión válida de forma segura antes de transicionar
                doc_status = fsm_repo.get_status(document_id, ast_hash)
                safe_version = doc_status.get("version", 0) if doc_status else 0
                
                fsm_repo.transition_to(
                    document_id, ast_hash, state_val, target_state.value,
                    safe_version, owner_id, is_terminal=(target_state == DocumentState.FAILED_FATAL), failure_reason=str(e)[:250]
                )
            except Exception as fsm_err:
                logger.critical(f"DOOMSDAY: Falla catastrófica persistiendo FAILED_*. {fsm_err}")
            break

    try:
        fsm_repo.release_lease(document_id, ast_hash, owner_id)
    except Exception:
        pass
        
    ctrl_conn.close()
    evt_conn.close()
    mat_conn.close()
    
    total_time = time.time() - pipeline_start
    final_state_val = current_state.value if current_state else "UNKNOWN"
    
    logger.info("pipeline_complete", extra={"extra_data": {
        "status": "success" if current_state == DocumentState.COMPLETED else "failed",
        "total_time_sec": round(total_time, 2)  # SOTA: Se lee la variable, eliminando Ruff F841
    }})
    
    return {"status": "terminal_reached", "final_state": final_state_val}

if __name__ == "__main__":
    import random
    setup_distributed_logger()
    metrics = Metrics()
    
    NODE_ID = os.getenv("NODE_ID", f"orchestrator_daemon_{uuid.uuid4().hex[:8]}")
    logger.info(f"SOTA: Runtime Orchestrator Daemon inicializado [{NODE_ID}].")
    
    base_sleep = 2.0
    max_sleep = 10.0
    consecutive_idle = 0
    
    while True:
        ctrl_conn = None
        try:
            ctrl_conn = get_connection(CONTROL_DB_PATH, timeout=30)
            task_repo = ControlPlaneRepository(ctrl_conn)
            
            candidates = task_repo.find_documents_with_pending_chunks(sample_size=10)
            ctrl_conn.close()
            
            if not candidates:
                consecutive_idle += 1
                sleep_time = min(base_sleep * (1.3 ** consecutive_idle), max_sleep)
                time.sleep(sleep_time + random.uniform(0.0, 1.0))
                continue
                
            consecutive_idle = 0
            
            selected_doc_id, selected_ast_hash = random.choice(candidates)
            logger.info(f"Contexto seleccionado probabilísticamente: Doc {selected_doc_id[:8]} -> Lanzando Runtime.")
            
            try:
                run_pipeline(document_id=selected_doc_id, ast_hash=selected_ast_hash)
            except OptimisticLockError:
                logger.warning(f"Fencing Activo: Documento {selected_doc_id[:8]} ya posee un lease válido. Buscando nuevo contexto.")
                continue
                
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as err:
            logger.error(f"Fallo crítico en el bucle principal del Runtime Orchestrator Daemon: {err}")
            if ctrl_conn:
                try:
                    ctrl_conn.close()
                except Exception:
                    pass
            time.sleep(max_sleep)