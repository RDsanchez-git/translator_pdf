from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING

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
    ASSEMBLING = auto()
    AUDITING = auto()
    FINISHED = auto()

@dataclass
class TranslationJob:
    """SOTA: Entidad de dominio pura. Máquina de estados desacoplada de la persistencia."""
    job_id: str
    source_path: str
    status: JobStatus = JobStatus.PENDING
    current_step: PipelineStep = PipelineStep.INITIALIZING
    
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    
    audit_summary: Optional[TranslationAuditSummary] = None

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