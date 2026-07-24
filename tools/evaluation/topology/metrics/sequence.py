from types import MappingProxyType
from typing import Hashable, Sequence

from core.ast.models import ASTNode
from tools.evaluation.topology.fingerprint import ASTFingerprintPolicy
from tools.evaluation.topology.models import MetricName, MetricResult
from tools.evaluation.topology.ports import TopologyMetric


class SequenceAlignmentMetric(TopologyMetric):
    """
    Métrica de fidelidad en la secuencia del orden de lectura mediante LCS.

    NOTA DE ARQUITECTURA:
    Esta implementación utiliza programación dinámica O(m * n) con matriz DP completa.
    Está destinada exclusivamente al corpus de calibración y benchmarking liviano.
    Para procesamiento de corpus masivos, debe sustituirse por el algoritmo de Hirschberg.
    """

    @property
    def name(self) -> MetricName:
        return MetricName.SEQUENCE

    def evaluate(
        self,
        candidate: Sequence[ASTNode],
        ground_truth: Sequence[ASTNode]
    ) -> MetricResult:
        cand_seq = [
            ASTFingerprintPolicy.semantic_fingerprint(node) for node in candidate
        ]
        gt_seq = [
            ASTFingerprintPolicy.semantic_fingerprint(node) for node in ground_truth
        ]

        lcs_length = self._lcs_length(cand_seq, gt_seq)
        total_nodes = len(cand_seq) + len(gt_seq)

        score = (2.0 * lcs_length) / total_nodes if total_nodes > 0 else 1.0

        return MetricResult(
            metric_name=self.name,
            value=score,
            details=MappingProxyType({
                "lcs_length": lcs_length,
                "candidate_length": len(cand_seq),
                "ground_truth_length": len(gt_seq),
            })
        )

    @staticmethod
    def _lcs_length(seq1: Sequence[Hashable], seq2: Sequence[Hashable]) -> int:
        m, n = len(seq1), len(seq2)
        if m == 0 or n == 0:
            return 0

        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]