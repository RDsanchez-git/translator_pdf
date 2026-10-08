import json
import time
import hashlib
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List

class ProcessingStage(Enum):
    GENERATION = "generation"
    NORMALIZATION = "normalization"
    VALIDATION = "validation"
    LOCAL_COMPILATION = "local_compilation" # SOTA: Unit Testing del chunk
    GLOBAL_ASSEMBLY = "global_assembly"

class ChunkLifecycle(Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    REJECTED = "rejected"

class FailureType(Enum):
    NONE = "none"
    NORMALIZATION_FAILURE = "normalization_failure"
    SEMANTIC_VALIDATION_FAILURE = "semantic_validation_failure"
    LATEX_COMPILATION_FAILURE = "latex_compilation_failure"

@dataclass(frozen=True, slots=True)
class RecoveredJobSnapshot:
    """SOTA: Capa Anticorrupción. Representación agnóstica de la FSM aislada del pipeline."""
    document_id: str
    ast_hash: str
    state_value: str

@dataclass(frozen=True)
class ValidationError:
    code: str
    message: str
    severity: str = "error"

@dataclass(frozen=True)
class ChunkPayload:
    raw_response: str
    normalized_response: str = ""

@dataclass(frozen=True)
class ChunkExecutionEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    ast_hash: str = "" # <-- Nueva firma
    node_id: str = ""
    # ... (deja el resto igual)
    payload: ChunkPayload = field(default_factory=lambda: ChunkPayload(raw_response=""))
    
    lifecycle: ChunkLifecycle = ChunkLifecycle.PENDING
    failure_type: FailureType = FailureType.NONE
    processing_stage: ProcessingStage = ProcessingStage.GENERATION
    validation_errors: List[ValidationError] = field(default_factory=list)
    
    # SOTA: Provenance estricto
    prompt_hash: str = ""
    prompt_template_version: str = "v1.0"
    normalizer_version: str = "v1.1"
    validator_version: str = "v1.1"
    timestamp: float = field(default_factory=time.time)

    @property
    def content_hash(self) -> str:
        """SOTA: Idempotencia basada en estado algorítmico y contenido."""
        state = {
            "normalized": self.payload.normalized_response or self.payload.raw_response,
            "normalizer_v": self.normalizer_version,
            "validator_v": self.validator_version,
            "prompt_template_v": self.prompt_template_version
        }
        # sort_keys=True es obligatorio para evitar colisiones por ordenamiento de diccionarios
        base = json.dumps(state, sort_keys=True)
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    @property
    def is_assemblable(self) -> bool:
        return (self.lifecycle == ChunkLifecycle.PROCESSED and self.failure_type == FailureType.NONE)

@dataclass(frozen=True)
class ExecutionEnvelope:
    """
    NADR-F18-02 §5.1 R1, R3: Resource envelope con límites explícitos.
    Inmutable (frozen=True). Cualquier cambio requiere nueva instancia.
    """
    max_rss_mb: float
    task_timeout_sec: float
    max_concurrent_tasks: int = 1

    @classmethod
    def default_local(cls) -> "ExecutionEnvelope":
        """
        Default basado en HITO_0.7 baseline (peak single-process ~77MB).
        Margen 4x para absorber GC y picos sin OOM del OS.
        task_timeout_sec = 180s alinea con el timeout del SyncProviderBridge.
        """
        return cls(
            max_rss_mb=512.0,
            task_timeout_sec=180.0,
            max_concurrent_tasks=1,
        )