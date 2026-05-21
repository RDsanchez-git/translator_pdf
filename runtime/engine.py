import os
import sys
import json
import hashlib
import time
import uuid
import random
import logging
from pathlib import Path
from core.ast.parser import parse_pdf

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ast.models import ASTNode, NodeType
from apps.llm_workers.gemini_client import GeminiClient
from apps.llm_workers.chunk_processor import ChunkProcessor
from apps.compiler.tex_builder import TexBuilder
from apps.compiler.docker_runner import DockerRunner
from core.metrics.metrics import Metrics

from infra.db.fsm_repository import FSMRepository
from core.execution.exceptions import PipelineIntegrityError, OptimisticLockError
from core.execution.state import (
    DocumentState, TERMINAL_STATES,
    StartParsingCommand, StartProcessingCommand, MarkAssemblyReadyCommand,
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

if __name__ == "__main__":
    # 1. Configuración de telemetría (SOTA: siempre es lo primero)
    setup_distributed_logger()
    
    # 2. Inicialización de dependencias
    metrics = Metrics()


CONTROL_DB_PATH = "infra/db/control.db"
EVENT_DB_PATH = "infra/db/event.db"
MAT_DB_PATH = "infra/db/materialized.db"

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
    
   # Bootstrap de Infraestructura TPS (Triple Plane Split)
    ctrl_conn = get_connection(CONTROL_DB_PATH,timeout=30)
    evt_conn = get_connection(EVENT_DB_PATH,timeout=30)
    mat_conn = get_connection(MAT_DB_PATH,timeout=30)
    
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "infra", "db", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    for conn in (ctrl_conn, evt_conn, mat_conn):
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=30000")
        conn.executescript(schema_sql) # SOTA: Se aplican todas las tablas a las 3 DBs (overhead nulo)

    # Repositorios Especializados
    mat_repo = MaterializedPlaneRepository(mat_conn)
    event_repo = EventPlaneRepository(evt_conn) # Faltaba instanciar este
    fsm_repo = FSMRepository(ctrl_conn)
    task_repo = ControlPlaneRepository(ctrl_conn)
    cmd_handler = DocumentCommandHandler(fsm_repo)
    
    client = GeminiClient()
    
    # SOTA: Inyectamos los objetos que cumplen los Protocols, NO las rutas de texto
    processor = ChunkProcessor(client, metrics, task_repo, event_repo, mat_repo)
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
                task_repo.enqueue_tasks(document_id, ast_hash, ordered_node_ids)

                ast_index = {n.node_id: n for n in ast}
                
                # SOTA: Iniciar Heartbeat Asíncrono para proteger I/O largo (Gemini)
                stop_event = threading.Event()
                cancel_event = threading.Event()

                # SOTA: Pasamos explícitamente la ruta de la DB, no la conexión viva
                hb_thread = threading.Thread(
                    target=heartbeat_daemon,
                    args=(document_id, ast_hash, owner_id, stop_event, cancel_event, CONTROL_DB_PATH),
                    daemon=True
                )
                hb_thread.start()
                
                try:
                    # 2. SOTA: El Worker Loop Durable
                    while True:
                        # Fencing check cooperativo
                        if cancel_event.is_set():
                            raise LeaseExpiredError("Cancelación cooperativa disparada por pérdida de lease.")
                            
                        # Adquisición Atómica (Task Leasing)
                        task = task_repo.pick_task(owner_id, document_id, ast_hash)
                        if not task:
                            break # Cola drenada localmente.
                            
                        task_id = task.task_id
                        node_id = task.node_id

                        # ======================================================
                        # SOTA: BLOQUEO FORZADO PARA CHAOS TEST
                        # ======================================================
                        logger.warning(f"CHAOS TEST: Procesando {node_id}. Ejecuta 'docker compose kill worker-a' AHORA.")
                        time.sleep(15)
                        # ======================================================

                        t_exec = ctx_execution_id.set(task.execution_id)
                        t_work = ctx_worker_id.set(owner_id)
                        t_task = ctx_task_id.set(task_id)
                        t_node = ctx_node_id.set(node_id)
                        
                        try:
                            target_node = ast_index[node_id]
                            processor.process_and_commit(target_node, document_id, ast_hash, task, owner_id)
                            task_repo.acknowledge_execution(task_id, owner_id)
                            logger.info("Chunk procesado y materializado exitosamente.")
                            
                        except CircuitTripError as e:
                            logger.critical(f"CIRCUIT TRIPPED! {e} Liberando tarea intacta y durmiendo...")
                            task_repo.release_task_untouched(task_id, owner_id)
                            stop_event.wait(timeout=30.0) # SOTA: Sleep seguro para threads
                            
                        except CircuitOpenError as e:
                            logger.warning(f"Circuito bloqueado. Durmiendo {e.cooldown_remaining:.1f}s")
                            task_repo.release_task_untouched(task_id, owner_id)
                            stop_event.wait(timeout=min(e.cooldown_remaining, 30.0))

                        except Exception as e:
                            state_val = current_state.value if current_state else "UNKNOWN"
                            logger.error("STATE_EXECUTION_FAILURE", extra={"extra_data": {"state": state_val, "error": str(e)[:250]}})
                            
                            try:
                                # SOTA: Circuit Breaker contra Poison Documents
                                # Obtenemos y actualizamos el contador de reintentos atómicamente
                                cursor = ctrl_conn.execute(
                                    "UPDATE document_fsm SET retry_count = retry_count + 1 WHERE document_id = ? RETURNING retry_count", 
                                    (document_id,)
                                )
                                row = cursor.fetchone()
                                current_retries = row[0] if row else 1
                                
                                # SOTA: Threshold máximo de 3 intentos antes de abortar definitivamente
                                target_state = DocumentState.FAILED_FATAL if current_retries >= 3 else DocumentState.FAILED_RETRYABLE
                                
                                if current_retries >= 3:
                                    logger.critical(f"POISON_PILL DETECTADO: Doc {document_id} superó {current_retries} retries. Promoviendo a FAILED_FATAL.")

                                doc_status = fsm_repo.get_status(document_id, ast_hash)
                                safe_version = doc_status.get("version", 0) if doc_status else 0
                                
                                # Forzamos la transición a nivel repositorio para respetar el enrutamiento dinámico
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
                    # SOTA: Garantizar que el hilo muera al terminar la fase
                    stop_event.set()
                    hb_thread.join(timeout=2.0)
                
                # 3. Barrera de Integridad CQRS Estricta
                valid_chunks_data = mat_repo.get_assemblable_chunks(
                    document_id, ast_hash, ordered_node_ids, required_projection_v=1
                )
                # SOTA: Acceso a DTO por atributo
                returned_ids = [n.node_id for n in valid_chunks_data]
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
                # SOTA Telemetry: Sonda de estado del AST y Query Model
                logger.info(f"SRE: AST TYPE: {type(ast)}")
                logger.info(f"SRE: AST LEN (pre-list): {len(ast) if hasattr(ast, '__len__') else 'NO_LEN'}")
                
                # Coerción defensiva (Hardening)
                ast_list = list(ast)
                
                ordered_node_ids = [n.node_id for n in ast_list]
                logger.info(f"SRE: ordered_node_ids extraídos: {len(ordered_node_ids)}")
                
                # Query al Materialized View
                valid_chunks_data = mat_repo.get_assemblable_chunks(
                    document_id, ast_hash, ordered_node_ids, required_projection_v=1
                )
                
                # SOTA Telemetry: Veredicto del Query Model
                logger.info(f"SRE: CHUNKS RECUPERADOS DB: {len(valid_chunks_data)}")
                if len(valid_chunks_data) > 0:
                    logger.info(f"SRE: Muestra de ID recuperado: {valid_chunks_data[0].node_id}")
                else:
                    logger.error(f"CRÍTICO: mat_repo.get_assemblable_chunks devolvió 0. Params: doc={document_id}, hash={ast_hash}, len_ids={len(ordered_node_ids)}")
                
                builder = TexBuilder()
                legacy_chunks_format = [(p.node_id, p.normalized_response) for p in valid_chunks_data]
                tex_document = builder.build(legacy_chunks_format)
                
                logger.info(f"SRE: TEX LEN: {len(tex_document)}")
                logger.info("SRE: TEX PREVIEW:\n" + tex_document[:1500])

                Path(tex_path).parent.mkdir(parents=True, exist_ok=True)
                with open(tex_path, "w", encoding="utf-8") as f:
                    f.write(tex_document)
                
                # 2. Verifica DISCO
                with open(tex_path, "r", encoding="utf-8") as f:
                    disk_content = f.read()

                logger.info(f"SRE: TEX LEN DISK: {len(disk_content)}")
                logger.info("SRE: TEX DISK PREVIEW:\n" + disk_content[:1500])
                
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
            # SOTA: Coerción explícita de tipos. Apaga el linter y previene AttributeError.
            state_val = current_state.value if current_state is not None else "UNKNOWN"
            logger.error("STATE_EXECUTION_FAILURE", extra={"extra_data": {"state": state_val, "error": str(e)[:250]}})
            
            try:
                # SOTA: Portabilidad ANSI SQL sin RETURNING, usando lock explícito
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
                
                # SOTA: Inyectamos 'state_val' en lugar del peligroso 'current_state.value'
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
        "total_time_sec": round(total_time, 2)
    }})
    
    return {"status": "terminal_reached", "final_state": final_state_val}

if __name__ == "__main__":
    setup_distributed_logger()
    metrics = Metrics()
    run_pipeline()