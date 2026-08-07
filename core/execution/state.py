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
    
    # SOTA: Desacoplamiento semántico de fallos
    FAILED_RETRYABLE = "FAILED_RETRYABLE" 
    FAILED_FATAL = "FAILED_FATAL"
    CANCELLED = "CANCELLED"
    STALLED = "STALLED"

# --- 2. GRAFO LEGAL ---
# SOTA: Agrupamos los fallos para no repetir código visualmente
_FAILURES = {DocumentState.FAILED_RETRYABLE, DocumentState.FAILED_FATAL}

LEGAL_TRANSITIONS: dict[DocumentState, Set[DocumentState]] = {
    DocumentState.CREATED: {DocumentState.PARSING, DocumentState.CANCELLED, DocumentState.STALLED} | _FAILURES,
    DocumentState.PARSING: {DocumentState.PROCESSING, DocumentState.CANCELLED, DocumentState.STALLED} | _FAILURES,
    DocumentState.PROCESSING: {DocumentState.READY_FOR_ASSEMBLY, DocumentState.CANCELLED, DocumentState.STALLED} | _FAILURES,
    DocumentState.READY_FOR_ASSEMBLY: {DocumentState.ASSEMBLING, DocumentState.CANCELLED, DocumentState.STALLED} | _FAILURES,
    DocumentState.ASSEMBLING: {DocumentState.READY_FOR_COMPILATION, DocumentState.CANCELLED, DocumentState.STALLED} | _FAILURES,
    DocumentState.READY_FOR_COMPILATION: {DocumentState.COMPILING, DocumentState.CANCELLED, DocumentState.STALLED} | _FAILURES,
    DocumentState.COMPILING: {DocumentState.COMPLETED, DocumentState.CANCELLED, DocumentState.STALLED} | _FAILURES,
    
    DocumentState.STALLED: {
        DocumentState.PARSING, DocumentState.PROCESSING, DocumentState.READY_FOR_ASSEMBLY,
        DocumentState.ASSEMBLING, DocumentState.READY_FOR_COMPILATION, DocumentState.COMPILING, 
        DocumentState.CANCELLED
    } | _FAILURES,
    
    # SOTA: Desde un fallo recuperable, un worker puede volver a intentar la fase en la que falló
    DocumentState.FAILED_RETRYABLE: {
        DocumentState.PARSING, DocumentState.PROCESSING, DocumentState.READY_FOR_ASSEMBLY,
        DocumentState.ASSEMBLING, DocumentState.READY_FOR_COMPILATION, DocumentState.COMPILING,
        DocumentState.FAILED_FATAL, DocumentState.CANCELLED
    },
    
    # Terminales reales
    DocumentState.COMPLETED: set(),
    DocumentState.FAILED_FATAL: set(), 
    DocumentState.CANCELLED: set(),
}

TERMINAL_STATES = {
    DocumentState.COMPLETED, 
    DocumentState.FAILED_FATAL, 
    DocumentState.CANCELLED
}

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
    ast_hash: str          # NUEVO: NADR-08 §5.3 R8 (identidad documental completa)
    node_id: str
    content_hash: str
