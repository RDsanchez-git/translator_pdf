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
from core.metrics.metrics import Metrics
from apps.bootstrap.provider_stack_factory import build_provider_stack
from core.execution.models import ExecutionEnvelope
from core.execution.ports import ResourceMonitorPort
from core.execution.exceptions import ResourceExhaustedError
from core.execution.coordination import CoordinationPrimitives
from core.execution.admission import AdmissionMechanismPort, AdmissionStatus
from runtime.admission_mechanism import SequentialAdmissionMechanism
from core.execution.backpressure import BackpressureMechanismPort
from runtime.backpressure_mechanism import SequentialBackpressureMechanism

from core.execution.cancellation import CancellationToken, TaskOutcome
from core.execution.exceptions import TaskCancelledError
from runtime.coordinated_shutdown import CoordinatedShutdownMechanism

from core.execution.visibility import (
    OperationalVisibilityPort,
    WorkUnitObservation,
    WorkUnitStatus,
    outcome_to_status,
)
from runtime.operational_visibility import StructuredLogVisibility


setup_distributed_logger()
logger = logging.getLogger("worker_llm")


class TaskLeaseHeartbeat:
    """
    SOTA: Daemon Thread con conexión SQLite dedicada para evitar el Self-Lock.
    Confía exclusivamente en el estado de renovación de la base de datos (Opción A).
    """
    def __init__(
        self,
        db_path: str,
        task_id: str,
        worker_id: str,
        ttl_sec: int = 120,
        coordination: CoordinationPrimitives | None = None,  # ← NUEVO
    ):
        self.db_path = db_path
        self.task_id = task_id
        self.worker_id = worker_id
        self.ttl_sec = ttl_sec
        self.interval = ttl_sec * 0.25 
        
        self.stop_event = threading.Event()
        self.lease_lost = threading.Event()
        self.conn = None
        
        # ── CORRECCIÓN (Fallo 2): usar CoordinationPrimitives compartido ──
        self._coord = coordination

        ctx = copy_context()
        self.thread = threading.Thread(target=lambda: ctx.run(self._beat), daemon=True)

    def _beat(self):
        from infra.db.connection import get_connection
        from infra.db.control_repo import ControlPlaneRepository
        
        self.conn = get_connection(self.db_path)
        control_repo = ControlPlaneRepository(self.conn)
        
        while not self.stop_event.wait(self.interval):
            # ── CORRECCIÓN (Fallo 2): verificar si el daemon se está deteniendo ──
            if self._coord is not None and self._coord.is_stopped():
                logger.info(f"[HEARTBEAT] Daemon stopping, heartbeat for task {self.task_id[:8]} exiting.")
                break
            
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
    def __init__(
        self,
        control_repo,
        event_repo,
        mat_repo,
        ast_registry,
        processor,
        metrics,
        resource_monitor: ResourceMonitorPort | None = None,
        envelope: ExecutionEnvelope | None = None,
        coordination: CoordinationPrimitives | None = None,  # NUEVO
        worker_type: str = "llm",
        node_id: str = "node-1",
        base_sleep: float = 1.0,
        max_sleep: float = 4.0,
        admission_mechanism: AdmissionMechanismPort | None = None,
        backpressure_mechanism: BackpressureMechanismPort | None = None,
        cancellation_token: CancellationToken | None = None,  # NUEVO,
        visibility: OperationalVisibilityPort | None = None,  # NUEVO



    ) -> None:
        self.control = control_repo
        self.event = event_repo
        self.mat = mat_repo
        self.ast_registry = ast_registry
        self.processor = processor
        self.metrics = metrics
        self.worker_type = worker_type
        self.node_id = node_id
        self.base_sleep = base_sleep
        self.max_sleep = max_sleep
        self.materialized = mat_repo
        
        # Bounded Execution (Task 3.1.1)
        self._resource_monitor = resource_monitor
        self._envelope = envelope or ExecutionEnvelope.default_local()
        self._exited_due_to_resource: bool = False
        
        # Coordination Primitives (Task 3.1.2)
        self._coord = coordination or CoordinationPrimitives.create()
        # Backward compat: exponer stop_event como propiedad para signal handlers
        self._stop_event = self._coord.stop_event
        self._admission = admission_mechanism or SequentialAdmissionMechanism(safety_margin=0.90)

        # Backpressure mechanism (Task 3.2.2)
        self._backpressure = backpressure_mechanism or SequentialBackpressureMechanism(self._coord)

        self._cancellation_token = cancellation_token or CancellationToken(parent=self._coord.stop_event)
        # Operational visibility (Task 3.4.1)
        self._visibility = visibility or StructuredLogVisibility()

    def stop(self) -> None:
        """Señala shutdown coordinado a todos los threads."""
        self._coord.signal_stop()

    def run(self):
        logger.info(
            f"Iniciando LLM Worker Daemon [{self.node_id}] - VRAM Bound | "
            f"Bounded: max_rss={self._envelope.max_rss_mb}MB, "
            f"timeout={self._envelope.task_timeout_sec}s"
        )
        consecutive_idle = 0
        task = None 
        
        while not self._coord.is_stopped():
            # ── ADMISSION MECHANISM (Task 3.2.1): evaluación explícita pre-pick ──
            # NADR-F18-02 §5.2 R5, R6, R7: mecanismo de admisión explícito,
            # sin retención de recursos para trabajo rechazado, separable de política.
            if self._resource_monitor is not None:
                current_rss = self._resource_monitor.get_current_rss_mb()
                decision = self._admission.evaluate(current_rss, self._envelope.max_rss_mb)
                
                if decision.status == AdmissionStatus.REJECT:
                    # Envelope violado: fail-fast operacional (INV-NO-RESOURCE-SIGNAL)
                    logger.critical(f"[ADMISSION] Rejected: {decision.reason}")
                    self._exited_due_to_resource = True
                    self._coord.signal_stop()
                    break
                
                if decision.status == AdmissionStatus.HOLD:
                    # Presión de recursos: aplicar backpressure (espera inactiva, interrumpible)
                    # NADR-F18-02 §5.3 R8, R9: propagación de presión, bounded buffering
                    logger.info(f"[ADMISSION] Hold: {decision.reason}. Applying backpressure...")
                    self._backpressure.apply(duration_sec=2.0)
                    continue
            # ── fin admission ──
            
            try:
                # Reclamar tarea (solo si admission dijo ALLOW)
                task = self.control.claim_next_pending_task(self.node_id, self.worker_type)
                
                if not task:
                    # Sin tareas: backoff exponencial (lógica existente)
                    consecutive_idle += 1
                    sleep_time = min(self.base_sleep * (1.2 ** consecutive_idle), self.max_sleep)
                    if self._coord.wait_for_stop(timeout=sleep_time + random.uniform(0.0, 0.5)):
                        break
                    continue
                
                consecutive_idle = 0
                # ── VISIBILITY (R24): unidad reclamada ──
                self._visibility.observe(WorkUnitObservation(
                    task_id=task["task_id"],
                    worker_id=self.node_id,
                    status=WorkUnitStatus.CLAIMED,
                ))
                outcome = self._process_task(task)
                # ── VISIBILITY (R24): estado terminal ──
                self._visibility.observe(WorkUnitObservation(
                    task_id=task["task_id"],
                    worker_id=self.node_id,
                    status=outcome_to_status(outcome),
                ))
                logger.info(f"[OUTCOME] Task {task['task_id'][:8]} -> {outcome.name}")
                task = None
                
                # Pausa breve entre tareas (lógica existente)
                if self._coord.wait_for_stop(timeout=random.uniform(0.1, 0.3)):
                    break
                
            except ResourceExhaustedError as e:
                # Fail-fast ante agotamiento durante tarea (INV-NO-RESOURCE-SIGNAL)
                logger.critical(f"[BOUNDED] Resource exhausted during task: {e}")
                self._exited_due_to_resource = True
                self._coord.signal_stop()
                break
                
            except (TransientAPIError, CircuitOpenError, TimeoutError):
                # Errores transitorios: abandonar tarea, self-healing reasignará
                task_id_err = task["task_id"][:8] if task else "UNKNOWN"
                logger.warning(f"Abandono transitorio. Self-healing reasignará. Tarea: {task_id_err}")
                task = None
                self._coord.wait_for_stop(timeout=self.max_sleep)
                
            except Exception as e:
                # Errores críticos no transitorios: log + continuar
                logger.exception(f"Error crítico en LLM Worker loop: {e}")
                task = None
                self._coord.wait_for_stop(timeout=self.max_sleep)
        
        # Log final diferenciado
        if self._exited_due_to_resource:
            logger.critical(f"Daemon [{self.node_id}] detenido por violación de envelope operacional (exit code 4).")
        else:
            logger.info(f"Daemon [{self.node_id}] detenido de forma segura.")

    def _process_task(self, task: dict) -> TaskOutcome:
        """
        Ciclo completo con cancelación cooperativa.
        Retorna TaskOutcome verificable (R14).
        """
        task_id = task["task_id"]
        # Resetear token para esta tarea (por si quedó cancelado de tarea anterior)
        self._cancellation_token.reset()

        try:
            # ── Checkpoint 1 (R11): pre-process ──
            self._cancellation_token.raise_if_cancelled()

            start_node = time.perf_counter()
            
            doc_id = task["document_id"]
            ast_hash = task["ast_hash"]
            node_id = task["node_id"]
            exec_id = f"exec_{uuid.uuid4().hex[:8]}"
            
            logger.info("Procesando chunk...", extra={"extra_data": {"task": task_id[:8], "node": node_id}})
            
            node = self.ast_registry.get_node(doc_id, ast_hash, node_id)
            if not node:
                logger.error("AST_NODE_NOT_FOUND", extra={"extra_data": {"node_id": node_id}})
                self.control.mark_task_failed(task_id, "AST Node missing", self.node_id, task["state_version"])
                return TaskOutcome.FAILED

            content = node.text_content or ""
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

            proj_status = self.materialized.get_projection_status(doc_id, ast_hash, node_id, self.processor.projection_v)
            if proj_status and proj_status.state == ProjectionState.CURRENT:
                self.control.mark_task_completed(task_id, self.node_id, task["state_version"])
                return TaskOutcome.COMPLETED

            raw_response = None

            replay = self.event.get_replay(content_hash, self.processor.prompt_v, self.processor.model_v)
            if replay:
                raw_response = replay.raw_response
                logger.info("ECONOMIC_REPLAY_HIT", extra={"extra_data": {"exec_id": exec_id}})
            else:
                QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", "infra/db/queue.db")
                with TaskLeaseHeartbeat(
                    QUEUE_DB_PATH,
                    task_id,
                    self.node_id,
                    coordination=self._coord,
                ) as heartbeat:
                    
                    # ── Checkpoint 2 (R11): pre-LLM-call ──
                    self._cancellation_token.raise_if_cancelled()
                    # ── VISIBILITY (R24): llamada LLM en curso ──
                    self._visibility.observe(WorkUnitObservation(
                        task_id=task_id,
                        worker_id=self.node_id,
                        status=WorkUnitStatus.PROCESSING,
                    ))

                    raw_response = self.processor.execute(node)
                    
                    if heartbeat.lease_lost.is_set():
                        raise OptimisticLockError(f"Split-Brain evitado: el lease de {task_id} fue revocado externamente durante I/O.")

                    # Guardar en WAL ANTES del checkpoint 3 (preservar resultado del LLM)
                    # Si se cancela después, el resultado está en WAL para replay económico
                    self.event.append_wal(
                        exec_id, doc_id, node_id, content_hash, 
                        raw_response, self.processor.prompt_v, self.processor.model_v, 
                        self.processor.projection_v, EventLifecycle.GENERATED
                    )

                    # ── Checkpoint 3 (R12): pre-persist ──
                    # Si se cancela aquí, el resultado del LLM ya está en WAL (preservado)
                    # pero no se materializa la proyección ni se marca como completada
                    self._cancellation_token.raise_if_cancelled()

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
            return TaskOutcome.COMPLETED

        except TaskCancelledError as e:
            # ── R13: liberar recursos (lease liberado para retry) ──
            # abandon_execution libera la tarea para que otro worker la tome
            # El heartbeat se cierra por context manager
            # Si el LLM ya procesó, el resultado está en WAL (preservado para replay)
            self.control.abandon_execution(task_id, reason=f"CANCELLED:{e.reason}")
            logger.warning(f"[CANCEL] Task {task_id[:8]} cancelled: {e.reason} (task released for retry)")
            return TaskOutcome.CANCELLED

        except Exception as e:
            self.control.abandon_execution(task_id, reason=str(e))
            logger.error(f"[FAIL] Task {task_id[:8]} failed: {e}")
            return TaskOutcome.FAILED


if __name__ == "__main__":
    from apps.llm_workers.sync_bridge import SyncProviderBridge
    from apps.llm_workers.prompt_builder import PromptBuilder
    from core.validation.estimators import ExactBPEEstimator
    from core.execution.models import ExecutionEnvelope  # NUEVO
    from infra.resilience.sqlite_rate_limit_store import SQLiteRateLimitStore
    from infra.os.resource_monitor import PsutilSelfResourceMonitor  # NUEVO
    import sys
    from core.execution.coordination import CoordinationPrimitives
    from runtime.admission_mechanism import SequentialAdmissionMechanism
    from runtime.backpressure_mechanism import SequentialBackpressureMechanism
    from core.execution.cancellation import CancellationToken
    from runtime.operational_visibility import StructuredLogVisibility



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

    estimator = ExactBPEEstimator()
    measurement_service = InferenceMeasurementService(estimator=estimator)

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

    # DF-27: Persistencia de cuotas con SQLite WAL
    rl_conn = get_connection("infra/db/rate_limits.db", timeout=30)
    rl_conn.execute("PRAGMA busy_timeout=30000")
    rl_store = SQLiteRateLimitStore(rl_conn)

    # DF-26: Provider stack construido en Composition Root único
    provider_stack = asyncio.run(build_provider_stack(
        api_key=api_key,
        rpm_limit=rpm_limit,
        tpm_limit=tpm_limit,
        rate_limit_store=rl_store,
    ))
# Coordination Primitives: un único conjunto compartido por daemon + heartbeat
    coord = CoordinationPrimitives.create()

    envelope = ExecutionEnvelope.default_local()
    monitor = PsutilSelfResourceMonitor()
    
    processor = SyncProviderBridge(
        async_provider=provider_stack,
        prompt_builder=builder,
        timeout_sec=envelope.task_timeout_sec,
    )
    
    admission = SequentialAdmissionMechanism(safety_margin=0.90)

    backpressure = SequentialBackpressureMechanism(coordination=coord)  # NUEVO

    # Cancellation token vinculado al stop_event global
    cancellation_token = CancellationToken(parent=coord.stop_event)

    visibility = StructuredLogVisibility()  # NUEVO

    daemon = LLMWorkerDaemon(
        control_repo=control_repo,
        event_repo=event_repo,
        mat_repo=mat_repo,
        ast_registry=ast_registry,
        processor=processor,
        metrics=metrics,
        resource_monitor=monitor,
        envelope=envelope,
        coordination=coord,          # NUEVO
        admission_mechanism=admission,
        backpressure_mechanism=backpressure,
        cancellation_token=cancellation_token,  # NUEVO
        visibility=visibility,  # NUEVO
    )
    
    def shutdown_handler(signum, frame):
        logger.info(f"Señal de terminación ({signum}) recibida. Iniciando Graceful Shutdown...")
        coord.signal_stop()           # ← usa el mismo CoordinationPrimitives

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        daemon.run()
    except KeyboardInterrupt:
        coord.signal_stop()           # ← usa el mismo CoordinationPrimitives
    finally:
        # ── SHUTDOWN ORDENADO (Task 3.3.2, R15) ──
        logger.info("[SHUTDOWN] Iniciando shutdown coordinado...")
        
        shutdown = CoordinatedShutdownMechanism(
            coordination=coord,
            processor_shutdown=processor.shutdown,
            connection_closers=[
                queue_conn.close,
                evt_conn.close,
                mat_conn.close,
                rl_conn.close,
            ],
        )
        
        reason = "resource_exhaustion" if daemon._exited_due_to_resource else "normal_termination"
        report = shutdown.execute(reason=reason)
        
        logger.info(
            f"[SHUTDOWN] Completado en {report.duration_sec:.3f}s | "
            f"bridge_ok={report.bridge_shutdown_ok} | "
            f"connections_closed={report.connections_closed} | "
            f"errors={len(report.errors)}"
        )
        for err in report.errors:
            logger.error(f"[SHUTDOWN] Error: {err}")
        
        if daemon._exited_due_to_resource:
            logger.critical("Exit code 4: Operational envelope violated (INV-NO-RESOURCE-SIGNAL)")
            sys.exit(4)
        # ── fin exit code mapping ──