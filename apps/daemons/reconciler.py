import time
import uuid
import random
import logging
import os
import threading
import sqlite3
from typing import Callable
from infra.db.system_repo import SystemPlaneRepository
from infra.db.control_repo import ControlPlaneRepository
from infra.db.event_repo import EventPlaneRepository
from core.execution.handlers import ReconciliationCommandHandler, DocumentCommandHandler
from contextvars import copy_context
from core.utils.telemetry import ctx_worker_id
from core.execution.state import RecoverZombieTaskCommand, RematerializeTaskCommand
from core.execution.state import MarkAssemblyReadyCommand
# (Importa los comandos definidos arriba)


logger = logging.getLogger(__name__)

class ReconcilerDaemon:
    def __init__(self, system_repo: SystemPlaneRepository,
                 task_repo: ControlPlaneRepository, event_repo: EventPlaneRepository,
                 recon_cmd_handler: ReconciliationCommandHandler,
                 doc_cmd_handler: DocumentCommandHandler,
                 ttl_sec: int = 120,
                 heartbeat_system_factory: Callable[[], tuple[SystemPlaneRepository, sqlite3.Connection]] | None = None):
        self.system = system_repo
        # The heartbeat must own its SQLite connection in its own thread.
        self.heartbeat_system_factory = heartbeat_system_factory
        self.task_repo = task_repo   
        self.event_repo = event_repo 
        self.recon_cmd_handler = recon_cmd_handler
        self.doc_cmd_handler = doc_cmd_handler
        
        self.node_id = f"reconciler_{uuid.uuid4().hex[:8]}"
        self.lease_name = "global_reconciler"
        self.ttl_sec = ttl_sec
        self.interval = ttl_sec * 0.3 
        
        self.INERTIA_WINDOW_SEC = 180.0 
        
        self.stop_event = threading.Event()
        self.is_leader = False
        self.current_epoch = 0
        # Operator alarm on durable uncertainty; no retry permission implied.
        value = os.getenv("G3_UNKNOWN_ESCALATION_SEC", "3600")
        try:
            self.unknown_escalation_sec = int(value)
        except ValueError as exc:
            raise ValueError("PPPR_G3_UNKNOWN_ESCALATION_INVALID_TTL") from exc
        if self.unknown_escalation_sec < 1:
            raise ValueError("PPPR_G3_UNKNOWN_ESCALATION_INVALID_TTL")

    def _escalate_g3_unknown(self) -> None:
        """Report persisted uncertainty without requeuing or rewriting it."""
        if not self.is_leader:
            return
        for finding in self.task_repo.list_due_g3_unknown(self.unknown_escalation_sec):
            if not self.is_leader:
                return
            logger.error(
                "PPPR_G3_UNKNOWN_OPERATOR_ESCALATION" if finding.audit_valid
                else "PPPR_G3_UNKNOWN_AUDIT_CORRUPT_REQUIRES_OPERATOR",
                extra={"extra_data": {
                    "task_id": finding.task_id,
                    "document_id": finding.document_id,
                    "ast_hash": finding.ast_hash,
                    "chunk_id": finding.chunk_id,
                    "execution_id": finding.execution_id,
                    "first_detected_at": finding.first_detected_at,
                    "cause": finding.cause,
                    "escalation_after_sec": self.unknown_escalation_sec,
                    "audit_valid": finding.audit_valid,
                    "disposition": "MANUAL_REVIEW_ONLY_NO_AUTO_RETRY",
                }},
            )

    def _sweep_fsm_stalls(self, now_safe: float):
        """SOTA: Reconciliación semántica del documento completo."""
        if not self.is_leader: 
            return

        # JOIN optimizado a través de base de datos adjunta (ATTACH)
        cursor = self.task_repo.conn.execute("""
            SELECT d.document_id, d.ast_hash, d.state_version
            FROM fsm_db.document_fsm d
            JOIN chunk_tasks c ON d.document_id = c.document_id AND d.ast_hash = c.ast_hash
            WHERE d.current_state = 'PROCESSING'
              AND d.updated_at < ?
              -- G3 documents must prove their publication and finalization.
              -- Never bypass the B4/3b barrier on task states alone.
              AND NOT EXISTS (
                  SELECT 1 FROM chunk_plans p
                  WHERE p.document_id=d.document_id AND p.ast_hash=d.ast_hash
              )
            GROUP BY d.document_id, d.ast_hash, d.state_version
            HAVING COUNT(c.task_id) > 0
               AND COUNT(c.task_id) = SUM(CASE WHEN c.task_state = 'COMPLETED' THEN 1 ELSE 0 END)
            LIMIT 50
        """, (now_safe,))
        
        stalled_docs = cursor.fetchall()
        
        for row in stalled_docs:
            if not self.is_leader: 
                return
            
            doc_id, ast_hash, state_version = row
            logger.info("FSM stall detectado. Despachando forward progress.", extra={"extra_data": {"doc_id": doc_id[:8]}})
            
            # SOTA: Forward Progress a través de la vía oficial (CQRS Command)
            # Nota: FSMValidator e Invariante de Optimistic Locking protegen contra Idempotencia aquí.
            cmd = MarkAssemblyReadyCommand(
                document_id=doc_id,
                ast_hash=ast_hash,
                owner_id=self.node_id, 
                expected_version=state_version
            )
            try:
                self.doc_cmd_handler.handle(cmd)
            except Exception as e:
                # Falla silenciosamente si otro orquestador revivió y ganó el lock
                logger.warning(f"FSM Stall bypass abortado (Posible race superado validamente): {e}")

    def _leadership_heartbeat(self):
        """Renew using a SQLite connection owned by this heartbeat thread."""
        heartbeat_conn = None
        try:
            system = self.system
            if self.heartbeat_system_factory is not None:
                system, heartbeat_conn = self.heartbeat_system_factory()
            while not self.stop_event.wait(self.interval):
                if self.is_leader:
                    success = system.renew_leadership(self.lease_name, self.node_id, self.ttl_sec)
                    if not success:
                        logger.critical("LEADERSHIP_LOST", extra={"extra_data": {"epoch": self.current_epoch}})
                        self.is_leader = False
                        self.current_epoch = 0
        except Exception:
            logger.exception("RECONCILER_HEARTBEAT_FAILED")
            self.is_leader = False
            self.current_epoch = 0
        finally:
            if heartbeat_conn is not None:
                heartbeat_conn.close()

    def run(self):
        logger.info("Iniciando nodo Reconciliador", extra={"extra_data": {"node_id": self.node_id}})
        
        ctx = copy_context()
        ctx_worker_id.set(self.node_id)
        
        heartbeat_thread = threading.Thread(target=lambda: ctx.run(self._leadership_heartbeat), daemon=True)
        heartbeat_thread.start()

        try:
            while not self.stop_event.is_set():
                if not self.is_leader:
                    epoch = self.system.acquire_leadership(self.lease_name, self.node_id, self.ttl_sec)
                    if epoch == 0:
                        # SOTA: Jitter para evitar election storms
                        if self.stop_event.wait(timeout=random.uniform(25.0, 35.0)):
                            break
                        continue
                        
                    self.is_leader = True
                    self.current_epoch = epoch
                    logger.info("LEADERSHIP_ACQUIRED", extra={"extra_data": {"epoch": self.current_epoch}})

                now_safe = time.time() - self.INERTIA_WINDOW_SEC

                # BARRIDOS PAGINADOS
                try:
                    self._sweep_tasks(now_safe)
                    self._sweep_fsm_stalls(now_safe) # Llamada al Vector 3
                    self._escalate_g3_unknown()
                except Exception as e:
                    logger.exception(f"Error crítico durante barrido paginado: {e}")
                
                # SOTA: Jitter en el ciclo principal
                if self.stop_event.wait(timeout=random.uniform(25.0, 35.0)):
                    break
                
        finally:
            self.stop_event.set()
            heartbeat_thread.join(timeout=2.0)
            if self.is_leader:
                self.system.release_leadership(self.lease_name, self.node_id)

    def _sweep_tasks(self, now_safe: float):
        """SOTA: Unifica la búsqueda de tareas estancadas (Vector 1 y 2) en una sola pasada paginada."""
        if not self.is_leader:
            return

        # PAGINACIÓN SOTA: Limit 100 para no ahogar SQLite
        cursor = self.task_repo.conn.execute("""
            SELECT task_id, document_id, node_id, updated_at, ast_hash,
                   worker_type, lease_owner, execution_id, lease_expires_at, state_version
            FROM chunk_tasks
            WHERE task_state = 'PROCESSING'
              AND lease_expires_at < ?
              AND updated_at < ?
            LIMIT 100
        """, (now_safe, now_safe))
        
        zombies = cursor.fetchall()
        
        for row in zombies:
            # Fencing Epoch: Si perdimos liderazgo a mitad del lote, abortamos instantáneamente
            if not self.is_leader:
                return 
            
            (task_id, doc_id, node_id, updated_at, ast_hash,
             worker_type, lease_owner, execution_id, lease_expires_at, state_version) = row

            if worker_type == 'ASSEMBLER':
                if not lease_owner or not execution_id or lease_expires_at is None:
                    logger.warning('G5_ASSEMBLER_LEGACY_LEASE_UNFENCED_MANUAL_REVIEW',
                                   extra={'extra_data': {'task': task_id[:8]}})
                    continue
                from infra.db.assembly_recovery import AssemblyLeaseRepository
                result = AssemblyLeaseRepository(self.task_repo.conn).recover_expired(
                    task_id=task_id, document_id=doc_id, ast_hash=ast_hash,
                    expected_owner=lease_owner, expected_execution_id=execution_id,
                    expected_expiry=lease_expires_at,
                    expected_updated_at=updated_at, expected_version=state_version,
                    reconciler_owner=self.node_id, reconciler_epoch=self.current_epoch,
                    stale_before=now_safe,
                )
                if result:
                    logger.info('G5_ASSEMBLER_EXPIRED_LEASE_' + result,
                                extra={'extra_data': {'task': task_id[:8]}})
                continue

            if (hasattr(self.task_repo, 'is_g3_chunk_task')
                    and self.task_repo.is_g3_chunk_task(task_id)):
                if worker_type == 'LLM':
                    recovered = self.task_repo.recover_expired_g3_task(
                        task_id=task_id, document_id=doc_id,
                        ast_hash=ast_hash, chunk_id=node_id,
                        expected_owner=lease_owner, expected_execution_id=execution_id,
                        expected_expiry=lease_expires_at,
                        expected_updated_at=updated_at, expected_version=state_version,
                        reconciler_owner=self.node_id, reconciler_epoch=self.current_epoch,
                        stale_before=now_safe,
                    )
                    if recovered:
                        state = self.task_repo.conn.execute(
                            "SELECT task_state FROM chunk_tasks WHERE task_id=?",
                            (task_id,),
                        ).fetchone()
                        logger.warning(
                            "G3_EXPIRED_LEASE_CLASSIFIED",
                            extra={"extra_data": {
                                "task": task_id[:8],
                                "state": state[0] if state else "UNKNOWN",
                            }},
                        )
                    else:
                        # Failed CAS may be a legitimate competing recovery;
                        # if the original expired claim survives, it remains
                        # unresolved and must not vanish from operator logs.
                        still = self.task_repo.conn.execute(
                            "SELECT 1 FROM chunk_tasks WHERE task_id=? "
                            "AND task_state='PROCESSING' AND lease_owner=? "
                            "AND execution_id=? AND lease_expires_at=?",
                            (task_id, lease_owner, execution_id, lease_expires_at),
                        ).fetchone()
                        if still:
                            logger.warning("PPPR_G3_EXPIRED_CLAIM_NOT_RECONCILED",
                                           extra={"extra_data": {
                                               "task": task_id,
                                               "execution_id": execution_id,
                                           }})
                else:
                    logger.warning("G3_NON_LLM_STALE_TASK_REQUIRES_SEPARATE_RECOVERY",
                                   extra={"extra_data": {"task": task_id[:8], "worker_type": worker_type}})
                continue  # G3 never uses legacy CQRS or its completion shortcuts.

            # SOTA: Clave de Idempotencia Determinística
            # Si el Handler ya la procesó, la ignorará
            idem_key = f"recon:{task_id}:{updated_at}"
            
            # CRUCE VECTOR 2 (CQRS Anti-Entropy) vs VECTOR 1 (Zombie puro)
            # Consultamos si existe el evento de generación en el WAL
            latest_event = self.event_repo.get_latest_event(node_id)
            
            if latest_event and latest_event.lifecycle == "GENERATED":
                # VECTOR 2: El costo de API ya se pagó. Re-materializamos.
                logger.info("Desincronización CQRS detectada.", extra={"extra_data": {"task": task_id[:8]}})
                cmd = RematerializeTaskCommand(
                    reconciliation_id=idem_key,
                    reconciler_epoch=self.current_epoch,
                    task_id=task_id,
                    document_id=doc_id,
                    ast_hash=ast_hash,           # NUEVO: NADR-08 §5.3 R8
                    node_id=node_id,
                    content_hash=latest_event.content_hash
                )
                self.recon_cmd_handler.handle(cmd)
            else:
                # VECTOR 1: Zombie puro. Devolver a PENDING.
                logger.info("Zombie detectado.", extra={"extra_data": {"task": task_id[:8]}})
                cmd = RecoverZombieTaskCommand(
                    reconciliation_id=idem_key,
                    reconciler_epoch=self.current_epoch,
                    task_id=task_id,
                    document_id=doc_id
                )
                self.recon_cmd_handler.handle(cmd)

if __name__ == "__main__":
    from core.utils.telemetry import setup_distributed_logger
    from core.metrics.metrics import Metrics
    from infra.db.control_repo import ControlPlaneRepository
    from infra.db.system_repo import SystemPlaneRepository
    from infra.db.event_repo import EventPlaneRepository
    from infra.db.materialized_repo import MaterializedPlaneRepository
    from infra.db.fsm_repository import FSMRepository
    from core.execution.handlers import DocumentCommandHandler, ReconciliationCommandHandler
    from infra.db.connection import get_connection
    
    setup_distributed_logger()
    metrics = Metrics()

    FSM_DB_PATH = os.getenv("FSM_DB_PATH", "infra/db/fsm.db")
    QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", "infra/db/queue.db")
    EVENT_DB_PATH = os.getenv("EVENT_DB_PATH", "infra/db/event.db")
    MAT_DB_PATH = os.getenv("MAT_DB_PATH", "infra/db/materialized.db")

    fsm_conn = get_connection(FSM_DB_PATH, timeout=30)
    queue_conn = get_connection(QUEUE_DB_PATH, timeout=30)
    evt_conn = get_connection(EVENT_DB_PATH, timeout=30)
    mat_conn = get_connection(MAT_DB_PATH, timeout=30)

    for conn in (fsm_conn, queue_conn, evt_conn, mat_conn):
        conn.execute("PRAGMA busy_timeout=30000")

    # Registro estático e idempotente para habilitar el JOIN inter-bases de datos en _sweep_fsm_stalls
    attached = queue_conn.execute("PRAGMA database_list").fetchall()
    if not any(db[1] == "fsm_db" for db in attached):
        queue_conn.execute(f"ATTACH DATABASE '{FSM_DB_PATH}' AS fsm_db")

    # 2. Inyección de Repositorios con asignación física segregada
    system_repo = SystemPlaneRepository(queue_conn) 
    task_repo = ControlPlaneRepository(queue_conn)
    event_repo = EventPlaneRepository(evt_conn)
    mat_repo = MaterializedPlaneRepository(mat_conn)
    fsm_repo = FSMRepository(fsm_conn)

    # 3. Inyección de Handlers
    doc_cmd_handler = DocumentCommandHandler(fsm_repo, task_repo=task_repo)
    recon_cmd_handler = ReconciliationCommandHandler(
        system_repo=system_repo,
        task_repo=task_repo,
        event_repo=event_repo,
        mat_repo=mat_repo,
        metrics=metrics
    )

    # The heartbeat opens/closes its OWN queue connection in its own thread.
    def heartbeat_system_factory():
        heartbeat_conn = get_connection(QUEUE_DB_PATH, timeout=30)
        return SystemPlaneRepository(heartbeat_conn), heartbeat_conn

    # 4. Arranque del Demonio
    daemon = ReconcilerDaemon(
        system_repo=system_repo,
        task_repo=task_repo,
        event_repo=event_repo,
        recon_cmd_handler=recon_cmd_handler,
        doc_cmd_handler=doc_cmd_handler,
        ttl_sec=120,
        heartbeat_system_factory=heartbeat_system_factory,
    )
    
    daemon.run()
