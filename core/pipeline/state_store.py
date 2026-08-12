# core/pipeline/state_store.py
"""
Adaptador hexagonal pasivo para la máquina de estados.

NADR-09 §5.1 R2: Los adaptadores de persistencia MUST NOT emitir,
interceptar ni sintetizar comandos o transiciones de estado.
NADR-09 §5.1 R5: MUST NOT existir mecanismos de auto-promoción.
"""

from typing import Protocol, Optional
from core.execution.state import DocumentCommand
from core.execution.state_mapping import RecoveredJobSnapshot
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler


class StateStoreProtocol(Protocol):
    """Puerto de persistencia abstracto para la máquina de estados."""

    def initialize(self, doc_id: str, ast_hash: str) -> None: ...

    def dispatch(self, command: DocumentCommand) -> int: ...

    def load(self, job_id: str) -> Optional[RecoveredJobSnapshot]: ...

    def get_current_version(self, doc_id: str, ast_hash: str) -> int: ...


class FSMStateStore:
    """
    Adaptador hexagonal pasivo.
    Sin STEP_TO_COMMAND_CLASS. Sin intercepciones. Sin save(job).
    """

    def __init__(self, fsm_repo: FSMRepository, command_handler: DocumentCommandHandler):
        self.fsm_repo = fsm_repo
        self.handler = command_handler

    def initialize(self, doc_id: str, ast_hash: str) -> None:
        self.fsm_repo.initialize_document(doc_id, ast_hash)

    def dispatch(self, command: DocumentCommand) -> int:
        return self.handler.handle(command)

    def load(self, job_id: str) -> Optional[RecoveredJobSnapshot]:
        dto = self.fsm_repo.get_by_document_id(job_id)
        if not dto:
            return None
        return RecoveredJobSnapshot(
            document_id=job_id,
            ast_hash=dto.ast_hash,
            state_value=dto.current_state
        )

    def get_current_version(self, doc_id: str, ast_hash: str) -> int:
        status = self.fsm_repo.get_status(doc_id, ast_hash)
        if status is None:
            raise ValueError(f"Documento {doc_id} no encontrado en FSM")
        return status.state_version