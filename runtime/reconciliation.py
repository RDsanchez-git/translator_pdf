"""
CQRS Reconciliation Daemon.

NADR-10 §5.2 R8: El mecanismo de reconciliación MUST estar activo en producción.
NADR-10 §5.2 R11: La activación MUST estar gobernada por configuración externa.
NADR-10 §5.2 R12: MUST NOT existir banderas de código que desactiven la reconciliación.
"""

import time
import logging
import random
from infra.db.connection import get_connection
from infra.db.control_repo import ControlPlaneRepository
from infra.db.event_repo import EventPlaneRepository
from infra.db.materialized_repo import MaterializedPlaneRepository
from infra.db.system_repo import SystemPlaneRepository
from core.execution.handlers import ReconciliationCommandHandler
from core.execution.state import RecoverZombieTaskCommand
from core.metrics.metrics import Metrics
from runtime.settings import RuntimeSettings

logger = logging.getLogger(__name__)


class CQRSReconciliationDaemon:
    """Daemon asíncrono para sanación de proyecciones y liberación de leases huérfanos."""
    
    def __init__(self, settings: RuntimeSettings):
        self.identity = "global_reconciler"
        self.metrics = Metrics()
        self._settings = settings

    def run_reconciliation_cycle(self) -> None:
        """Sana inconsistencias de sub-tareas individuales en el Control Plane."""
        # NADR-10 §5.2 R11: La activación se gobierna por configuración inyectada
        if not self._settings.reconciliation_enabled:
            logger.info(
                "Reconciliación CQRS desactivada por configuración externa."
            )
            return

        with get_connection("infra/db/queue.db") as q_conn, \
             get_connection("infra/db/event.db") as e_conn, \
             get_connection("infra/db/materialized.db") as m_conn, \
             get_connection("infra/db/fsm.db") as sys_conn:
             
            task_repo = ControlPlaneRepository(q_conn)
            event_repo = EventPlaneRepository(e_conn)
            mat_repo = MaterializedPlaneRepository(m_conn)
            system_repo = SystemPlaneRepository(sys_conn)
            
            handler = ReconciliationCommandHandler(
                system_repo=system_repo,
                task_repo=task_repo,
                event_repo=event_repo,
                mat_repo=mat_repo,
                metrics=self.metrics
            )
            
            try:
                epoch = system_repo.get_current_epoch(self.identity)
            except Exception:
                epoch = 1

            candidates = task_repo.find_documents_with_pending_chunks(sample_size=10)
            
            for doc_id, ast_hash in candidates:
                cursor = q_conn.execute(
                    "SELECT task_id FROM chunk_tasks WHERE document_id = ? AND task_state = 'PROCESSING' AND lease_expires_at < ?",
                    (doc_id, time.time())
                )
                expired_tasks = cursor.fetchall()
                
                for (task_id,) in expired_tasks:
                    logger.warning(f"LEASE_EXPIRED: Sub-tarea {task_id[:8]} huérfana. Sanando lease.")
                    
                    cmd = RecoverZombieTaskCommand(
                        reconciliation_id=f"rec_{time.time_ns()}",
                        reconciler_epoch=epoch,
                        task_id=task_id,
                        document_id=doc_id
                    )
                    
                    try:
                        handler.handle(cmd)
                        q_conn.commit()
                    except Exception as e:
                        logger.error(f"Falla al reconciliar tarea {task_id[:8]}: {str(e)}")


if __name__ == "__main__":
    import os
    from core.utils.telemetry import setup_distributed_logger
    setup_distributed_logger()
    
    # La lectura de env se hace en el borde (imperative shell), no en el daemon
    enabled = os.environ.get("PHASE17BIS_RECONCILIATION_ENABLED", "true").lower() in ("true", "1", "yes")
    settings = RuntimeSettings(reconciliation_enabled=enabled)
    
    reconciler = CQRSReconciliationDaemon(settings=settings)
    logger.info("Daemon de Reconciliación CQRS inicializado.")
    
    while True:
        reconciler.run_reconciliation_cycle()
        time.sleep(settings.sweep_interval_seconds + random.uniform(0.0, settings.sweep_jitter_seconds))