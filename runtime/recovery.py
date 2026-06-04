import time
import logging
import random
from infra.db.connection import get_connection
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler
from core.execution.state import StallDocumentCommand
from core.execution.exceptions import OptimisticLockError

logger = logging.getLogger(__name__)

class AbandonedProcessWatchdog:
    """SOTA: Escanea el plano de control para detectar caídas físicas de workers y aislar hilos zombies."""
    
    def __init__(self, fsm_db_path: str = "infra/db/fsm.db"):
        self.fsm_db_path = fsm_db_path
        self.identity = "watchdog_recovery_daemon"

    def execute_sweep(self, threshold_sec: int = 3600) -> None:
        """Identifica documentos colapsados en transiciones activas y los promueve a STALLED."""
        with get_connection(self.fsm_db_path, timeout=15) as conn:
            fsm_repo = FSMRepository(conn)
            cmd_handler = DocumentCommandHandler(fsm_repo)
            
            abandoned_docs = fsm_repo.find_stalled_documents(threshold_sec=threshold_sec)
            
            for doc_id, ast_hash in abandoned_docs:
                status = fsm_repo.get_status(doc_id, ast_hash)
                if not status:
                    continue
                    
                logger.warning(f"ZOMBIE_DETECTED: Documento {doc_id[:8]} estancado en {status.current_state}. Aislando.")
                
                cmd = StallDocumentCommand(
                    document_id=doc_id,
                    ast_hash=ast_hash,
                    owner_id=self.identity,
                    expected_version=status.state_version,
                    reason=f"Timeout operacional excedido ({threshold_sec}s)."
                )
                
                try:
                    cmd_handler.handle(cmd)
                    conn.commit()
                    logger.info(f"ZOMBIE_ISOLATED: Documento {doc_id[:8]} movido a STALLED.")
                except OptimisticLockError:
                    logger.warning(f"FENCING_CONFLICT: Conflicto CAS en {doc_id[:8]}. Worker activo mutó el estado.")
                except Exception as e:
                    logger.error(f"Falla al procesar aislamiento para {doc_id[:8]}: {str(e)}")

if __name__ == "__main__":
    from core.utils.telemetry import setup_distributed_logger
    setup_distributed_logger()
    
    watchdog = AbandonedProcessWatchdog()
    logger.info("Watchdog de Procesos Abandonados MVP inicializado.")
    
    while True:
        watchdog.execute_sweep(threshold_sec=3600)
        time.sleep(30 + random.uniform(0.0, 5.0))