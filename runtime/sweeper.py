import time
import logging
import sqlite3
import random
from core.execution.state import (
    StallDocumentCommand, FailDocumentCommand
)
from core.execution.handlers import DocumentCommandHandler
from infra.db.fsm_repository import FSMRepository
from core.utils.logger import setup_logger

logger = logging.getLogger(__name__)

class RecoveryDaemon:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.identity = "sweeper_daemon"
        
    def run_sweep_cycle(self):
        """SOTA: Ciclo forense de detección y corrección de estado distribuido."""
        conn = sqlite3.connect(self.db_path, timeout=15)
        fsm_repo = FSMRepository(conn)
        cmd_handler = DocumentCommandHandler(fsm_repo)
        
        # 1. Caza de Leases Zombies (Workers que murieron por OOM o Crash)
        stale_docs = fsm_repo.find_stale_leases()
        for doc_id, ast_hash, state, owner in stale_docs:
            logger.warning(f"SWEEPER_DETECTED_STALE_LEASE: Doc {doc_id[:8]} abandonado por {owner} en estado {state}")
            try:
                # SOTA: El Sweeper "roba" el ownership legítimamente usando la primitiva hostil
                current_version = fsm_repo.steal_expired_lease(doc_id, ast_hash, self.identity, ttl_sec=60)
                
                # Transiciona a STALLED para que el orquestador lo recoja en el próximo boot
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
                 # También usurpamos aquí si el lease quedó tomado o vencido en cuarentena
                 current_version = fsm_repo.steal_expired_lease(doc_id, ast_hash, self.identity, ttl_sec=60)
                 cmd = FailDocumentCommand(doc_id, ast_hash, self.identity, current_version, reason="TTL de Cuarentena (STALLED) excedido.")
                 cmd_handler.handle(cmd)
                 fsm_repo.release_lease(doc_id, ast_hash, self.identity)
             except Exception as e:
                 logger.error(f"Fallo del Sweeper al abortar {doc_id[:8]}: {e}")

        conn.close()

if __name__ == "__main__":

    setup_logger()
    
    daemon = RecoveryDaemon("infra/db/document_engine.db")
    logger.info("Sweeper Daemon iniciado. Escaneando anomalías...")
    
    while True:
        daemon.run_sweep_cycle()
        # SOTA: Adaptive polling con Jitter para desincronizar daemons
        time.sleep(30 + random.uniform(0.0, 5.0))