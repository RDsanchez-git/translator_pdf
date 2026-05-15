from enum import Enum
from dataclasses import dataclass
from typing import Set
from core.execution.exceptions import IllegalStateTransitionError

# --- 1. ENUMS FSM ---
class DocumentState(Enum):
    CREATED = "CREATED"
    PARSING = "PARSING"
    PROCESSING = "PROCESSING"
    READY_FOR_ASSEMBLY = "READY_FOR_ASSEMBLY"
    ASSEMBLING = "ASSEMBLING"
    READY_FOR_COMPILATION = "READY_FOR_COMPILATION"
    COMPILING = "COMPILING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    STALLED = "STALLED"

# --- 2. GRAFO LEGAL ---
LEGAL_TRANSITIONS: dict[DocumentState, Set[DocumentState]] = {
    # ... [mantener transiciones previas]
    DocumentState.PARSING: {DocumentState.PROCESSING, DocumentState.FAILED, DocumentState.CANCELLED, DocumentState.STALLED},
    DocumentState.PROCESSING: {DocumentState.READY_FOR_ASSEMBLY, DocumentState.FAILED, DocumentState.CANCELLED, DocumentState.STALLED},
    DocumentState.ASSEMBLING: {DocumentState.READY_FOR_COMPILATION, DocumentState.FAILED, DocumentState.CANCELLED, DocumentState.STALLED},
    DocumentState.COMPILING: {DocumentState.COMPLETED, DocumentState.FAILED, DocumentState.CANCELLED, DocumentState.STALLED},
    DocumentState.STALLED: {
        DocumentState.PARSING, DocumentState.PROCESSING, DocumentState.READY_FOR_ASSEMBLY,
        DocumentState.ASSEMBLING, DocumentState.READY_FOR_COMPILATION, DocumentState.COMPILING, 
        DocumentState.FAILED, DocumentState.CANCELLED
    },
    # Terminales
    DocumentState.COMPLETED: set(),
    DocumentState.FAILED: set(), 
    DocumentState.CANCELLED: set(),
}

TERMINAL_STATES = {DocumentState.COMPLETED, DocumentState.FAILED, DocumentState.CANCELLED}

# --- 3. TRANSITION VALIDATOR PURO ---
class FSMValidator:
    @staticmethod
    def validate(old_state: DocumentState, new_state: DocumentState) -> None:
        """SOTA: Validación determinista en memoria. Aborta antes de tocar la DB."""
        allowed_states = LEGAL_TRANSITIONS.get(old_state, set())
        if new_state not in allowed_states:
            raise IllegalStateTransitionError(
                f"Transición FSM ilegal: No se puede mutar de {old_state.value} a {new_state.value}."
            )

# --- 4. COMMAND DTOs (Intentions) ---
@dataclass(frozen=True)
class DocumentCommand:
    """Clase base estricta para intenciones operacionales."""
    document_id: str
    ast_hash: str
    owner_id: str
    expected_version: int

@dataclass(frozen=True) 
class StartParsingCommand(DocumentCommand):
    pass

@dataclass(frozen=True) 
class StartProcessingCommand(DocumentCommand):
    pass

@dataclass(frozen=True) 
class MarkAssemblyReadyCommand(DocumentCommand):
    pass

@dataclass(frozen=True)
class StartAssemblyCommand(DocumentCommand):
    pass

@dataclass(frozen=True)
class MarkCompilationReadyCommand(DocumentCommand):
    pass

@dataclass(frozen=True)
class StartCompilationCommand(DocumentCommand):
    pass

@dataclass(frozen=True)
class CompleteDocumentCommand(DocumentCommand):
    pass

@dataclass(frozen=True) 
class FailDocumentCommand(DocumentCommand):
    reason: str

@dataclass(frozen=True) 
class CancelDocumentCommand(DocumentCommand):
    reason: str

@dataclass(frozen=True)
class StallDocumentCommand(DocumentCommand):
    reason: str

@dataclass(frozen=True)
class ResumeDocumentCommand(DocumentCommand):
    pass

@dataclass(frozen=True)
class ReconcilerCommand:
    reconciliation_id: str 
    reconciler_epoch: int  

@dataclass(frozen=True)
class RecoverZombieTaskCommand(ReconcilerCommand):
    task_id: str
    document_id: str

@dataclass(frozen=True)
class RematerializeTaskCommand(ReconcilerCommand):
    task_id: str
    document_id: str
    node_id: str
    content_hash: str
