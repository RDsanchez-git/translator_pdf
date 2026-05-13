import logging
from core.execution.state import (
    DocumentCommand, StartParsingCommand, StartProcessingCommand,
    MarkAssemblyReadyCommand, StartAssemblyCommand, MarkCompilationReadyCommand,
    StartCompilationCommand, CompleteDocumentCommand, FailDocumentCommand,
    CancelDocumentCommand, DocumentState, FSMValidator, TERMINAL_STATES
)
from infra.db.fsm_repository import FSMRepository

logger = logging.getLogger(__name__)

class DocumentCommandHandler:
    """SOTA: Capa de coordinación pura. Transiciona estados sin ejecutar side-effects."""
    
    def __init__(self, repository: FSMRepository):
        self.repo = repository

    def _get_target_state(self, command: DocumentCommand) -> DocumentState:
        """Asigna la semántica operacional (intención -> estado)."""
        mapping = {
            StartParsingCommand: DocumentState.PARSING,
            StartProcessingCommand: DocumentState.PROCESSING,
            MarkAssemblyReadyCommand: DocumentState.READY_FOR_ASSEMBLY,
            StartAssemblyCommand: DocumentState.ASSEMBLING,
            MarkCompilationReadyCommand: DocumentState.READY_FOR_COMPILATION,
            StartCompilationCommand: DocumentState.COMPILING,
            CompleteDocumentCommand: DocumentState.COMPLETED,
            FailDocumentCommand: DocumentState.FAILED,
            CancelDocumentCommand: DocumentState.CANCELLED
        }
        target = mapping.get(type(command))
        if not target:
            raise TypeError(f"Comando desconocido: {type(command)}")
        return target

    def handle(self, command: DocumentCommand) -> int:
        """
        Ejecuta el ciclo de vida de la transición FSM:
        1. Extracción de estado actual físico.
        2. Validación de contrato FSM (en memoria).
        3. Mutación Atómica con Optimistic Locking.
        Retorna la nueva versión de estado (state_version) si es exitoso.
        """
        # 1. Fotografía física del estado (Read)
        doc_status = self.repo.get_status(command.document_id, command.ast_hash)
        if not doc_status:
            raise ValueError(f"Documento {command.document_id} no inicializado en FSM.")
        
        current_state = DocumentState(doc_status["state"])
        db_ast_hash = doc_status["ast_hash"]

        # Protección cruzada contra colisiones generacionales
        if db_ast_hash != command.ast_hash:
            raise ValueError(f"Fuga generacional: Comando esperaba {command.ast_hash}, FSM tiene {db_ast_hash}")

        # 2. Intención
        target_state = self._get_target_state(command)

        # 3. Validación Matemática de Transición (Invariante FSM)
        FSMValidator.validate(current_state, target_state)

        # Manejo de razones para estados de fallo
        is_terminal = target_state in TERMINAL_STATES
        failure_reason = getattr(command, "reason", None) if is_terminal else None

        # 4. Transacción Física (Write) - Falla ruidosamente si pierde el Lock o Lease
        self.repo.transition_to(
            document_id=command.document_id,
            ast_hash=command.ast_hash,
            old_state=current_state.value,
            new_state=target_state.value,
            current_version=command.expected_version,
            owner_id=command.owner_id,
            is_terminal=is_terminal,
            failure_reason=failure_reason # Requiere agregar este parámetro en transition_to de FSMRepository
        )

        logger.info("FSM_TRANSITION_SUCCESS", extra={
            "extra_data": {
                "doc_id": command.document_id[:8],
                "transition": f"{current_state.value} -> {target_state.value}",
                "new_version": command.expected_version + 1
            }
        })

        return command.expected_version + 1