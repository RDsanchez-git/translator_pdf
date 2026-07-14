import os
import time
import uuid
import hashlib
import random
import logging
import threading
from contextvars import copy_context
import signal
import asyncio

from core.utils.telemetry import setup_distributed_logger
from core.execution.exceptions import OptimisticLockError, TransientAPIError, CircuitOpenError
from core.execution.ports import EventLifecycle, ProjectionState
from core.normalization.normalizer import TextNormalizer
from core.ast.registry import ASTRegistry
from core.ast.enums import ContentNodeType
from infra.db.connection import get_connection
from infra.db.control_repo import ControlPlaneRepository
from infra.db.event_repo import EventPlaneRepository
from infra.db.materialized_repo import MaterializedPlaneRepository
from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
from core.finops.measurement import InferenceMeasurementService
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
from core.metrics.metrics import Metrics

setup_distributed_logger()
logger = logging.getLogger("worker_llm")

class TaskLeaseHeartbeat:
    """
    SOTA: Daemon Thread con conexión SQLite dedicada para evitar el Self-Lock.
    Confía exclusivamente en el estado de renovación de la base de datos (Opción A).
    """
    def __init__(self, db_path: str, task_id: str, worker_id: str, ttl_sec: int = 120):
        self.db_path = db_path
        self.task_id = task_id
        self.worker_id = worker_id
        self.ttl_sec = ttl_sec
        self.interval = ttl_sec * 0.25 
        
        self.stop_event = threading.Event()
        self.lease_lost = threading.Event()
        self.conn = None

        ctx = copy_context()
        self.thread = threading.Thread(target=lambda: ctx.run(self._beat), daemon=True)

    def _beat(self):
        from infra.db.connection import get_connection
        from infra.db.control_repo import ControlPlaneRepository
        
        self.conn = get_connection(self.db_path)
        control_repo = ControlPlaneRepository(self.conn)
        
        while not self.stop_event.wait(self.interval):
            try:
                success = control_repo.renew_task_lease(self.task_id, self.worker_id, self.ttl_sec)
                if not success:
                    logger.critical("LEASE_LOST_DURING_IO", extra={"extra_data": {"task": self.task_id[:8]}})
                    self.lease_lost.set()
                    break
            except Exception as e:
                logger.error(f"Fallo en hilo de heartbeat al conectar a DB: {e}")
                self.lease_lost.set()
                break
                
        self.conn.close()

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_event.set() 
        self.thread.join(timeout=2.0)


class LLMWorkerDaemon:
    """SOTA: Orquestador físico del Worker LLM (Fast-Path, Replay & Execution)."""
    def __init__(self, control_repo, event_repo, mat_repo, ast_registry, processor, metrics):
        self.control = control_repo
        self.event = event_repo
        self.materialized = mat_repo
        self.ast_registry = ast_registry
        self.processor = processor
        self.metrics = metrics
        
        self.node_id = f"llm_worker_{uuid.uuid4().hex[:8]}"
        self.worker_type = "LLM"
        
        self.base_sleep = 1.0
        self.max_sleep = 4.0
        
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """Solicita la detención segura del bucle principal."""
        self._stop_event.set()

    def run(self):
        logger.info(f"Iniciando LLM Worker Daemon [{self.node_id}] - VRAM Bound")
        consecutive_idle = 0
        task = None 
        
        while not self._stop_event.is_set():
            try:
                task = self.control.claim_next_pending_task(self.node_id, self.worker_type)
                
                if not task:
                    consecutive_idle += 1
                    sleep_time = min(self.base_sleep * (1.2 ** consecutive_idle), self.max_sleep)
                    if self._stop_event.wait(timeout=sleep_time + random.uniform(0.0, 0.5)):
                        break
                    continue
                
                consecutive_idle = 0
                self._process_task(task)
                task = None
                
                if self._stop_event.wait(timeout=random.uniform(0.1, 0.3)):
                    break
                
            except (TransientAPIError, CircuitOpenError, TimeoutError):
                task_id_err = task["task_id"][:8] if task else "UNKNOWN"
                logger.warning(f"Abandono transitorio. Self-healing reasignará. Tarea: {task_id_err}")
                task = None
                self._stop_event.wait(timeout=self.max_sleep)
            except Exception as e:
                logger.exception(f"Error crítico en LLM Worker loop: {e}")
                task = None
                self._stop_event.wait(timeout=self.max_sleep)
                
        logger.info(f"Daemon [{self.node_id}] detenido de forma segura.")

    def _process_task(self, task: dict):
        start_node = time.perf_counter()
        
        doc_id = task["document_id"]
        ast_hash = task["ast_hash"]
        node_id = task["node_id"]
        task_id = task["task_id"]
        exec_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        logger.info("Procesando chunk...", extra={"extra_data": {"task": task_id[:8], "node": node_id}})
        
        node = self.ast_registry.get_node(doc_id, ast_hash, node_id)
        if not node:
            logger.error("AST_NODE_NOT_FOUND", extra={"extra_data": {"node_id": node_id}})
            self.control.mark_task_failed(task_id, "AST Node missing", self.node_id, task["state_version"])
            return

        # SOTA FIX: Uso de la propiedad fachada polimórfica .text_content
        content = node.text_content or ""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        proj_status = self.materialized.get_projection_status(doc_id, ast_hash, node_id, self.processor.projection_v)
        if proj_status and proj_status.state == ProjectionState.CURRENT:
            self.control.mark_task_completed(task_id, self.node_id, task["state_version"])
            return

        raw_response = None

        replay = self.event.get_replay(content_hash, self.processor.prompt_v, self.processor.model_v)
        if replay:
            raw_response = replay.raw_response
            logger.info("ECONOMIC_REPLAY_HIT", extra={"extra_data": {"exec_id": exec_id}})
        else:
            QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", "infra/db/queue.db")
            with TaskLeaseHeartbeat(QUEUE_DB_PATH, task_id, self.node_id) as heartbeat:
                
                raw_response = self.processor.execute(node)
                
                if heartbeat.lease_lost.is_set():
                    raise OptimisticLockError(f"Split-Brain evitado: el lease de {task_id} fue revocado externamente durante I/O.")

                self.event.append_wal(
                    exec_id, doc_id, node_id, content_hash, 
                    raw_response, self.processor.prompt_v, self.processor.model_v, 
                    self.processor.projection_v, EventLifecycle.GENERATED
                )

        # SOTA FIX: Elisión de la normalización evaluando granularidad fina del AST V2 (DISPLAY e INLINE EQUATION)
        if node.node_type in (ContentNodeType.DISPLAY_EQUATION, ContentNodeType.INLINE_EQUATION):
            normalized = raw_response
        else:
            normalized = TextNormalizer.normalize(raw_response)
            
        normalized_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        
        self.materialized.upsert_projection(
            doc_id, ast_hash, node_id, content_hash, 
            normalized, normalized_hash, self.processor.projection_v
        )
        
        self.control.mark_task_completed(task_id, self.node_id, task["state_version"])
        self.metrics.observe("node_latency", time.perf_counter() - start_node)


if __name__ == "__main__":
    from apps.llm_workers.sync_bridge import SyncProviderBridge
    from apps.llm_workers.adapters import GroqProvider
    from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
    from apps.llm_workers.cache_provider import CachedLLMProvider
    from apps.llm_workers.prompt_builder import PromptBuilder
    from core.ast.models import FastWordEstimator

    QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", "infra/db/queue.db")
    EVENT_DB_PATH = os.getenv("EVENT_DB_PATH", "infra/db/event.db")
    MAT_DB_PATH = os.getenv("MAT_DB_PATH", "infra/db/materialized.db")
    
    queue_conn = get_connection(QUEUE_DB_PATH)
    evt_conn = get_connection(EVENT_DB_PATH)
    mat_conn = get_connection(MAT_DB_PATH)
    
    for conn in (queue_conn, evt_conn, mat_conn):
        conn.execute("PRAGMA busy_timeout=30000")
    
    control_repo = ControlPlaneRepository(queue_conn)
    event_repo = EventPlaneRepository(evt_conn)
    mat_repo = MaterializedPlaneRepository(mat_conn)
    
    ast_registry = ASTRegistry() 
    metrics = Metrics()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY no configurada. Imposible operar motor LLM.")

    estimator = FastWordEstimator()
    measurement_service = InferenceMeasurementService(estimator=estimator)

    # SOTA FIX: Firma FinOps corregida sin el parámetro estimator obsoleto
    budget_calculator = PromptBudgetCalculator(
        primary_window_limit=8192,
        fallback_window_limit=1048576,
        min_output_reserve=256,
        max_output_reserve=4096
    )

    compression_policy = StandardCompressionPolicy()

    # SOTA FIX: Inyección de la suite FinOps completa requerida por PromptBuilder en la Fase 16
    builder = PromptBuilder(
        model_name="llama3-70b-8192", 
        prompt_version="v1.0", 
        measurement_service=measurement_service,
        budget_calculator=budget_calculator,
        compression_policy=compression_policy
    )
    
    # SOTA FIX: Inyección del dialecto estricto de OpenAI y remoción de ResilientProvider
    dialect = OpenAICompatibleDialect()
    groq_provider = GroqProvider(api_key=api_key, dialect=dialect)
    quota = QuotaManager(rpm_limit=30, tpm_limit=6000)
    rate_provider = RateLimitedProvider(underlying=groq_provider, quota_manager=quota)
    
    cached_provider = CachedLLMProvider(rate_provider, db_path=MAT_DB_PATH)
    
    asyncio.run(cached_provider.initialize())
    
    processor = SyncProviderBridge(async_provider=cached_provider, prompt_builder=builder)

    daemon = LLMWorkerDaemon(
        control_repo=control_repo,
        event_repo=event_repo,
        mat_repo=mat_repo,
        ast_registry=ast_registry,
        processor=processor,
        metrics=metrics
    )
    
    def shutdown_handler(signum, frame):
        logger.info(f"Señal de terminación ({signum}) recibida. Iniciando Graceful Shutdown...")
        daemon.stop()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        daemon.run()
    except KeyboardInterrupt:
        daemon.stop()
    finally:
        logger.info("Liberando recursos globales...")
        processor.shutdown()
        for conn in (queue_conn, evt_conn, mat_conn):
            try:
                conn.close()
            except Exception:
                pass