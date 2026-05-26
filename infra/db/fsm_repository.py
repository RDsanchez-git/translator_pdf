from typing import Optional
import time
import logging
from core.execution.exceptions import OptimisticLockError
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass(frozen=True, slots=True)
class DocumentStatusDTO:
    document_id: str
    ast_hash: str
    current_state: str
    state_version: int
    suspended_state: Optional[str]

class FSMRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def initialize_document(self, document_id: str, ast_hash: str) -> None:
        """SOTA: Bootstrap del documento en la FSM sin leases (CAS-Driven)."""
        now = time.time()
        self.db.execute(
            """INSERT OR IGNORE INTO document_fsm 
               (document_id, ast_hash, current_state, entered_state_at, created_at, updated_at)
               VALUES (?, ?, 'CREATED', ?, ?, ?)""",
            (document_id, ast_hash, now, now, now)
        )

    def transition_to(self, document_id: str, ast_hash: str, old_state: str, new_state: str, 
                      current_version: int, owner_id: str, is_terminal: bool = False,
                      failure_reason: Optional[str] = None, suspended_state: Optional[str] = None) -> None:
        """SOTA: Transición atómica gobernada por Exclusión Mutua Optimista (CAS Duro)."""
        now = time.time()
        cursor = self.db.execute(
            """UPDATE document_fsm
               SET current_state = ?, state_version = state_version + 1, is_terminal = ?,
                   entered_state_at = ?, updated_at = ?, failure_reason = ?, suspended_state = ?
               WHERE document_id = ? AND ast_hash = ? AND current_state = ?
                 AND state_version = ?""",
            (new_state, 1 if is_terminal else 0, now, now, failure_reason, suspended_state,
             document_id, ast_hash, old_state, current_version)
        )
        if cursor.rowcount == 0:
            logger.error(f"LOCK_FAILURE: Doc {document_id[:8]} no pudo transicionar de {old_state} a {new_state}. Conflicto de versión.")
            raise OptimisticLockError(f"Conflicto de concurrencia/lock optimista en documento {document_id}")

    def get_status(self, document_id: str, ast_hash: str) -> Optional[DocumentStatusDTO]:
        """Lectura rápida inmutable para validación CAS."""
        row = self.db.execute(
            """SELECT current_state, state_version, suspended_state 
               FROM document_fsm 
               WHERE document_id = ? AND ast_hash = ?""", 
            (document_id, ast_hash)
        ).fetchone()
        
        if row is None:
            return None
            
        return DocumentStatusDTO(
            document_id=document_id,
            ast_hash=ast_hash,
            current_state=row[0],
            state_version=row[1],
            suspended_state=row[2]
        )

    def find_stalled_documents(self, threshold_sec: int = 3600) -> list[tuple[str, str]]:
        """Busca documentos que llevan demasiado tiempo en STALLED sin recuperación."""
        threshold = time.time() - threshold_sec
        cursor = self.db.execute(
            """SELECT document_id, ast_hash 
               FROM document_fsm 
               WHERE current_state = 'STALLED' AND updated_at < ?""",
            (threshold,)
        )
        return cursor.fetchall()

    def find_next_ready_for_assembly(self) -> tuple[str, str] | None:
        """SOTA: Encapsulación estricta de querying documental con fairness sin locks temporales."""
        cursor = self.db.execute(
            """
            SELECT document_id, ast_hash 
            FROM document_fsm 
            WHERE current_state = 'READY_FOR_ASSEMBLY'
              AND is_terminal = 0
            ORDER BY updated_at ASC 
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        return (row[0], row[1]) if row else None
    
    def is_document_already_processed(self, document_id: str) -> bool:
        """
        SOTA: Query de sondeo rápido indexado para cortocircuito en el segundo cero.
        Retorna True si el ID documental ya existe en la FSM en un estado no fallido.
        """
        cursor = self.db.execute(
            """
            SELECT 1 FROM document_fsm 
            WHERE document_id = ? 
              AND current_state NOT IN ('FAILED_FATAL', 'FAILED_RETRYABLE')
            LIMIT 1
            """,
            (document_id,)
        )
        return cursor.fetchone() is not None