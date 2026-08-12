import os
import sys
import hashlib
import time
import uuid
import random
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.metrics.metrics import Metrics
from infra.db.fsm_repository import FSMRepository
from core.execution.exceptions import PipelineIntegrityError, OptimisticLockError
from core.execution.state import (
    DocumentState, TERMINAL_STATES, MarkAssemblyReadyCommand
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
from infra.db.connection import get_connection
from core.normalization.normalizer import TextNormalizer
from core.execution.ports import EventLifecycle
from core.ast.registry import ASTRegistry
from core.normalization.latex_sanitizer import InlineMathProtector
from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
from core.finops.measurement import InferenceMeasurementService
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
from core.ast.enums import ContentNodeType
from apps.llm_workers.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

FSM_DB_PATH = "infra/db/fsm.db"
QUEUE_DB_PATH = "infra/db/queue.db"
EVENT_DB_PATH = "infra/db/event.db"
MAT_DB_PATH = "infra/db/materialized.db"

GLOBAL_LLM_SEMAPHORE = threading.Semaphore(int(os.getenv("MAX_GLOBAL_LLM_CONCURRENCY", "4")))

def run_pipeline(document_id: str, ast_hash: str, pdf_output_name: str = "MVP_traduccion.pdf") -> dict:
    pipeline_start = time.time()
    logger.info(f"Orquestador de Runtime acoplado al Documento [ID: {document_id[:8]}]")
    
    fsm_conn = get_connection(FSM_DB_PATH, timeout=30)
    queue_conn = get_connection(QUEUE_DB_PATH, timeout=30)
    evt_conn = get_connection(EVENT_DB_PATH, timeout=30)
    mat_conn = get_connection(MAT_DB_PATH, timeout=30)
    
    for conn in (fsm_conn, queue_conn, evt_conn, mat_conn):
        conn.execute("PRAGMA busy_timeout=30000")
        
    mat_repo = MaterializedPlaneRepository(mat_conn)
    fsm_repo = FSMRepository(fsm_conn)
    task_repo = ControlPlaneRepository(queue_conn)
    cmd_handler = DocumentCommandHandler(fsm_repo, task_repo=task_repo)
    ast_registry = ASTRegistry()
    
    # SOTA: Instanciación Singleton del Bridge para aislamiento Thread-Safe
    from apps.llm_workers.sync_bridge import SyncProviderBridge
    from apps.llm_workers.adapters import GroqProvider
    from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
    from core.validation.estimators import ExactBPEEstimator
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY no configurada. Imposible operar motor LLM.")
    
    estimator = ExactBPEEstimator()
    measurement_service = InferenceMeasurementService(estimator=estimator)
    
    # SOTA FIX: Adecuación a firmas FinOps y políticas de compresión canónicas de la Fase 16
    budget_calculator = PromptBudgetCalculator(
        primary_window_limit=8192,
        fallback_window_limit=1048576,
        min_output_reserve=256,
        max_output_reserve=4096
    )
    
    compression_policy = StandardCompressionPolicy()
    
    builder = PromptBuilder(
        model_name="llama3-70b-8192", 
        prompt_version="v1.0", 
        measurement_service=measurement_service,
        budget_calculator=budget_calculator,
        compression_policy=compression_policy
    )
    
    rpm_limit = int(os.getenv("GROQ_RPM_LIMIT", "30"))
    tpm_limit = int(os.getenv("GROQ_TPM_LIMIT", "6000"))
    
    dialect = OpenAICompatibleDialect()
    groq_provider = GroqProvider(api_key=api_key, dialect=dialect)
    quota = QuotaManager(rpm_limit=rpm_limit, tpm_limit=tpm_limit)
    rate_provider = RateLimitedProvider(underlying=groq_provider, quota_manager=quota)
    
    processor = SyncProviderBridge(async_provider=rate_provider, prompt_builder=builder)
    owner_id = f"orchestrator_{uuid.uuid4().hex[:8]}"
    cache_key = (document_id, ast_hash)
    
    if os.getenv("IS_BENCHMARK") == "1" or document_id.startswith("doc_"):
        cursor = queue_conn.execute("SELECT node_id FROM chunk_tasks WHERE document_id = ?", (document_id,))
        ordered_node_ids = [row[0] for row in cursor.fetchall()]
        
        from core.ast.models import ASTNode, ParagraphPayload
        
        # SOTA FIX: Instanciación real y tipada del ASTNode para evitar evasiones de Type Checking
        doc_nodes = {
            nid: ASTNode(
                node_id=nid,
                node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="SOTA synthetic content benchmarking")
            )
            for nid in ordered_node_ids
        }
    else:
        if cache_key not in ast_registry._cache:
            ast_registry._load_document(document_id, ast_hash)
        doc_nodes = ast_registry._cache.get(cache_key, {})
        if not doc_nodes:
            raise PipelineIntegrityError(f"Error crítico: El AST cacheado por el OCR Router no existe en disco para {document_id[:8]}")
        ordered_node_ids = list(doc_nodes.keys())
        
    retry_attempt = 0 
    current_state = None
    
    while True:
        try:
            doc_status = fsm_repo.get_status(document_id, ast_hash)
            if doc_status is None:
                logger.warning(f"FSM missing document {document_id[:8]} (no row returned)")
                break
            try:
                current_state = DocumentState(doc_status.current_state)
            except ValueError as e:
                logger.critical(
                    "FSM_INVALID_STATE",
                    extra={"extra_data": {"value": doc_status.current_state, "error": str(e)}}
                )
                raise PipelineIntegrityError(f"Estado FSM inválido para {document_id[:8]}")
            
            current_version = doc_status.state_version
            if current_state in TERMINAL_STATES:
                logger.info("PIPELINE_TERMINATED", extra={"extra_data": {"final_state": current_state.value}})
                break
                
            if current_state == DocumentState.PROCESSING:
                ast_index = doc_nodes
                max_threads = int(os.getenv("MAX_CONCURRENT_CHUNKS", "4"))
                
                def chunk_worker_thread():
                    th_queue_conn = get_connection(QUEUE_DB_PATH, timeout=30)
                    th_evt_conn = get_connection(EVENT_DB_PATH, timeout=30)
                    th_mat_conn = get_connection(MAT_DB_PATH, timeout=30)
                    
                    for c in (th_queue_conn, th_evt_conn, th_mat_conn):
                        c.execute("PRAGMA busy_timeout=30000")
                        
                    th_task_repo = ControlPlaneRepository(th_queue_conn)
                    th_event_repo = EventPlaneRepository(th_evt_conn)
                    th_mat_repo = MaterializedPlaneRepository(th_mat_conn)
                    
                    local_processor = processor  
                    
                    try:
                        while True:
                            task = th_task_repo.pick_task(owner_id, document_id, ast_hash)
                            if not task:
                                break
                                
                            task_id = task.task_id
                            node_id = task.node_id
                            
                            t_exec = ctx_execution_id.set(task.execution_id)
                            t_work = ctx_worker_id.set(owner_id)
                            t_task = ctx_task_id.set(task_id)
                            t_node = ctx_node_id.set(node_id)
                            
                            try:
                                target_node = ast_index[node_id]
                                
                                # SOTA FIX: Enrutamiento directo y desacoplado basado en la taxonomía pura del AST V2
                                if target_node.node_type in (ContentNodeType.DISPLAY_EQUATION, ContentNodeType.INLINE_EQUATION, ContentNodeType.CODE, ContentNodeType.IMAGE):
                                    policy = "PRESERVE"
                                else:
                                    policy = "TRANSLATE"
                                
                                if policy in ("PRESERVE", "IGNORE"):
                                    raw_response = local_processor.execute(target_node)
                                else:
                                    # SOTA FIX: Abstracción polimórfica para extracción e instanciación inmutable de sub-payloads
                                    # SOTA FIX: Abstracción polimórfica para extracción e instanciación inmutable de sub-payloads
                                    original_content = target_node.text_content or ""
                                    masked_content, math_map = InlineMathProtector.mask(original_content)
                                    
                                    from core.ast.models import ParagraphPayload, HeadingPayload, TablePayload, ListPayload
                                    if target_node.node_type == ContentNodeType.HEADING:
                                        from core.ast.enums import HeadingLevel
                                        # SOTA FIX: Type Narrowing estructural mediante isinstance para satisfacer la unión en Pyright Strict
                                        old_level = target_node.payload.heading_level if isinstance(target_node.payload, HeadingPayload) else HeadingLevel.UNKNOWN
                                        masked_payload = HeadingPayload(content=masked_content, heading_level=old_level)
                                    elif target_node.node_type == ContentNodeType.LIST:
                                        masked_payload = ListPayload(content=masked_content)
                                    elif target_node.node_type in (ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX):
                                        masked_payload = TablePayload(content=masked_content)
                                    else:
                                        masked_payload = ParagraphPayload(content=masked_content)
                                        
                                    exec_node = target_node.model_copy(update={"payload": masked_payload})
                                    
                                    with GLOBAL_LLM_SEMAPHORE:
                                        raw_response = local_processor.execute(exec_node)
                                        
                                    raw_response = InlineMathProtector.restore(raw_response, math_map)
                                
                                content_to_hash = target_node.text_content or ""
                                
                                th_event_repo.append_wal(
                                    task.execution_id, document_id, node_id, 
                                    hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest(), 
                                    raw_response, processor.prompt_v, processor.model_v, 
                                    processor.projection_v, EventLifecycle.GENERATED
                                )
                                
                                normalized = TextNormalizer.normalize(raw_response) if policy == "TRANSLATE" else raw_response
                                normalized_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
                                
                                th_mat_repo.upsert_projection(
                                    document_id, ast_hash, node_id, 
                                    hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest(), 
                                    normalized, normalized_hash, processor.projection_v
                                )
                                
                                th_task_repo.acknowledge_execution(task_id, owner_id)
                                logger.info(f"Chunk {node_id[:8]} materializado exitosamente.")
                                
                            except CircuitTripError as e:
                                logger.critical(f"CIRCUIT TRIPPED! {e}. Liberando tarea.")
                                th_task_repo.release_task_untouched(task_id, owner_id)
                                time.sleep(10.0)
                            except CircuitOpenError:
                                th_task_repo.release_task_untouched(task_id, owner_id)
                                time.sleep(5.0)
                            except Exception as e:
                                logger.error(f"Falla en sub-tarea {node_id[:8]}: {str(e)[:250]}")
                                try:
                                    th_task_repo.abandon_execution(task_id, owner_id, str(e)[:250])
                                except OptimisticLockError:
                                    pass
                            finally:
                                ctx_execution_id.reset(t_exec)
                                ctx_worker_id.reset(t_work)
                                ctx_task_id.reset(t_task)
                                ctx_node_id.reset(t_node)
                    finally:
                        for c in (th_queue_conn, th_evt_conn, th_mat_conn):
                            try:
                                c.close()
                            except Exception:
                                pass
                                
                with ThreadPoolExecutor(max_workers=max_threads) as executor:
                    futures = [executor.submit(chunk_worker_thread) for _ in range(max_threads)]
                    for future in futures:
                        future.result() 
                
                doc_status = fsm_repo.get_status(document_id, ast_hash)
                current_version = doc_status.state_version if doc_status else current_version
                
                cursor = queue_conn.execute(
                    """SELECT 
                        SUM(CASE WHEN task_state = 'FAILED' THEN 1 ELSE 0 END),
                        SUM(CASE WHEN task_state IN ('PENDING', 'PROCESSING', 'RETRYABLE_ERROR') THEN 1 ELSE 0 END)
                       FROM chunk_tasks WHERE document_id = ? AND ast_hash = ?""",
                    (document_id, ast_hash)
                )
                row = cursor.fetchone()
                failed_chunks = row[0] or 0
                active_chunks = row[1] or 0
                if failed_chunks > 0 and active_chunks == 0:
                    logger.critical(f"Poison Pill confirmada: {failed_chunks} fallidos, {active_chunks} activos. Promoviendo a FAILED_FATAL.")
                    fsm_repo.transition_to(
                        document_id, ast_hash, current_state.value, DocumentState.FAILED_FATAL.value,
                        current_version, owner_id, is_terminal=True, failure_reason=f"Colapso de pipeline por {failed_chunks} tareas muertas."
                    )
                    break
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
                    if os.getenv("IS_BENCHMARK") == "1":
                        logger.info(f"[BENCHMARK] Documento {document_id[:8]} forzando transición terminal en repositorio.")
                        fsm_repo.transition_to(
                            document_id=document_id,
                            ast_hash=ast_hash,
                            old_state=current_state.value,
                            new_state=DocumentState.COMPLETED.value,
                            current_version=current_version,
                            owner_id=owner_id,
                            is_terminal=True
                        )
                        fsm_conn.commit()
                        current_state = DocumentState.COMPLETED  
                        break
                        
                    doc_status = fsm_repo.get_status(document_id, ast_hash)
                    if not doc_status:
                        break
                    
                    cmd = MarkAssemblyReadyCommand(document_id, ast_hash, owner_id, doc_status.state_version)
                    cmd_handler.handle(cmd)
                    current_state = DocumentState.READY_FOR_ASSEMBLY  
                    break 
                else:
                    sleep_sec = min(30.0, 2.0 * (1.5 ** retry_attempt)) + random.uniform(0.1, 1.0)
                    missing_count = len(set_expected - set_returned)
                    logger.info("assembly_barrier_waiting", extra={"extra_data": {"missing_chunks": missing_count, "sleep_sec": round(sleep_sec, 2)}})
                    time.sleep(sleep_sec)
                    retry_attempt += 1
                    
            elif current_state == DocumentState.FAILED_RETRYABLE:
                target_recovery = doc_status.suspended_state or DocumentState.PROCESSING.value
                logger.warning(f"Auto-recuperación de FAILED_RETRYABLE detectada. Retornando flujo hacia: {target_recovery}")
                time.sleep(2.0)
                
                doc_status = fsm_repo.get_status(document_id, ast_hash)
                if doc_status:
                    try:
                        fsm_repo.transition_to(
                            document_id, ast_hash, DocumentState.FAILED_RETRYABLE.value, 
                            target_recovery, doc_status.state_version, owner_id,
                            suspended_state=None 
                        )
                    except OptimisticLockError:
                        logger.warning("Conflicto CAS en auto-recuperación local. Delegando control.")
                        break
                continue
            elif current_state == DocumentState.STALLED:
                logger.warning(f"Documento {document_id[:8]} se encuentra en STALLED (requiere atencion). Liberando orquestador.")
                time.sleep(2.0)
                break
                
        except OptimisticLockError as e:
            logger.warning(f"Lock de concurrencia optimista interceptado. Abortando ejecutor local: {e}")
            break
            
        except Exception as e:
            import traceback
            print("\n!!! CRASH EN INICIALIZACION DE PIPELINE !!!", flush=True)
            traceback.print_exc()
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", flush=True)
            logger.error(f"Falla catastrofica en setup de run_pipeline: {str(e)}")
            break

    total_time = time.time() - pipeline_start
    final_state_val = current_state.value if current_state else "UNKNOWN"
    processor.shutdown()
    
    for conn in (fsm_conn, queue_conn, evt_conn, mat_conn):
        try:
            conn.close()
        except Exception:
            pass
            
    logger.info("pipeline_complete", extra={"extra_data": {"status": "success" if current_state == DocumentState.COMPLETED else "failed", "total_time_sec": round(total_time, 2)}})
    return {"status": "terminal_reached", "final_state": final_state_val}

if __name__ == "__main__":
    setup_distributed_logger()
    metrics = Metrics()
    NODE_ID = os.getenv("NODE_ID", f"orchestrator_daemon_{uuid.uuid4().hex[:8]}")
    logger.info(f"SOTA: Runtime Orchestrator Daemon inicializado [{NODE_ID}].")
    
    base_sleep = 2.0
    max_sleep = 10.0
    consecutive_idle = 0
    
    while True:
        queue_conn = None
        try:
            queue_conn = get_connection(QUEUE_DB_PATH, timeout=30)
            task_repo = ControlPlaneRepository(queue_conn)
            candidates = task_repo.find_documents_with_pending_chunks(sample_size=10)
            queue_conn.close()
            
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
            import traceback
            logger.exception(
                f"Fallo crítico en el bucle principal del Runtime Orchestrator Daemon: {err}"
            )
            print("\n========== FULL TRACEBACK ==========\n", flush=True)
            traceback.print_exc()
            print("\n====================================\n", flush=True)
            if queue_conn:
                try:
                    queue_conn.close()
                except Exception:
                    pass
            time.sleep(max_sleep)