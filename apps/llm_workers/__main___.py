import os
import time
import uuid
import hashlib
import random
import logging
import threading
from contextvars import copy_context

from core.utils.telemetry import setup_distributed_logger
from core.execution.exceptions import OptimisticLockError
from core.execution.ports import EventLifecycle, ProjectionState
from core.normalization.normalizer import TextNormalizer
from core.ast.registry import ASTRegistry
from infra.db.connection import get_connection
from infra.db.control_repo import ControlPlaneRepository
from infra.db.event_repo import EventPlaneRepository
from infra.db.materialized_repo import MaterializedPlaneRepository
from core.metrics.metrics import Metrics

from apps.llm_workers.gemini_client import GeminiClient
from apps.llm_workers.chunk_processor import ChunkProcessor, LLMTransientError

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
        # SOTA: Conexión dedicada exclusiva para el hilo del Heartbeat
        from infra.db.connection import get_connection
        from infra.db.control_repo import ControlPlaneRepository
        
        self.conn = get_connection(self.db_path)
        control_repo = ControlPlaneRepository(self.conn)
        
        while not self.stop_event.wait(self.interval):
            try:
                # Intenta renovar el lease en su propia transacción aislada
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
        
        # Adaptive Sleep Config
        self.base_sleep = 1.0
        self.max_sleep = 4.0

    def run(self):
        logger.info(f"Iniciando LLM Worker Daemon [{self.node_id}] - VRAM Bound")
        consecutive_idle = 0
        task = None  # Corrección 1: Previene UnboundLocalError si claim falla catastróficamente
        
        while True:
            try:
                task = self.control.claim_next_pending_task(self.node_id, self.worker_type)
                
                if not task:
                    consecutive_idle += 1
                    sleep_time = min(self.base_sleep * (1.2 ** consecutive_idle), self.max_sleep)
                    time.sleep(sleep_time + random.uniform(0.0, 0.5))
                    continue
                
                consecutive_idle = 0
                self._process_task(task)
                task = None # Reset post-ejecución limpia
                
                time.sleep(random.uniform(0.1, 0.3))
                
            except LLMTransientError:
                task_id_err = task["task_id"][:8] if task else "UNKNOWN"
                logger.warning(f"Abandono transitorio. Self-healing reasignará. Tarea: {task_id_err}")
                task = None
                time.sleep(self.max_sleep)
            except Exception as e:
                logger.exception(f"Error crítico en LLM Worker loop: {e}")
                task = None
                time.sleep(self.max_sleep)

    def _process_task(self, task: dict):
        start_node = time.perf_counter()
        
        doc_id = task["document_id"]
        ast_hash = task["ast_hash"]
        node_id = task["node_id"]
        task_id = task["task_id"]
        exec_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        logger.info("Procesando chunk...", extra={"extra_data": {"task": task_id[:8], "node": node_id}})
        
        # Carga optimizada del AST (Asume caché o índice puntual O(1))
        node = self.ast_registry.get_node(doc_id, ast_hash, node_id)
        if not node:
            logger.error("AST_NODE_NOT_FOUND", extra={"extra_data": {"node_id": node_id}})
            self.control.mark_task_failed(task_id, "AST Node missing", self.node_id, task["state_version"])
            return

        content = node.content or ""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        proj_status = self.materialized.get_projection_status(doc_id, ast_hash, node_id, self.processor.projection_v)
        if proj_status and proj_status.state == ProjectionState.CURRENT:
            # Corrección 4: Validación defensiva pasándole metadatos de pertenencia
            self.control.mark_task_completed(task_id, self.node_id, task["state_version"])
            return

        raw_response = None

        replay = self.event.get_replay(content_hash, self.processor.prompt_v, self.processor.model_v)
        if replay:
            raw_response = replay.raw_response
            logger.info("ECONOMIC_REPLAY_HIT", extra={"extra_data": {"exec_id": exec_id}})
        else:
            # Corrección 2: Pasamos la ruta física de la DB para la conexión aislada del hilo
            CONTROL_DB_PATH = os.getenv("CONTROL_DB_PATH", "infra/db/control.db")
            with TaskLeaseHeartbeat(CONTROL_DB_PATH, task_id, self.node_id) as heartbeat:
                
                raw_response = self.processor.execute(node)
                
                # Fencing Post-I/O Puro (Opción A): Si el hilo detectó pérdida del lease, disparamos pánico
                if heartbeat.lease_lost.is_set():
                    raise OptimisticLockError(f"Split-Brain evitado: el lease de {task_id} fue revocado externamente durante I/O.")

                self.event.append_wal(
                    exec_id, doc_id, node_id, content_hash, 
                    raw_response, self.processor.prompt_v, self.processor.model_v, 
                    self.processor.projection_v, EventLifecycle.GENERATED
                )

        normalized = TextNormalizer.normalize(raw_response) if getattr(node, 'type', None) != 'EQUATION' else raw_response
        normalized_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        
        self.materialized.upsert_projection(
            doc_id, ast_hash, node_id, content_hash, 
            normalized, normalized_hash, self.processor.projection_v
        )
        
        # Corrección 4: Completado atómico validando que el token de versión y dueño sigan vigentes
        self.control.mark_task_completed(task_id, self.node_id, task["state_version"])
        self.metrics.observe("node_latency", time.perf_counter() - start_node)


if __name__ == "__main__":
    CONTROL_DB_PATH = os.getenv("CONTROL_DB_PATH", "infra/db/control.db")
    EVENT_DB_PATH = os.getenv("EVENT_DB_PATH", "infra/db/event.db")
    MAT_DB_PATH = os.getenv("MAT_DB_PATH", "infra/db/materialized.db")
    
    ctrl_conn = get_connection(CONTROL_DB_PATH)
    evt_conn = get_connection(EVENT_DB_PATH)
    mat_conn = get_connection(MAT_DB_PATH)
    
    control_repo = ControlPlaneRepository(ctrl_conn)
    event_repo = EventPlaneRepository(evt_conn)
    mat_repo = MaterializedPlaneRepository(mat_conn)
    
    # Asume instanciación estándar de tus componentes core
    ast_registry = ASTRegistry() 
    metrics = Metrics()
    client = GeminiClient() 
    
    processor = ChunkProcessor(client, metrics)
    
    daemon = LLMWorkerDaemon(
        control_repo=control_repo,
        event_repo=event_repo,
        mat_repo=mat_repo,
        ast_registry=ast_registry,
        processor=processor,
        metrics=metrics
    )
    daemon.run()