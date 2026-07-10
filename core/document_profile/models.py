from enum import StrEnum
from dataclasses import dataclass
from collections.abc import Sequence

from core.ast.models import ASTNode
from core.domain.document import DocumentType

class PageLayout(StrEnum):
    """Taxonomía de topología física inferida."""
    SINGLE_COLUMN = "single_column"
    DOUBLE_COLUMN = "double_column"
    # MULTI_COLUMN removido: El algoritmo MVP no lo emite. Evitamos estados imposibles.
    UNKNOWN = "unknown" 
    # UNKNOWN significa: 
    # - Muestra sin bloques espaciales (geometría insuficiente)
    # - Extractor geométrico no disponible o fallido
    # - Confianza matemática 0.0

@dataclass(slots=True, frozen=True)
class ProfileInput:
    nodes: Sequence[ASTNode]

@dataclass(slots=True, frozen=True)
class LayoutDetection:
    layout: PageLayout
    confidence: float

@dataclass(slots=True, frozen=True)
class TypeDetection:
    document_type: DocumentType | None
    confidence: float

@dataclass(slots=True, frozen=True)
class InferredDocumentProfile:
    layout: PageLayout
    document_type: DocumentType | None

@dataclass(slots=True, frozen=True)
class ProfileDiagnostics:
    layout_confidence: float
    type_confidence: float

@dataclass(slots=True, frozen=True)
class ProfilingResult:
    profile: InferredDocumentProfile
    diagnostics: ProfileDiagnostics