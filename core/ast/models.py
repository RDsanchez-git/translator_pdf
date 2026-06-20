from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union, Tuple, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections import Counter

# =====================================================================
# FAMILIA 1: NODOS ESTRUCTURALES (Contenedores lógicos / Layout)
# =====================================================================
class StructuralNodeType(str, Enum):
    DOCUMENT = "document"
    PART = "part"
    CHAPTER = "chapter"
    SECTION = "section"
    SUBSECTION = "subsection"

# =====================================================================
# FAMILIA 2: NODOS SEMÁNTICOS (Payloads de contenido / Traducibles)
# =====================================================================
class ContentNodeType(str, Enum):
    # Texto
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    
    # STEM
    EQUATION = "equation"
    INLINE_EQUATION = "inline_equation"
    TABLE = "table"
    FIGURE = "figure"
    IMAGE = "image"
    CAPTION = "caption"
    ALGORITHM = "algorithm"
    CODE_BLOCK = "code_block"
    
    # Académico
    FOOTNOTE = "footnote"
    CITATION = "citation"
    REFERENCE_ENTRY = "reference_entry"
    BIBLIOGRAPHY = "bibliography"
    APPENDIX = "appendix"
    
    # Recuperación (SOTA Fallbacks)
    MACRO_CHUNK = "macro_chunk"
    COMPOSITE_BLOCK = "composite_block"
    UNKNOWN = "unknown"

# =====================================================================
# FAMILIA 3: NODOS 
# =====================================================================

class TranslationTaskType(str, Enum):
    TRANSLATE = "translate"
    PRESERVE = "preserve"
    PARTIAL = "partial_translate"

class OverflowPolicy(str, Enum):
    BY_SENTENCE = "by_sentence"
    BY_PARAGRAPH = "by_paragraph"
    HARD_TRUNCATE = "hard_truncate"

# Tipo compuesto para flexibilidad en tipado estático
NodeType = Union[StructuralNodeType, ContentNodeType]

class ASTNode(BaseModel):
    node_id: str
    sequence_id: int = -1  # Control de evolución del esquema
    type: NodeType
    content: Optional[str] = None  
    latex: Optional[str] = None
    status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parent_id: Optional[str] = None
    control_plane: Dict[str, Any] = Field(default_factory=dict) 

    @property
    def has_valid_sequence(self) -> bool:
        """Garantiza que el nodo posee un índice topológico real en base 1."""
        return self.sequence_id >= 1


# SEMANTIC PACKAGING LAYER ---

class TokenEstimator(ABC):
    """SOTA: Interfaz base para inyección de dependencias del tokenizador."""
    @abstractmethod
    def estimate(self, text: str) -> int:
        pass

class FastWordEstimator(TokenEstimator):
    """Fallback heurístico ultra-rápido si el tokenizador nativo no está disponible."""
    def estimate(self, text: str) -> int:
        if not text:
            return 0
        return int(len(text.split()) * 1.3)
    

@dataclass(frozen=True)
class TranslationUnit:
    """Contrato inmutable, determinista e independiente del proveedor LLM."""
    chunk_index: int
    chunk_id: str
    chunk_fingerprint: str          # SOTA: Hash de (start_seq, end_seq) para reanudación resiliente
    chunk_type: TranslationTaskType
    source_sequence_range: Tuple[int, int]
    node_count: int
    context_id: str
    context_depth: int              # Profundidad en el árbol lógico (ej. 3 para H3)
    target_payload: str
    estimated_tokens: int
    payload_sha256: str

@dataclass
class ChunkingReport:
    """Auditoría de ejecución del chunker para la telemetría global."""
    total_groups: int = 0
    total_chunks: int = 0
    average_chunk_tokens: int = 0
    max_chunk_tokens: int = 0
    context_switches: int = 0
    overflow_events: int = 0

@dataclass(frozen=True)
class TranslatedUnit:
    """SOTA: Contrato inmutable de salida de la capa de ejecución distribuida (Fase 10C)."""
    chunk_index: int
    chunk_id: str
    chunk_type: str
    source_sequence_range: Tuple[int, int]
    translated_payload: str
    payload_sha256: str
    model_name: str
    prompt_version: str                     # Corrección 5: Trazabilidad inmutable para Cache Key
    input_tokens: int
    output_tokens: int
    latency_ms: float

@dataclass(frozen=True)
class ReconstructedDocument:
    """SOTA: DTO final inmutable que encapsula el documento ensamblado y su telemetría base."""
    content: str
    total_chunks: int
    translated_chunks: int
    passthrough_chunks: int
    total_input_tokens: int
    total_output_tokens: int


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

class FailureReason(str, Enum):
    CONTEXT_OVERFLOW = "context_overflow"
    PROVIDER_FAILURE = "provider_failure"
    VALIDATION_FAILURE = "validation_failure"
    RETRY_EXHAUSTED = "retry_exhausted"               # Corrección: Causa de negocio, no mecanismo
    UNHANDLED_WORKER_CRASH = "unhandled_worker_crash" # SOTA: Red de seguridad

@dataclass(frozen=True)
class ChunkOutcome:
    chunk_index: int
    chunk_id: str
    status: ExecutionStatus
    original_payload_sha256: str                      # SOTA: O(1) memory footprint
    translated_unit: Optional["TranslatedUnit"] = None
    failure_reason: Optional[FailureReason] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """SOTA: Invariante fuerte. Imposibilita estados contradictorios."""
        if self.status == ExecutionStatus.SUCCESS and self.translated_unit is None:
            raise ValueError("Invariante Roto: SUCCESS requiere un translated_unit válido.")

    @property
    def is_success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS

@dataclass(frozen=True)
class DispatchResult:
    outcomes: List[ChunkOutcome]
    
    @property
    def total_processed(self) -> int:
        return len(self.outcomes)
        
    @property
    def total_failed(self) -> int:
        return sum(1 for o in self.outcomes if not o.is_success)

    @property
    def success_rate(self) -> float:
        if not self.outcomes:
            return 0.0
        return (self.total_processed - self.total_failed) / self.total_processed

    @property
    def failed_by_reason(self) -> Dict[str, int]:
        """SOTA: Taxonomía de fallos empaquetada lista para métricas prometheus/datadog."""
        counts = Counter(
            o.failure_reason.value for o in self.outcomes 
            if not o.is_success and o.failure_reason
        )
        return dict(counts)


@dataclass(frozen=True, slots=True)
class OriginalChunk:
    """SOTA: DTO de hidratación segura para el Assembler."""
    chunk_id: str
    payload: str
    payload_sha256: str

class DispatchAnalytics:
    """SOTA: Separación de Responsabilidades (SRP). Motor de cálculo FinOps/SRE."""
    
    @staticmethod
    def calculate_success_rate(result: 'DispatchResult') -> float:
        if not result.outcomes:
            return 0.0
        return (result.total_processed - result.total_failed) / result.total_processed

    @staticmethod
    def aggregate_failures(result: 'DispatchResult') -> Dict[str, int]:
        counts = Counter(
            o.failure_reason.value for o in result.outcomes 
            if not o.is_success and o.failure_reason
        )
        return dict(counts)