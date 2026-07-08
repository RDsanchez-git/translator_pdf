from enum import StrEnum
from dataclasses import dataclass
from core.ast.models import ASTNode

class BoundaryDecision(StrEnum):
    """Decisión semántica sobre la viabilidad de agrupar nodos consecutivos."""
    ALLOW = "ALLOW"
    HARD_BREAK = "HARD_BREAK"
    SOFT_BREAK = "SOFT_BREAK"

@dataclass(slots=True, frozen=True)
class ChunkMetadata:
    """Métricas y topología del bloque estructuradas para observabilidad en sumideros (ELK/Datadog)."""
    estimated_tokens: int
    node_count: int
    sequence_start: int
    sequence_end: int

@dataclass(slots=True, frozen=True)
class TranslationChunk:
    """
    Unidad de trabajo inmutable despachada al LLM.
    Invariante: Su creación respeta la Monotonicidad del Pipeline (zero mutation del ASTNode).
    """
    chunk_id: str
    nodes: tuple[ASTNode, ...]
    metadata: ChunkMetadata