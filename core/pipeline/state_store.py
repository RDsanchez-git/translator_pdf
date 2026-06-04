from typing import Protocol, Optional, Type
from core.pipeline.job import TranslationJob, PipelineStep, JobStatus
from core.execution.state_mapping import RecoveredJobSnapshot
from core.execution.state import (
    DocumentCommand,
    StartParsingCommand,
    StartProcessingCommand,
    StartAssemblyCommand,
    CompleteDocumentCommand,
    FailDocumentCommand
)
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler

class StateStoreProtocol(Protocol):
    """SOTA: Puerto de persistencia abstracto para la máquina de estados del Job."""
    
    def save(self, job: TranslationJob) -> None:
        """Upsert idempotente del estado actual del trabajo."""
        ...
        
    def load(self, job_id: str) -> Optional[RecoveredJobSnapshot]:
        """Recupera el snapshot agnóstico para reanudación macro."""
        ...

class FSMStateStore(StateStoreProtocol):
    """SOTA: Adaptador Hexagonal Definitivo. Conecta el Runtime con la FSM Operacional."""

    # Mapeo estricto 1:1. Se remueve AUDITING para evitar transiciones forzadas artificiales
    STEP_TO_COMMAND_CLASS: dict[PipelineStep, Type[DocumentCommand]] = {
        PipelineStep.PARSING: StartParsingCommand,
        PipelineStep.CHUNKING: StartProcessingCommand,
        PipelineStep.DISPATCHING: StartProcessingCommand,
        PipelineStep.ASSEMBLING: StartAssemblyCommand,
        PipelineStep.FINISHED: CompleteDocumentCommand
    }

    def __init__(self, fsm_repo: FSMRepository, command_handler: DocumentCommandHandler):
        self.fsm_repo = fsm_repo
        self.handler = command_handler
        self.owner_id = "pipeline_runtime_layer"

    def load(self, job_id: str) -> Optional[RecoveredJobSnapshot]:
        """SOTA Fix: Rehidrata el estado delegando exclusivamente en el FSMRepository."""
        dto = self.fsm_repo.get_by_document_id(job_id)
        if not dto:
            return None
            
        return RecoveredJobSnapshot(
            document_id=job_id,
            ast_hash=dto.ast_hash,
            state_value=dto.current_state
        )

    def save(self, job: TranslationJob) -> None:
        """Traduce el progreso a mutaciones gobernadas por CAS con control estricto de idempotencia."""
        doc_id = job.document_id or job.job_id
        
        if not job.ast_hash:
            raise RuntimeError(f"Falla de Integridad: No se puede persistir el estado sin un ast_hash válido para {doc_id}")
            
        ast_hash = job.ast_hash
        status = self.fsm_repo.get_status(doc_id, ast_hash)
        
        if status is None:
            if job.current_step != PipelineStep.PARSING:
                raise RuntimeError(f"Falla de Inicialización: El documento {doc_id} no existe en la FSM.")
            self.fsm_repo.initialize_document(doc_id, ast_hash)
            status = self.fsm_repo.get_status(doc_id, ast_hash)
            if status is None:
                raise RuntimeError(f"Falla crítica de E/S en FSM para {doc_id}")

        cmd_class = self.STEP_TO_COMMAND_CLASS.get(job.current_step)
        if not cmd_class and job.status != JobStatus.FAILED:
            return

        if job.status != JobStatus.FAILED and cmd_class:
            from core.execution.state_mapping import PIPELINE_TO_FSM
            target_state = PIPELINE_TO_FSM[job.current_step]
            if status.current_state == target_state.value:
                return

        expected_version = status.state_version

        if job.status == JobStatus.FAILED:
            command = FailDocumentCommand(
                document_id=doc_id,
                ast_hash=ast_hash,
                owner_id=self.owner_id,
                expected_version=expected_version,
                reason=job.error_message or "Falla no controlada en runtime."
            )
        elif cmd_class is not None:
            # Intercepción A: Transición obligatoria de procesamiento a ensamblado
            if status.current_state == "PROCESSING" and cmd_class == StartAssemblyCommand:
                from core.execution.state import MarkAssemblyReadyCommand
                cmd_ready = MarkAssemblyReadyCommand(
                    document_id=doc_id, ast_hash=ast_hash,
                    owner_id=self.owner_id, expected_version=expected_version
                )
                expected_version = self.handler.handle(cmd_ready)
            
            # SOTA Fix (Error 1): Intercepción y auto-promoción secuencial de la fase de compilación
            if status.current_state == "ASSEMBLING" and cmd_class == CompleteDocumentCommand:
                from core.execution.state import MarkCompilationReadyCommand, StartCompilationCommand
                
                cmd_ready_comp = MarkCompilationReadyCommand(
                    document_id=doc_id, ast_hash=ast_hash,
                    owner_id=self.owner_id, expected_version=expected_version
                )
                expected_version = self.handler.handle(cmd_ready_comp)
                
                cmd_start_comp = StartCompilationCommand(
                    document_id=doc_id, ast_hash=ast_hash,
                    owner_id=self.owner_id, expected_version=expected_version
                )
                expected_version = self.handler.handle(cmd_start_comp)
            
            command = cmd_class(
                document_id=doc_id,
                ast_hash=ast_hash,
                owner_id=self.owner_id,
                expected_version=expected_version
            )
        else:
            return

        self.handler.handle(command)