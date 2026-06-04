from dataclasses import dataclass
from core.pipeline.job import PipelineStep
from core.execution.state import DocumentState

@dataclass(frozen=True, slots=True)
class RecoveredJobSnapshot:
    """SOTA: Capa Anticorrupción. Representación agnóstica de la FSM aislada del pipeline."""
    document_id: str
    ast_hash: str
    state_value: str

# SOTA: Mapeo directo de hitos del pipeline ejecutable actual hacia la FSM operativa
PIPELINE_TO_FSM: dict[PipelineStep, DocumentState] = {
    PipelineStep.PARSING: DocumentState.PARSING,
    PipelineStep.CHUNKING: DocumentState.PROCESSING,
    PipelineStep.DISPATCHING: DocumentState.PROCESSING,
    PipelineStep.ASSEMBLING: DocumentState.ASSEMBLING,
    PipelineStep.AUDITING: DocumentState.ASSEMBLING,    # SOTA Fix: Protege barreras macro evitando KeyError
    PipelineStep.FINISHED: DocumentState.COMPLETED
}

# SOTA: Mapeo inverso corregido para Resume Macro
FSM_TO_PIPELINE_RESUME: dict[DocumentState, PipelineStep] = {
    DocumentState.PARSING: PipelineStep.PARSING,
    DocumentState.PROCESSING: PipelineStep.CHUNKING,    # Deslizamiento seguro hacia el Chunker
    DocumentState.READY_FOR_ASSEMBLY: PipelineStep.ASSEMBLING,
    DocumentState.ASSEMBLING: PipelineStep.ASSEMBLING
}