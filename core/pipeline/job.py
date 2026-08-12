from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from core.metrics.summary import TranslationAuditSummary

class JobStatus(Enum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    PAUSED = auto()

class PipelineStep(Enum):
    INITIALIZING = auto()
    PARSING = auto()
    CHUNKING = auto()
    DISPATCHING = auto()
    READY_FOR_ASSEMBLY = auto()   # NUEVO — NADR-09 §5.1 R3
    ASSEMBLING = auto()
    READY_FOR_COMPILATION = auto() # NUEVO — NADR-09 §5.1 R3
    COMPILING = auto()             # NUEVO — NADR-09 §5.1 R3
    FINISHED = auto()

@dataclass
class TranslationJob:
    """SOTA: Entidad de dominio pura. Máquina de estados desacoplada de la persistencia."""
    job_id: str
    source_path: str
    
    # Ajuste operacional 11C.1: Vinculación con FSM sin filtrado de control de versiones
    document_id: Optional[str] = None
    ast_hash: Optional[str] = None
    
    status: JobStatus = JobStatus.PENDING
    current_step: PipelineStep = PipelineStep.INITIALIZING
    
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    
    audit_summary: Optional[TranslationAuditSummary] = None
    
    # SOTA: Registro seguro para metadatos del pipeline (Fase 12.00.8)
    pipeline_metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_started(self) -> None:
        """Garantiza idempotencia temporal. No sobreescribe si es una reanudación (Resume)."""
        if self.started_at is None:
            self.started_at = datetime.now()

    def mark_processing(self) -> None:
        if self.status != JobStatus.PENDING and self.status != JobStatus.PAUSED:
            raise ValueError(f"No se puede procesar un trabajo en estado: {self.status.name}")
        self.status = JobStatus.PROCESSING
        self.mark_started()

    def enter_step(self, step: PipelineStep) -> None:
        if self.status != JobStatus.PROCESSING:
            raise RuntimeError("No se pueden registrar pasos en un trabajo inactivo.")
        self.current_step = step

    def mark_completed(self, summary: TranslationAuditSummary) -> None:
        self.status = JobStatus.COMPLETED
        self.current_step = PipelineStep.FINISHED
        self.audit_summary = summary
        self.finished_at = datetime.now()

    def mark_failed(self, error_type: str, error_message: str) -> None:
        self.status = JobStatus.FAILED
        self.error_type = error_type
        self.error_message = error_message
        self.finished_at = datetime.now()