from types import MappingProxyType
from typing import Hashable, Sequence

from core.ast.models import ASTNode
from tools.evaluation.topology.fingerprint import ASTFingerprintPolicy
from tools.evaluation.topology.models import ConfusionMatrix, MetricName, MetricResult
from tools.evaluation.topology.ports import TopologyMetric


class EntityRecallMetric(TopologyMetric):
    """Métrica hash-based O(n) de cobertura de recuperación por tipo de bloque semántico."""

    @property
    def name(self) -> MetricName:
        return MetricName.RECALL

    def evaluate(
        self,
        candidate: Sequence[ASTNode],
        ground_truth: Sequence[ASTNode]
    ) -> MetricResult:
        cand_fingerprints = [
            ASTFingerprintPolicy.semantic_fingerprint(node) for node in candidate
        ]
        gt_fingerprints = [
            ASTFingerprintPolicy.semantic_fingerprint(node) for node in ground_truth
        ]

        cand_counts: dict[Hashable, int] = {}
        for fp in cand_fingerprints:
            cand_counts[fp] = cand_counts.get(fp, 0) + 1

        gt_counts: dict[Hashable, int] = {}
        for fp in gt_fingerprints:
            gt_counts[fp] = gt_counts.get(fp, 0) + 1

        tp = 0
        for fp, count in cand_counts.items():
            if fp in gt_counts:
                tp += min(count, gt_counts[fp])

        fp_val = max(0, len(cand_fingerprints) - tp)
        fn_val = max(0, len(gt_fingerprints) - tp)

        cm = ConfusionMatrix(tp=tp, fp=fp_val, fn=fn_val)

        return MetricResult(
            metric_name=self.name,
            value=cm.f1_score,
            details=MappingProxyType({
                "true_positives": cm.tp,
                "false_positives": cm.fp,
                "false_negatives": cm.fn,
                "precision": cm.precision,
                "recall": cm.recall,
                "f1_score": cm.f1_score,
            })
        )