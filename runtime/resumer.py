import logging
from infra.db.connection import get_connection
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler
from core.execution.state import ResumeDocumentCommand
from core.execution.exceptions import OptimisticLockError, IllegalStateTransitionError

logger = logging.getLogger(__name__)

class OnDemandResumeManager:
    """SOTA: Capa de servicio encargada de levantar bloqueos de cuarentena bajo demanda."""
    
    def __init__(self, fsm_db_path: str = "infra/db/fsm.db"):
        self.fsm_db_path = fsm_db_path
        self.identity = "manual_resume_manager"

    def rescue_stalled_document(self, document_id: str, ast_hash: str) -> bool:
        """Transiciona un documento de STALLED a su estado suspendido original via CAS."""
        with get_connection(self.fsm_db_path, timeout=15) as conn:
            fsm_repo = FSMRepository(conn)
            cmd_handler = DocumentCommandHandler(fsm_repo)
            
            status = fsm_repo.get_status(document_id, ast_hash)
            if not status:
                logger.error(f"RESUME_REJECTED: El documento {document_id} no existe en la FSM.")
                return False
                
            if status.current_state != "STALLED":
                logger.info(f"RESUME_BYPASS: El documento {document_id} está en {status.current_state}. No requiere rescate.")
                return True

            if not status.suspended_state:
                logger.critical(f"INTEGRITY_VIOLATION: Documento {document_id} en STALLED no posee estado suspendido.")
                return False

            cmd = ResumeDocumentCommand(
                document_id=document_id,
                ast_hash=ast_hash,
                owner_id=self.identity,
                expected_version=status.state_version
            )
            
            try:
                cmd_handler.handle(cmd)
                conn.commit()
                logger.info(f"RESUME_SUCCESS: Cuarentena levantada para {document_id}. Retornado a {status.suspended_state}.")
                return True
            except (OptimisticLockError, IllegalStateTransitionError) as err:
                logger.warning(f"RESUME_LOCK_FAILURE: Conflicto en FSM al reanudar {document_id}: {str(err)}")
                return False