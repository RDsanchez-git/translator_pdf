import time
import logging
import random
from core.execution.state import (
    StallDocumentCommand, FailDocumentCommand
)
from core.execution.handlers import DocumentCommandHandler
from infra.db.fsm_repository import FSMRepository
from core.utils.logger import setup_logger
from infra.db.connection import get_connection

logger = logging.getLogger(__name__)

# SOTA: Rutas físicas del Triple Plane Split
CONTROL_DB_PATH = "infra/db/control.db"
EVENT_DB_PATH = "infra/db/event.db"
MAT_DB_PATH = "infra/db/materialized.db"

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
        # Forzamos el vaciado del WAL al archivo .db principal antes de hacer queries pesadas
        self._force_wal_checkpoint(EVENT_DB_PATH, "Event Plane")
        self._force_wal_checkpoint(MAT_DB_PATH, "Materialized Plane")
        self._force_wal_checkpoint(CONTROL_DB_PATH, "Control Plane")

        # --- FASE 2: RECUPERACIÓN LÓGICA (FSM & LEASES) ---
        conn_ctrl = get_connection(CONTROL_DB_PATH, timeout = 15)
        try:
            fsm_repo = FSMRepository(conn_ctrl)
            cmd_handler = DocumentCommandHandler(fsm_repo)
            
            # 1. Caza de Leases Zombies (Workers que murieron por OOM o Crash)
            stale_docs = fsm_repo.find_stale_leases()
            for doc_id, ast_hash, state, owner in stale_docs:
                logger.warning(f"SWEEPER_DETECTED_STALE_LEASE: Doc {doc_id[:8]} abandonado por {owner} en estado {state}")
                try:
                    # SOTA: El Sweeper "roba" el ownership legítimamente
                    current_version = fsm_repo.steal_expired_lease(doc_id, ast_hash, self.identity, ttl_sec=60)
                    
                    cmd = StallDocumentCommand(doc_id, ast_hash, self.identity, current_version, reason="Sweeper revoked dead lease")
                    cmd_handler.handle(cmd)
                    
                    fsm_repo.release_lease(doc_id, ast_hash, self.identity)
                    logger.info(f"SWEEPER_QUARANTINED: Doc {doc_id[:8]} movido a STALLED.")
                    
                except Exception as e:
                    logger.error(f"Fallo del Sweeper al procesar zombie {doc_id[:8]}: {e}")

            # 2. Purgatorio (Documentos estancados demasiado tiempo)
            stalled_docs = fsm_repo.find_stalled_documents(threshold_sec=3600) # 1 hora
            for doc_id, ast_hash in stalled_docs:
                 logger.warning(f"SWEEPER_PERMANENT_FAILURE: Doc {doc_id[:8]} lleva 1 hora STALLED. Abortando.")
                 try:
                     current_version = fsm_repo.steal_expired_lease(doc_id, ast_hash, self.identity, ttl_sec=60)
                     cmd = FailDocumentCommand(doc_id, ast_hash, self.identity, current_version, reason="TTL de Cuarentena (STALLED) excedido.")
                     cmd_handler.handle(cmd)
                     fsm_repo.release_lease(doc_id, ast_hash, self.identity)
                 except Exception as e:
                     logger.error(f"Fallo del Sweeper al abortar {doc_id[:8]}: {e}")
        finally:
            conn_ctrl.close()

if __name__ == "__main__":
    setup_logger()
    
    daemon = RecoveryDaemon()
    logger.info("Sweeper Daemon SOTA iniciado. Escaneando anomalías y purgando WAL...")
    
    while True:
        daemon.run_sweep_cycle()
        # SOTA: Adaptive polling con Jitter para desincronizar daemons
        time.sleep(30 + random.uniform(0.0, 5.0))