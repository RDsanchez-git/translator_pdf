from __future__ import annotations

from enum import StrEnum
from dataclasses import dataclass
from collections.abc import Sequence

from core.ast.models import ASTNode
from core.domain.document import DocumentType

class SamplingCoverage(StrEnum):
    """Alcance de la muestra; no certifica la cobertura íntegra del PDF."""
    STRICT_SCOPE = "STRICT_SCOPE"
    PARTIAL = "PARTIAL"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True, slots=True)
class SamplingReport:
    nodes: Sequence[ASTNode]
    coverage: SamplingCoverage
    reasons: tuple[str, ...] = ()
    geometry_reasons: tuple[str, ...] = ()


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
    # None: registro legado; su evidencia física NO está acreditada.
    physical_diagnostics: ProfileDiagnostics | None = None

@dataclass(slots=True, frozen=True)
class ProfileDiagnostics:
    layout_confidence: float
    type_confidence: float
    sampling_coverage: SamplingCoverage = SamplingCoverage.INDETERMINATE
    sampling_reasons: tuple[str, ...] = ()
    geometry_reasons: tuple[str, ...] = ()

@dataclass(slots=True, frozen=True)
class ProfilingResult:
    profile: InferredDocumentProfile
    diagnostics: ProfileDiagnostics