"""Infraestructura de perfilado con proveniencia física verificable (PPPR G2)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite

from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.document_profile.extractors import NodeGeometry
from core.document_profile.models import SamplingCoverage, SamplingReport
from core.document_profile.ports import ProfileSamplingPolicy, ReportingSamplingPolicy


@dataclass(frozen=True, slots=True)
class _NodeGeometryDTO:
    center_x: float
    relative_center_x: float
    page_number: int


class NodeGeometryAdapter:
    """Solo calcula geometría sobre una región física acreditada.

    BBoxes de listas paralelas antiguas y anchos supuestos NO acreditan
    correspondencia de página, ni se agregan regiones multipágina sin política.
    """

    def extract(self, node: ASTNode) -> NodeGeometry | None:
        regions = node.metadata.physical_regions
        if len(regions) != 1:
            return None
        region = regions[0]
        bbox = region.bbox
        if bbox is None:
            return None

        center_x = bbox.center_x
        if not isfinite(center_x):
            return None

        if bbox.is_normalized:
            if not (0 <= bbox.x0 < bbox.x1 <= 1):
                return None
            relative_center_x = center_x
        else:
            width = region.page_width
            if width is None or not isfinite(width) or width <= 0:
                return None
            if bbox.x0 < 0 or bbox.x1 > width:
                return None
            relative_center_x = center_x / width

        return _NodeGeometryDTO(
            center_x=center_x,
            relative_center_x=relative_center_x,
            page_number=region.page_number,
        )


class NodeSemanticAdapter:
    """Proyección semántica a la taxonomía canónica del AST."""

    def kind(self, node: ASTNode) -> ContentNodeType | None:
        node_type = node.node_type
        if isinstance(node_type, ContentNodeType):
            return node_type
        if isinstance(node_type, str):
            try:
                return ContentNodeType(node_type)
            except ValueError:
                return None
        return None


class FirstPagesSamplingPolicy:
    """Primeras N páginas FÍSICAS, no primeras N páginas observadas.

    Si un nodo cruza la frontera, se descarta íntegro y se marca PARTIAL.
    Si no hay vinculación física acreditada, no se lo asigna a página 0:
    se omite y se registra INDETERMINATE. La salida de sample() mantiene
    el contrato Sequence anterior; sample_with_report() expone el límite.
    """

    __slots__ = ("_geom_extractor", "_max_pages")

    def __init__(self, geom_extractor: NodeGeometryAdapter, max_pages: int):
        if max_pages < 1:
            raise ValueError("PROFILER_MAX_SAMPLING_PAGES debe ser >= 1")
        self._geom_extractor = geom_extractor
        self._max_pages = max_pages

    def sample_with_report(self, nodes: Sequence[ASTNode]) -> SamplingReport:
        selected: list[ASTNode] = []
        reasons: list[str] = []
        has_unknown = False
        has_partial = False

        for node in nodes:
            regions = node.metadata.physical_regions
            if not regions:
                has_unknown = True
                reasons.append(f"{node.node_id}:UNVERIFIED_PHYSICAL_PROVENANCE")
                continue

            documents = {r.source_document for r in regions}
            if len(documents) != 1:
                has_unknown = True
                reasons.append(f"{node.node_id}:MIXED_SOURCE_DOCUMENTS")
                continue

            page_numbers = {r.page_number for r in regions}
            inside = any(p <= self._max_pages for p in page_numbers)
            outside = any(p > self._max_pages for p in page_numbers)
            if inside and outside:
                has_partial = True
                reasons.append(f"{node.node_id}:CROSS_BOUNDARY_CONTENT_OMITTED")
                continue
            if inside:
                selected.append(node)
            # only outside: legitimately excluded from the first N pages

        coverage = (
            SamplingCoverage.INDETERMINATE if has_unknown else
            SamplingCoverage.PARTIAL if has_partial else
            SamplingCoverage.STRICT_SCOPE
        )
        return SamplingReport(
            nodes=tuple(selected),
            coverage=coverage,
            reasons=tuple(reasons),
        )

    def sample(self, nodes: Sequence[ASTNode]) -> Sequence[ASTNode]:
        return self.sample_with_report(nodes).nodes


# Comprobación estática de interfaces, sin instanciar adaptadores inválidos.
_geometry_port: type[NodeGeometryAdapter] = NodeGeometryAdapter
_sampling_port: type[FirstPagesSamplingPolicy] = FirstPagesSamplingPolicy
