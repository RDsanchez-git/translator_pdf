# FILE: core/benchmark/topology/evaluators/recall.py

from typing import Sequence
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.benchmark.topology.ports import TopologicalEvaluatorProtocol, NodeMatchingPolicy
from core.benchmark.topology.models import MetricScoreDTO, ConfusionMatrix, MatchingKey


class EntityRecallEvaluator(TopologicalEvaluatorProtocol):
    """
    Micro-juez de recuperación estructural.
    
    COMPLEJIDAD ASINTÓTICA:
    - Tiempo lineal esperado O(n) condicionado a la entropía de la clave del dominio.
    """
    def __init__(
        self,
        target_type: ContentNodeType,
        matching_policy: NodeMatchingPolicy
    ):
        self._target_type = target_type
        self._matching_policy = matching_policy

    @property
    def metric_name(self) -> str:
        return f"f1_score_{self._target_type.value.lower()}"

    def evaluate(
        self, 
        candidate_ast: Sequence[ASTNode],
        ground_truth_ast: Sequence[ASTNode]
    ) -> MetricScoreDTO:
        # 1. Filtrado selectivo en O(n)
        candidates = [n for n in candidate_ast if n.node_type == self._target_type]
        gts = [n for n in ground_truth_ast if n.node_type == self._target_type]

        if not candidates and not gts:
            matrix = ConfusionMatrix(true_positives=0, false_positives=0, false_negatives=0)
            return self._build_dto(matrix)

        # 2. Indexación asintótica utilizando el Value Object MatchingKey como hash
        gt_buckets: dict[MatchingKey, list[ASTNode]] = {}
        for gt_node in gts:
            key = self._matching_policy.matching_key(gt_node)
            gt_buckets.setdefault(key, []).append(gt_node)

        # Registro de exclusión gobernado por la firma lógica de la política, no por el AST
        consumed_gt_uids: set[str] = set()
        tp = 0

        # 3. Consumo de buckets protegiendo la complejidad lineal esperada
        for c_node in candidates:
            key = self._matching_policy.matching_key(c_node)
            if key in gt_buckets:
                for gt_candidate in gt_buckets[key]:
                    gt_uid = self._matching_policy.unique_identifier(gt_candidate)
                    if gt_uid in consumed_gt_uids:
                        continue
                    if self._matching_policy.match(c_node, gt_candidate):
                        consumed_gt_uids.add(gt_uid)
                        tp += 1
                        break

        fp = len(candidates) - tp
        fn = len(gts) - tp

        matrix = ConfusionMatrix(true_positives=tp, false_positives=fp, false_negatives=fn)
        return self._build_dto(matrix)

    def _build_dto(self, matrix: ConfusionMatrix) -> MetricScoreDTO:
        return MetricScoreDTO(
            metric_name=self.metric_name,
            primary_score=matrix.f1_score,
            diagnostics=matrix.to_diagnostics()
        )