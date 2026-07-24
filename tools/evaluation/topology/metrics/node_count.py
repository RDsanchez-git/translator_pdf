from types import MappingProxyType
from typing import Sequence

from core.ast.models import ASTNode
from tools.evaluation.topology.models import MetricName, MetricResult
from tools.evaluation.topology.ports import TopologyMetric


class NodeCountMetric(TopologyMetric):
    """Métrica O(1) de verificación rápida (sanity check) para volumen de nodos."""

    @property
    def name(self) -> MetricName:
        return MetricName.NODE_COUNT

    def evaluate(
        self,
        candidate: Sequence[ASTNode],
        ground_truth: Sequence[ASTNode]
    ) -> MetricResult:
        cand_len = len(candidate)
        gt_len = len(ground_truth)
        max_len = max(cand_len, gt_len)

        if max_len == 0:
            score = 1.0
            diff = 0
        else:
            diff = abs(cand_len - gt_len)
            score = max(0.0, 1.0 - (diff / max_len))

        return MetricResult(
            metric_name=self.name,
            value=score,
            details=MappingProxyType({
                "candidate_nodes": cand_len,
                "ground_truth_nodes": gt_len,
                "absolute_difference": diff,
            })
        )