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
        total_valid = 0
        left_mass = 0
        right_mass = 0

        for node in input_data.nodes:
            geom = self._geom_extractor.extract(node)
            if not geom:
                continue

            total_valid += 1
            if geom.relative_center_x <= self._LEFT_CLUSTER_MAX:
                left_mass += 1
            elif geom.relative_center_x >= self._RIGHT_CLUSTER_MIN:
                right_mass += 1

        if total_valid == 0:
            return LayoutDetection(layout=PageLayout.UNKNOWN, confidence=0.0)

        left_ratio, right_ratio = self._compute_cluster_densities(total_valid, left_mass, right_mass)
        
        is_bimodal = (left_ratio >= self._CLUSTER_DENSITY_THRESHOLD and 
                      right_ratio >= self._CLUSTER_DENSITY_THRESHOLD)

        layout_type = PageLayout.DOUBLE_COLUMN if is_bimodal else PageLayout.SINGLE_COLUMN
        confidence = self._compute_confidence(left_ratio, right_ratio, is_bimodal)

        return LayoutDetection(layout=layout_type, confidence=confidence)