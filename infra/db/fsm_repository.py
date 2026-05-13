from typing import Optional
import time
import logging
from core.execution.exceptions import OptimisticLockError, LeaseExpiredError

logger = logging.getLogger(__name__)

class FSMRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def initialize_document(self, document_id: str, ast_hash: str) -> None:
        """SOTA: Bootstrap del documento en la FSM con liveness inicial."""
        now = time.time()
        self.db.execute(
            """INSERT OR IGNORE INTO document_state_machine 
               (document_id, ast_hash, current_state, entered_state_at, created_at, updated_at, last_heartbeat_at)
               VALUES (?, ?, 'CREATED', ?, ?, ?, ?)""",
            (document_id, ast_hash, now, now, now, now)  # now repetido para last_heartbeat_at
        )

    def transition_to(self, document_id: str, ast_hash: str, old_state: str, new_state: str, 
                      current_version: int, owner_id: str, is_terminal: bool = False,
                      failure_reason: Optional[str] = None) -> None:
        """SOTA: Mutación Atómica con Fencing Bidi-dimensional y Razones de Fallo."""
        now = time.time()
        cursor = self.db.execute(
            """UPDATE document_state_machine
               SET current_state = ?,
                   state_version = state_version + 1,
                   is_terminal = ?,
                   entered_state_at = ?,
                   updated_at = ?,
                   failure_reason = ?
               WHERE document_id = ? AND ast_hash = ?
                 AND current_state = ?
                 AND state_version = ?
                 AND lease_owner = ?
                 AND lease_expires_at > ?""",
            (new_state, 1 if is_terminal else 0, now, now, failure_reason,
             document_id, ast_hash, old_state, current_version, owner_id, now)
        )

        if cursor.rowcount == 0:
            logger.error(f"LOCK_FAILURE: Doc {document_id[:8]} no pudo transicionar de {old_state} a {new_state}.")
            raise OptimisticLockError(f"Conflicto de concurrencia en documento {document_id}")

    def acquire_lease(self, document_id: str, ast_hash: str, owner_id: str, ttl_sec: int = 300) -> int:
        """SOTA: Fence atómico de Adquisición. Muta la versión para invalidar a dueños previos."""
        now = time.time()
        expires = now + ttl_sec
        cursor = self.db.execute(
            """UPDATE document_state_machine
               SET lease_owner = ?,
                   lease_expires_at = ?,
                   last_heartbeat_at = ?,
                   updated_at = ?,
                   state_version = state_version + 1
               WHERE document_id = ? AND ast_hash = ?
                 AND (lease_owner IS NULL OR lease_expires_at < ?)
                 AND is_terminal = 0
               RETURNING state_version""",
            (owner_id, expires, now, now, document_id, ast_hash, now)
        )
        
        row = cursor.fetchone()
        if not row:
            raise OptimisticLockError(f"Lease denegado para {document_id[:8]}. Generación {ast_hash[:8]}.")
            
        return row[0]

    def get_status(self, document_id: str, ast_hash: str) -> dict:
        """SOTA: Proyección estricta del estado filtrada por generación."""
        row = self.db.execute(
            """SELECT current_state, state_version, ast_hash, lease_owner, lease_expires_at 
               FROM document_state_machine 
               WHERE document_id = ? AND ast_hash = ?""", 
            (document_id, ast_hash)
        ).fetchone()
        
        if not row:
            return {}
            
        return {
            "state": row[0], 
            "version": row[1], 
            "ast_hash": row[2],
            "lease_owner": row[3],
            "lease_expires_at": row[4]
        }
    
    def renew_lease(self, document_id: str, ast_hash: str, owner_id: str, ttl_sec: int = 300) -> None:
        """SOTA: Extensión de liveness. Falla si el worker fue declarado muerto por el Sweeper."""
        now = time.time()
        expires = now + ttl_sec
        cursor = self.db.execute(
            """UPDATE document_state_machine
               SET last_heartbeat_at = ?,
                   lease_expires_at = ?,
                   updated_at = ?
               WHERE document_id = ? AND ast_hash = ? 
                 AND lease_owner = ? 
                 AND lease_expires_at >= ?""",
            (now, expires, now, document_id, ast_hash, owner_id, now)
        )
        
        if cursor.rowcount == 0:
            logger.error("LEASE_RENEWAL_FAILED", extra={"extra_data": {"doc_id": document_id, "owner": owner_id}})
            raise LeaseExpiredError(f"Fallo al renovar lease. El worker {owner_id} perdió el ownership o expiró.")

    def release_lease(self, document_id: str, ast_hash: str, owner_id: str) -> None:
        """SOTA: Liberación segura de recursos. Falla si ya no somos los dueños."""
        now = time.time()
        cursor = self.db.execute(
            """UPDATE document_state_machine
               SET lease_owner = NULL,
                   lease_expires_at = NULL,
                   updated_at = ?
               WHERE document_id = ? AND ast_hash = ? AND lease_owner = ?""",
            (now, document_id, ast_hash, owner_id)
        )
        if cursor.rowcount == 0:
            logger.warning(f"Intento de release de lease ajeno o inexistente: Doc {document_id[:8]} por {owner_id}")