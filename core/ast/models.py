from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Dict, Any, Optional, Union, Tuple, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections import Counter
from core.domain.document import BoundingBox
from core.ast.enums import ContentNodeType, TranslationStrategy, HeadingLevel, SemanticOrigin

# =====================================================================
# FAMILIA 1 Y 2: AST V2 COMPOSITION (Estructura Plana y Payloads Tipados)
# =====================================================================

class NodeMetadata(BaseModel):
    """Value Object inmutable que encapsula el linaje físico y dimensional."""
    model_config = ConfigDict(frozen=True)
    
    bboxes: List[BoundingBox] = Field(default_factory=list)
    pages: List[int] = Field(default_factory=list)
    provider_native_id: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    layout_reading_order: int = -1
    semantic_origin: SemanticOrigin = SemanticOrigin.PDF_TEXT

# --- DEFINICIÓN DE PAYLOADS COMPONENTES (DTOs DE VALOR INMUTABLES) ---

class HeadingPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    content: str
    heading_level: HeadingLevel = HeadingLevel.UNKNOWN

    def with_content(self, new_content: str) -> "HeadingPayload":
        return self.model_copy(update={"content": new_content})

class ParagraphPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    content: str

    def with_content(self, new_content: str) -> "ParagraphPayload":
        return self.model_copy(update={"content": new_content})

class MathPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    content: str

    def with_content(self, new_content: str) -> "MathPayload":
        return self.model_copy(update={"content": new_content})

class CodePayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    content: str
    language: Optional[str] = None

    def with_content(self, new_content: str) -> "CodePayload":
        return self.model_copy(update={"content": new_content})

class TablePayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    content: str

    def with_content(self, new_content: str) -> "TablePayload":
        return self.model_copy(update={"content": new_content})

class ImagePayload(BaseModel):
    """Nodo no combinable por invariante trans-página."""
    model_config = ConfigDict(frozen=True)
    alt_text: Optional[str] = None
    asset_path: Optional[str] = None

class ListPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    content: str

    def with_content(self, new_content: str) -> "ListPayload":
        return self.model_copy(update={"content": new_content})

ASTPayload = Union[
    HeadingPayload,
    ParagraphPayload,
    MathPayload,
    CodePayload,
    TablePayload,
    ImagePayload,
    ListPayload
]

class ASTNode(BaseModel):
    """SOTA: Contenedor unificado e inmutable. Resuelve la ambigüedad posicional de Pydantic."""
    model_config = ConfigDict(frozen=True)

    node_id: str
    sequence_id: int = -1
    node_type: ContentNodeType
    strategy: TranslationStrategy = TranslationStrategy.TRANSLATE
    metadata: NodeMetadata = Field(default_factory=lambda: NodeMetadata())
    depth: int = 0
    payload: ASTPayload
    
    # Preservado estrictamente para retrocompatibilidad con la capa de Workers/Dispatcher
    control_plane: Dict[str, Any] = Field(default_factory=dict)

    parent_node_id: Optional[str] = None
    # segment_index = 0 implica "Nodo intacto / original". Índices 1+ implican fragmentación.
    segment_index: int = 0
    # segment_count prepara el terreno para la validación O(1) de la Fase 16.6.
    segment_count: int = 1


    def spawn_fragment(self, new_id: str, new_payload: 'ASTPayload', segment_index: int) -> 'ASTNode':
        """SOTA: Encapsula la lógica de clonación estructural (Information Hiding).
        Aísla a los consumidores de conocer la API subyacente del DTO (Pydantic)."""
        return self.model_copy(update={
            "node_id": new_id,
            "payload": new_payload,
            "parent_node_id": self.node_id,
            "segment_index": segment_index
        })

    @property
    def has_valid_sequence(self) -> bool:
        """Garantiza que el nodo posee un índice topológico real en base 1."""
        return self.sequence_id >= 1

    @model_validator(mode="before")
    @classmethod
    def _discriminate_payload(cls, values: Any) -> Any:
        """Garantiza la correcta instanciación del DTO de payload según el tipo de nodo, 
        neutralizando por completo el Type Erasure estructural de Pydantic V2."""
        if not isinstance(values, dict):
            return values
        
        n_type = values.get("node_type")
        payload_data = values.get("payload")
        
        if n_type is None or payload_data is None:
            return values
            
        if isinstance(payload_data, (HeadingPayload, ParagraphPayload, MathPayload, CodePayload, TablePayload, ImagePayload, ListPayload)):
            return values

        type_mapping = {
            ContentNodeType.HEADING: HeadingPayload,
            ContentNodeType.PARAGRAPH: ParagraphPayload,
            ContentNodeType.DISPLAY_EQUATION: MathPayload,
            ContentNodeType.INLINE_EQUATION: MathPayload,
            ContentNodeType.CODE: CodePayload,
            ContentNodeType.TABLE_SIMPLE: TablePayload,
            ContentNodeType.TABLE_COMPLEX: TablePayload,
            ContentNodeType.IMAGE: ImagePayload,
            ContentNodeType.CAPTION: ParagraphPayload,
            ContentNodeType.LIST: ListPayload,
        }

        if isinstance(payload_data, str):
            if n_type == ContentNodeType.HEADING:
                values["payload"] = HeadingPayload(content=payload_data)
            elif n_type == ContentNodeType.IMAGE:
                values["payload"] = ImagePayload(asset_path=payload_data)
            else:
                target_model = type_mapping.get(n_type)
                if target_model:
                    values["payload"] = target_model(content=payload_data)
        elif isinstance(payload_data, dict):
            target_model = type_mapping.get(n_type)
            if target_model:
                values["payload"] = target_model(**payload_data)
            
        return values


    @property
    def text_content(self) -> str:
        """SOTA: Extracción polimórfica segura. Aisla al sistema del DTO subyacente."""
        return getattr(self.payload, "content", "")

    def with_strategy(self, new_strategy: TranslationStrategy) -> "ASTNode":
        """Syntactic sugar inmutable para la transición de estados en el pipeline."""
        if self.strategy == new_strategy:
            return self
        return self.model_copy(update={"strategy": new_strategy})

    def with_sequence_id(self, new_seq: int) -> 'ASTNode':
        """SOTA: Reasignación inmutable del orden lógico sin exponer la infraestructura."""
        return self.model_copy(update={"sequence_id": new_seq})
    
# =====================================================================
# FAMILIA 3: INFRAESTRUCTURA DE EJECUCIÓN, CHUNKING Y TELEMETRÍA
# =====================================================================

class TranslationTaskType(str, Enum):
    TRANSLATE = "translate"
    PRESERVE = "preserve"
    PARTIAL = "partial_translate"

class OverflowPolicy(str, Enum):
    BY_SENTENCE = "by_sentence"
    BY_PARAGRAPH = "by_paragraph"
    HARD_TRUNCATE = "hard_truncate"

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

    def estimate_tokens(self, text: str) -> int:
        return int(self.estimate(text))

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
    prompt_version: str                     # Trazabilidad inmutable para Cache Key
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
    RETRY_EXHAUSTED = "retry_exhausted"
    UNHANDLED_WORKER_CRASH = "unhandled_worker_crash"
    UNKNOWN_ERROR = "unknown_error"
    UNPROCESSABLE_ENTITY = "unprocessable_entity"
    CIRCUIT_OPEN = "circuit_open"
    QUOTA_REJECTION = "quota_rejection"
    QUOTA_TIMEOUT = "quota_timeout"

@dataclass(frozen=True)
class ChunkOutcome:
    chunk_index: int
    chunk_id: str
    status: ExecutionStatus
    original_payload_sha256: str
    translated_unit: Optional[TranslatedUnit]
    failure_reason: Optional[FailureReason]
    error_message: Optional[str]
    telemetry: Optional[dict] = None

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

class ExecutionRoute(str, Enum):
    """SOTA: Trazabilidad tipada del enrutamiento de inferencia."""
    PRIMARY = "primary"
    FALLBACK = "fallback"
    BYPASS = "bypass"

class ExecutionStage(str, Enum):
    PRE_NETWORK = "pre_network"
    NETWORK = "network"
    POST_NETWORK = "post_network"


