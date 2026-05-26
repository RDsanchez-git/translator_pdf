import time
import logging
import os
import random
from core.execution.state import (FailDocumentCommand
)
from core.execution.handlers import DocumentCommandHandler
from infra.db.fsm_repository import FSMRepository
from core.utils.logger import setup_logger
from infra.db.connection import get_connection

logger = logging.getLogger(__name__)



FSM_DB_PATH = os.getenv("FSM_DB_PATH", "infra/db/fsm.db")
QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", "infra/db/queue.db")
EVENT_DB_PATH = os.getenv("EVENT_DB_PATH", "infra/db/event.db")
MAT_DB_PATH = os.getenv("MAT_DB_PATH", "infra/db/materialized.db")

class RecoveryDaemon:
    def __init__(self):
        self.identity = "sweeper_daemon"

    def _force_wal_checkpoint(self, db_path: str, plane_name: str):
        """SOTA: Evita el colapso de latencia por crecimiento descontrolado del WAL."""
        try:
            # SOTA: Conexión efímera solo para mantenimiento
            with get_connection(db_path) as conn:
                cursor = conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                row = cursor.fetchone()
                # row[0] indica si el checkpoint fue bloqueado. 0 = Éxito.
                if row and row[0] != 0:
                    logger.warning(f"WAL Checkpoint bloqueado en {plane_name}. Lectores concurrentes activos. Estado: {row}")
        except Exception as e:
            logger.error(f"Error en WAL Checkpoint para {plane_name}: {e}")
        
    def run_sweep_cycle(self):
        """SOTA: Ciclo forense de detección, corrección y mantenimiento de disco."""
        
        # --- FASE 1: MANTENIMIENTO FÍSICO (WAL CHECKPOINT) ---
        self._force_wal_checkpoint(EVENT_DB_PATH, "Event Plane")
        self._force_wal_checkpoint(MAT_DB_PATH, "Materialized Plane")
        self._force_wal_checkpoint(FSM_DB_PATH, "FSM Plane")
        self._force_wal_checkpoint(QUEUE_DB_PATH, "Queue Plane")

        # --- FASE 2: RECUPERACIÓN LÓGICA VÍA CAS DURO ---
        conn_fsm = get_connection(FSM_DB_PATH, timeout=15)
        conn_queue = get_connection(QUEUE_DB_PATH, timeout=15)
        try:
            conn_fsm.execute("PRAGMA busy_timeout=15000")
            conn_queue.execute("PRAGMA busy_timeout=15000")
            
            fsm_repo = FSMRepository(conn_fsm)
            from infra.db.control_repo import ControlPlaneRepository
            task_repo = ControlPlaneRepository(conn_queue)
            cmd_handler = DocumentCommandHandler(fsm_repo, task_repo=task_repo)

            # Purgatorio: Desalojo de documentos estancados en STALLED por más de una hora
            stalled_docs = fsm_repo.find_stalled_documents(threshold_sec=3600)
            for doc_id, ast_hash in stalled_docs:
                 logger.warning(f"SWEEPER_PERMANENT_FAILURE: Doc {doc_id[:8]} excedió el TTL de cuarentena. Abortando.")
                 try:
                     # Hot-fetch inmutable para blindar el lock optimista (CAS)
                     status = fsm_repo.get_status(doc_id, ast_hash)
                     if status:
                         cmd = FailDocumentCommand(
                             document_id=doc_id, 
                             ast_hash=ast_hash, 
                             owner_id=self.identity, 
                             expected_version=status.state_version, 
                             reason="TTL de Cuarentena (STALLED) excedido."
                         )
                         cmd_handler.handle(cmd)
                         logger.info(f"SWEEPER_ABORTED: Doc {doc_id[:8]} movido a FAILED_FATAL de forma segura.")
                 except Exception as e:
                     logger.error(f"Fallo del Sweeper al abortar {doc_id[:8]} vía CAS: {e}")
        finally:
            for c in (conn_fsm, conn_queue):
                try:
                    c.close()
                except Exception:
                    pass

if __name__ == "__main__":
    setup_logger()
    
    daemon = RecoveryDaemon()
    logger.info("Sweeper Daemon SOTA iniciado. Escaneando anomalías y purgando WAL...")
    
    while True:
        daemon.run_sweep_cycle()
        # SOTA: Adaptive polling con Jitter para desincronizar daemons
        time.sleep(30 + random.uniform(0.0, 5.0))