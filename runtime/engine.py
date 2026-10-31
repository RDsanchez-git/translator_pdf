import os
import asyncio
import sys
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
    DocumentState, TERMINAL_STATES
)
from infra.db.control_repo import ControlPlaneRepository
from core.utils.telemetry import (
    setup_distributed_logger, 
    ctx_execution_id, ctx_worker_id, ctx_task_id, ctx_node_id
)
from core.execution.exceptions import CircuitTripError, CircuitOpenError
from infra.db.connection import get_connection
from core.ast.registry import ASTRegistry
from core.ast.models import TranslationTaskType
from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
from core.finops.measurement import InferenceMeasurementService
from apps.llm_workers.prompt_builder import PromptBuilder
from core.ast.hashing import compute_ast_hash
from runtime.chunk_staging import stage_claimed_unit
from runtime.publication_pipeline import advance_staged_document
from apps.bootstrap.provider_stack_factory import build_provider_stack

logger = logging.getLogger(__name__)

FSM_DB_PATH = "infra/db/fsm.db"
QUEUE_DB_PATH = "infra/db/queue.db"
EVENT_DB_PATH = "infra/db/event.db"
MAT_DB_PATH = "infra/db/materialized.db"

GLOBAL_LLM_SEMAPHORE = threading.Semaphore(int(os.getenv("MAX_GLOBAL_LLM_CONCURRENCY", "4")))


def _create_chunk_processor():
    """Initialize paid provider only if at least one unit needs inference."""
    from apps.llm_workers.sync_bridge import SyncProviderBridge
    from core.validation.estimators import ExactBPEEstimator
    from infra.resilience.thread_owned_sqlite_rate_limit_store import ThreadOwnedSQLiteRateLimitStore
    
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
    
    # Durable SQLite quota state, confined to a dedicated owner thread.
    quota_store = ThreadOwnedSQLiteRateLimitStore("infra/db/rate_limits.db", timeout=30)

    try:
        provider_stack = asyncio.run(build_provider_stack(
            api_key=api_key,
            rpm_limit=rpm_limit,
            tpm_limit=tpm_limit,
            rate_limit_store=quota_store,
        ))
        processor = SyncProviderBridge(async_provider=provider_stack, prompt_builder=builder)
    except BaseException:
        quota_store.close()
        raise
    return processor, quota_store


def run_pipeline(document_id: str, ast_hash: str, pdf_output_name: str = "MVP_traduccion.pdf") -> dict:

    pipeline_start = time.time()
    logger.info(f"Orquestador de Runtime acoplado al Documento [ID: {document_id[:8]}]")

    fsm_conn = get_connection(FSM_DB_PATH, timeout=30)
    queue_conn = get_connection(QUEUE_DB_PATH, timeout=30)
    for conn in (fsm_conn, queue_conn):
        conn.execute("PRAGMA busy_timeout=30000")

    fsm_repo = FSMRepository(fsm_conn)
    task_repo = ControlPlaneRepository(queue_conn)
    ast_registry = ASTRegistry()

    # Verify the actual OCR AST and persisted plan before building any paid provider.
    # In particular, legacy benchmark nodes are NOT equivalent to manifest units.
    try:
        if os.getenv("IS_BENCHMARK") == "1":
            raise PipelineIntegrityError("G3_B4_3A_BENCHMARK_REQUIRES_OWN_PLAN")
        ast = ast_registry.get_document_ast(document_id, ast_hash)
        if not ast or compute_ast_hash(ast) != ast_hash:
            raise PipelineIntegrityError("G3_B4_3A_AST_MISSING_OR_HASH_MISMATCH")
        plan = task_repo.load_chunk_plan(document_id, ast_hash, ast)
        unit_index = {unit.chunk_id: unit for unit in plan.units}
        if len(unit_index) != len(plan.units):
            raise PipelineIntegrityError("G3_B4_3A_DUPLICATE_CHUNKS")
    except BaseException:
        fsm_conn.close()
        queue_conn.close()
        raise

    owner_id = f"orchestrator_{uuid.uuid4().hex[:8]}"
    current_state = None
    failure = None
    processor = None
    quota_store = None
    
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
            
            if current_state in TERMINAL_STATES:
                logger.info("PIPELINE_TERMINATED", extra={"extra_data": {"final_state": current_state.value}})
                break
                
            if current_state == DocumentState.PROCESSING:
                initial_rows = queue_conn.execute(
                    "SELECT node_id, task_state FROM chunk_tasks WHERE document_id=? AND ast_hash=? "
                    "AND worker_type='LLM'", (document_id, ast_hash),
                ).fetchall()
                initial_states = [state for _, state in initial_rows]
                if (len(initial_states) == len(plan.units) and initial_states
                        and set(initial_states) in ({"RESULT_STAGED"}, {"COMPLETED"})):
                    # Recovery-only path: no API key, rate-limiter or inference required.
                    mat_conn = get_connection(MAT_DB_PATH, timeout=30)
                    try:
                        advance_staged_document(task_repo, mat_conn, fsm_repo,
                                                plan, ast, owner_id)
                    finally:
                        mat_conn.close()
                    current_state = DocumentState.READY_FOR_ASSEMBLY
                    break

                runnable_rows = [(chunk_id, state) for chunk_id, state in initial_rows
                                 if state in ("PENDING", "RETRYABLE_ERROR")]
                has_runnable_work = bool(runnable_rows)
                needs_inference = any(
                    unit_index[chunk_id].chunk_type != TranslationTaskType.PRESERVE
                    for chunk_id, _ in runnable_rows
                )
                if needs_inference:
                    processor, quota_store = _create_chunk_processor()
                def chunk_worker_thread():
                    th_queue_conn = get_connection(QUEUE_DB_PATH, timeout=30)
                    th_queue_conn.execute("PRAGMA busy_timeout=30000")
                    th_task_repo = ControlPlaneRepository(th_queue_conn)
                    try:
                        while True:
                            task = th_task_repo.pick_task(owner_id, document_id, ast_hash)
                            if task is None:
                                break
                            chunk_id = task.node_id  # Legacy queue column stores G3 chunk_id.
                            t_exec = ctx_execution_id.set(task.execution_id)
                            t_work = ctx_worker_id.set(owner_id)
                            t_task = ctx_task_id.set(task.task_id)
                            t_node = ctx_node_id.set(chunk_id)
                            try:
                                unit = unit_index.get(chunk_id)
                                if unit is None:
                                    raise PipelineIntegrityError("G3_B4_3A_UNEXPECTED_CLAIMED_CHUNK")
                                stage_claimed_unit(th_task_repo, plan, ast, unit, task,
                                                   owner_id, processor, GLOBAL_LLM_SEMAPHORE)
                            except CircuitTripError as exc:
                                logger.critical("Circuit tripped for %s: %s", chunk_id[:8], exc)
                                th_task_repo.release_task_untouched(task.task_id, owner_id)
                                time.sleep(10.0)
                            except CircuitOpenError:
                                th_task_repo.release_task_untouched(task.task_id, owner_id)
                                time.sleep(5.0)
                            except Exception as exc:
                                logger.exception("G3_B4_3A_STAGE_FAILURE: %s", chunk_id[:8])
                                try:
                                    th_task_repo.abandon_execution(task.task_id, owner_id,
                                                                   str(exc)[:250])
                                except OptimisticLockError:
                                    pass
                            else:
                                logger.info("G3_B4_3A_RESULT_STAGED: %s", chunk_id[:8])
                            finally:
                                ctx_execution_id.reset(t_exec)
                                ctx_worker_id.reset(t_work)
                                ctx_task_id.reset(t_task)
                                ctx_node_id.reset(t_node)
                    finally:
                        th_queue_conn.close()

                if has_runnable_work:
                    max_threads = int(os.getenv("MAX_CONCURRENT_CHUNKS", "4"))
                    with ThreadPoolExecutor(max_workers=max_threads) as executor:
                        futures = [executor.submit(chunk_worker_thread) for _ in range(max_threads)]
                        for future in futures:
                            future.result()
                
                # Strictly read-only readiness check. No publication/ACK in B4/3a.
                states = queue_conn.execute(
                    "SELECT task_state FROM chunk_tasks WHERE document_id=? AND ast_hash=? "
                    "AND worker_type='LLM'", (document_id, ast_hash),
                ).fetchall()
                if len(states) != len(plan.units):
                    raise PipelineIntegrityError("G3_B4_3A_QUEUE_COVERAGE_DRIFT")
                # Preserve the pre-G3 poison-pill decision, scoped to LLM tasks.
                # A staged receipt is not a completed task, and it is not retried.
                failed = sum(state == "FAILED" for (state,) in states)
                runnable = sum(state in ("PENDING", "PROCESSING", "RETRYABLE_ERROR")
                               for (state,) in states)
                if failed and not runnable:
                    fsm_repo.transition_to(
                        document_id, ast_hash, current_state.value,
                        DocumentState.FAILED_FATAL.value, doc_status.state_version,
                        owner_id, is_terminal=True,
                        failure_reason=f"G3 staging aborted: {failed} LLM tasks failed.",
                    )
                    current_state = DocumentState.FAILED_FATAL
                    logger.error("G3_B4_3A_FAILED_FATAL: %s poisoned LLM tasks", failed)
                    break
                all_staged = bool(states) and all(state == "RESULT_STAGED" for (state,) in states)
                if all_staged or (states and all(state == "COMPLETED" for (state,) in states)):
                    mat_conn = get_connection(MAT_DB_PATH, timeout=30)
                    try:
                        advance_staged_document(task_repo, mat_conn, fsm_repo,
                                                plan, ast, owner_id)
                    finally:
                        mat_conn.close()
                    current_state = DocumentState.READY_FOR_ASSEMBLY
                else:
                    logger.info("G3_B4_3B_INCOMPLETE: %s", [state for (state,) in states])
                break

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
            failure = "optimistic_lock"
            logger.warning(f"Lock de concurrencia optimista interceptado. Abortando ejecutor local: {e}")
            break
            
        except Exception as e:
            failure = type(e).__name__
            import traceback
            print("\n!!! CRASH EN INICIALIZACION DE PIPELINE !!!", flush=True)
            traceback.print_exc()
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", flush=True)
            logger.error(f"Falla catastrofica en setup de run_pipeline: {str(e)}")
            break

    total_time = time.time() - pipeline_start
    final_state_val = current_state.value if current_state else "UNKNOWN"
    if processor is not None:
        processor.shutdown()

    for conn in (fsm_conn, queue_conn, quota_store):
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
            
    outcome = ("failed" if failure is not None else
               "ready_for_assembly" if current_state == DocumentState.READY_FOR_ASSEMBLY else
               "staging_incomplete" if current_state == DocumentState.PROCESSING else
               "terminal_reached" if current_state in TERMINAL_STATES else "not_completed")
    logger.info("pipeline_complete", extra={"extra_data": {"status": outcome,
                "total_time_sec": round(total_time, 2)}})
    return {"status": outcome, "final_state": final_state_val}

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
            recovery = task_repo.find_documents_ready_for_g3_recovery(sample_size=10)
            candidates = list(dict.fromkeys([*recovery, *candidates]))
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