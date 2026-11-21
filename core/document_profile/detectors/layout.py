from typing import Final
from core.document_profile.models import ProfileInput, LayoutDetection, PageLayout
from core.document_profile.extractors import NodeGeometryExtractor

class HeuristicLayoutDetector:
    """
    SOTA: Inferencia de topología basada en bimodalidad espacial.
    """
    __slots__ = ("_geom_extractor",)

    _LEFT_CLUSTER_MAX: Final[float] = 0.40
    _RIGHT_CLUSTER_MIN: Final[float] = 0.60
    _CLUSTER_DENSITY_THRESHOLD: Final[float] = 0.25

    def __init__(self, geom_extractor: NodeGeometryExtractor):
        self._geom_extractor = geom_extractor

    def _compute_cluster_densities(self, total_nodes: int, left_mass: int, right_mass: int) -> tuple[float, float]:
        if total_nodes == 0:
            return 0.0, 0.0
        return (left_mass / total_nodes), (right_mass / total_nodes)

    def _compute_confidence(self, left_ratio: float, right_ratio: float, is_bimodal: bool) -> float:
        if is_bimodal:
            balance = min(left_ratio, right_ratio) * 2.0
            return min(balance, 1.0)
        return min(left_ratio + right_ratio, 1.0)

    def detect(self, input_data: ProfileInput) -> LayoutDetection:
        # La bimodalidad es una propiedad de cada página física:
        # bloques a la izquierda en una página y a la derecha en otra
        # no constituyen evidencia de doble columna en ninguna de ellas.
        page_counts: dict[int, list[int]] = {}
        for node in input_data.nodes:
            geom = self._geom_extractor.extract(node)
            if geom is None:
                continue
            counts = page_counts.setdefault(geom.page_number, [0, 0, 0])
            counts[0] += 1
            if geom.relative_center_x <= self._LEFT_CLUSTER_MAX:
                counts[1] += 1
            elif geom.relative_center_x >= self._RIGHT_CLUSTER_MIN:
                counts[2] += 1

        if not page_counts:
            return LayoutDetection(layout=PageLayout.UNKNOWN, confidence=0.0)

        per_page: list[LayoutDetection] = []
        for total, left_mass, right_mass in page_counts.values():
            left_ratio, right_ratio = self._compute_cluster_densities(
                total, left_mass, right_mass
            )
            is_bimodal = (
                left_ratio >= self._CLUSTER_DENSITY_THRESHOLD
                and right_ratio >= self._CLUSTER_DENSITY_THRESHOLD
            )
            per_page.append(
                LayoutDetection(
                    layout=(
                        PageLayout.DOUBLE_COLUMN
                        if is_bimodal else PageLayout.SINGLE_COLUMN
                    ),
                    confidence=self._compute_confidence(
                        left_ratio, right_ratio, is_bimodal
                    ),
                )
            )
        if len({finding.layout for finding in per_page}) != 1:
            # No existe MIXED en la taxonomía pública: declarar incertidumbre.
            return LayoutDetection(layout=PageLayout.UNKNOWN, confidence=0.0)
        return LayoutDetection(
            layout=per_page[0].layout,
            confidence=min(finding.confidence for finding in per_page),
        )
