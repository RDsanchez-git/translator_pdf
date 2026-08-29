from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Dict, Any, Optional, Union, Tuple, List, cast
from dataclasses import dataclass
from collections import Counter
from core.domain.document import BoundingBox
from core.ast.enums import ContentNodeType, TranslationStrategy, HeadingLevel, SemanticOrigin
from core.shared.identity_contracts import NodeId

# =====================================================================
# FAMILIA 1 Y 2: AST V2 COMPOSITION (Estructura Plana y Payloads Tipados)
# =====================================================================
class NodeMetadata(BaseModel):
    """Value Object inmutable que encapsula el linaje físico y dimensional."""
    model_config = ConfigDict(frozen=True)
    
    # SOTA FIX: Se sustituye la factoría genérica 'list' por lambdas evaluadas 
    # bajo el contexto de tipado de Pyright para evitar 'list[Unknown]'
    bboxes: List[BoundingBox] = Field(default_factory=lambda: [])
    pages: List[int] = Field(default_factory=lambda: [])
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
    """Contenedor unificado e inmutable del AST V2.

    CONTRATO DE DOMINIO (NADR-F17BIS-17 §5.1, Task 2.2.1/2.2.3 Fase 3):

    node_id:
        - Identidad lógica estable del nodo dentro del AST.
        - DOMINIO: cualquier string no vacío que NO contenga el carácter ':'.
        - PROHIBIDO: ':' (delimitador de campo en el framing criptográfico
          de OracleSemanticIdentityCalculator).
        - JUSTIFICACIÓN: garantizar inyectividad del encoding. El oracle_hash
          usa un framing determinista donde node_id participa como dimensión
          de identidad semántica. Si node_id pudiera contener ':', dos payloads
          distintos podrían producir representaciones ambiguas antes del hash.
        - VALIDACIÓN: fail-fast en construcción vía NodeId
          (core/shared/identity_contracts.py).
        - SENTINEL: no aplica (node_id es obligatorio).

    parent_node_id:
        - Referencia al node_id del nodo padre (para fragmentos).
        - Mismo contrato de dominio que node_id (Optional[NodeId]).
        - None para nodos raíz o no fragmentados.
        - JUSTIFICACIÓN: consistencia de dominio. Si node_id no puede contener
          ':', ninguna referencia a un node_id debería poder contenerlo.

    Nota SOTA:
        Los métodos que crean nuevos ASTNode con node_id actualizado deben pasar
        por el constructor validado. En particular, spawn_fragment() NO usa
        model_copy(update={"node_id": ...}) porque Pydantic v2 no revalida los
        campos actualizados en model_copy().
    """

    model_config = ConfigDict(frozen=True)
    node_id: NodeId
    sequence_id: int = -1
    node_type: ContentNodeType
    strategy: TranslationStrategy = TranslationStrategy.TRANSLATE
    metadata: NodeMetadata = Field(default_factory=lambda: NodeMetadata())
    depth: int = 0
    payload: ASTPayload

    control_plane: Dict[str, Any] = Field(default_factory=dict)
    parent_node_id: Optional[NodeId] = None
    segment_index: int = 0
    segment_count: int = 1

    def spawn_fragment(self, new_id: str, new_payload: "ASTPayload", segment_index: int) -> "ASTNode":
        """Crea un fragmento hijo validando explícitamente el nuevo node_id.

        Importante: NO usar model_copy(update={"node_id": new_id}).
        En Pydantic v2, model_copy(update=...) no revalida los campos,
        por lo que permitiría saltarse el contrato NodeId. Usamos el
        constructor completo para preservar fail-fast.
        """
        return ASTNode(
            node_id=new_id,
            sequence_id=self.sequence_id,
            node_type=self.node_type,
            strategy=self.strategy,
            metadata=self.metadata,
            depth=self.depth,
            payload=new_payload,
            control_plane=dict(self.control_plane),
            parent_node_id=self.node_id,
            segment_index=segment_index,
            segment_count=self.segment_count,
        )

    @property
    def has_valid_sequence(self) -> bool:
        return self.sequence_id >= 1

    @model_validator(mode="before")
    @classmethod
    def _discriminate_payload(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values

        # SOTA FIX: Forzado estricto en tiempo de análisis estático mediante cast.
        # Destruye el rastro de dict[Unknown, Unknown] generado por el Type Guard.
        v_dict = cast(Dict[str, Any], values)
        n_type: Optional[ContentNodeType] = v_dict.get("node_type")
        payload_data: Any = v_dict.get("payload")

        if n_type is None or payload_data is None:
            return v_dict

        if isinstance(
            payload_data,
            (
                HeadingPayload,
                ParagraphPayload,
                MathPayload,
                CodePayload,
                TablePayload,
                ImagePayload,
                ListPayload,
            ),
        ):
            return v_dict

        type_mapping: Dict[ContentNodeType, Any] = {
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
                v_dict["payload"] = HeadingPayload(content=payload_data)
            elif n_type == ContentNodeType.IMAGE:
                v_dict["payload"] = ImagePayload(asset_path=payload_data)
            else:
                target_model = type_mapping.get(n_type)
                if target_model:
                    v_dict["payload"] = target_model(content=payload_data)
        elif isinstance(payload_data, dict):
            target_model = type_mapping.get(n_type)
            if target_model:
                v_dict["payload"] = target_model(**payload_data)

        return v_dict

    @property
    def text_content(self) -> str:
        return getattr(self.payload, "content", "")

    def with_strategy(self, new_strategy: TranslationStrategy) -> "ASTNode":
        if self.strategy == new_strategy:
            return self
        return self.model_copy(update={"strategy": new_strategy})

    def with_sequence_id(self, new_seq: int) -> "ASTNode":
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

@dataclass(frozen=True)
class TranslationUnit:
    chunk_index: int
    chunk_id: str
    chunk_fingerprint: str
    chunk_type: TranslationTaskType
    source_sequence_range: Tuple[int, int]
    node_count: int
    context_id: str
    context_depth: int
    target_payload: str
    estimated_tokens: int
    payload_sha256: str

@dataclass
class ChunkingReport:
    total_groups: int = 0
    total_chunks: int = 0
    average_chunk_tokens: int = 0
    max_chunk_tokens: int = 0
    context_switches: int = 0
    overflow_events: int = 0

@dataclass(frozen=True)
class TranslatedUnit:
    chunk_index: int
    chunk_id: str
    chunk_type: str
    source_sequence_range: Tuple[int, int]
    translated_payload: str
    payload_sha256: str
    model_name: str
    prompt_version: str
    input_tokens: int
    output_tokens: int
    latency_ms: float

@dataclass(frozen=True)
class ReconstructedDocument:
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
    # SOTA FIX: Bloqueo explícito de 'dict[Unknown, Unknown]' en el DTO raíz
    telemetry: Optional[Dict[str, Any]] = None

    def __post_init__(self):
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
        counts = Counter(
            o.failure_reason.value for o in self.outcomes 
            if not o.is_success and o.failure_reason
        )
        # SOTA FIX: Comprehension para satisfacer estrictamente Dict[str, int]
        return {str(k): int(v) for k, v in counts.items()}

@dataclass(frozen=True, slots=True)
class OriginalChunk:
    chunk_id: str
    payload: str
    payload_sha256: str

class DispatchAnalytics:
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
        # SOTA FIX: Prevención de reportMissingTypeArgument en factoría genérica
        return {str(k): int(v) for k, v in counts.items()}

class ExecutionRoute(str, Enum):
    PRIMARY = "primary"
    FALLBACK = "fallback"
    BYPASS = "bypass"

class ExecutionStage(str, Enum):
    PRE_NETWORK = "pre_network"
    NETWORK = "network"
    POST_NETWORK = "post_network"