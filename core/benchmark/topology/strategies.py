from typing import Sequence
from core.ast.models import ASTNode
from core.benchmark.topology.ports import EvaluationStrategy, TopologicalEvaluatorProtocol, ScoreAggregationPolicy
from core.benchmark.topology.models import TopologicalEvaluationReport, MetricScoreDTO

class ParserEvaluationStrategy(EvaluationStrategy):
    """
    Orquestador perimetral de evaluación de parsers. 
    Aplica composición pura sobre colecciones ordenadas e inmutables.
    """
    def __init__(
        self, 
        evaluators: Sequence[TopologicalEvaluatorProtocol],
        aggregator: ScoreAggregationPolicy
    ):
        self._evaluators = evaluators
        self._aggregator = aggregator

    def evaluate_run(
        self, 
        document_id: str, 
        candidate_ast: Sequence[ASTNode], 
        ground_truth_ast: Sequence[ASTNode]
    ) -> TopologicalEvaluationReport:
        computed_metrics: list[MetricScoreDTO] = []
        
        # 1. Evaluación en flujo continuo delegada a la colección de micro-jueces
        for evaluator in self._evaluators:
            score_dto = evaluator.evaluate(candidate_ast, ground_truth_ast)
            computed_metrics.append(score_dto)
            
        # 2. Unificación externa del score global vía política inyectada
        final_score = self._aggregator.aggregate(computed_metrics)
        
        return TopologicalEvaluationReport(
            document_id=document_id,
            metrics=tuple(computed_metrics),
            overall_score=final_score
        )