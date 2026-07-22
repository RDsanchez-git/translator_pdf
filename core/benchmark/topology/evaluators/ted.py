from typing import Sequence
from core.ast.models import ASTNode
from core.benchmark.topology.ports import (
    TopologicalEvaluatorProtocol,
    AnchorAlignmentStrategy,
    AnchorPartitionStrategy,
    TreeEditEngine,
    OverflowStrategy,
    NormalizationPolicy,
    TreeEditCostContext
)
from core.benchmark.topology.models import (
    MetricScoreDTO, 
    TedDiagnostics, 
    NormalizationInput, 
    TEDEvaluationContext
)

class TreeEditDistanceEvaluator(TopologicalEvaluatorProtocol):
    """
    Application Service que orquesta el pipeline de evaluación topológica TED.
    Coordina el flujo de transformaciones inmutables de forma secuencial y unidireccional.
    """
    def __init__(
        self,
        aligner: AnchorAlignmentStrategy,
        partitioner: AnchorPartitionStrategy,
        engine: TreeEditEngine,
        overflow_handler: OverflowStrategy,
        normalizer: NormalizationPolicy,
        cost_context: TreeEditCostContext,
        evaluation_context: TEDEvaluationContext | None = None
    ):
        self._aligner = aligner
        self._partitioner = partitioner
        self._engine = engine
        self._overflow_handler = overflow_handler
        self._normalizer = normalizer
        self._cost_context = cost_context
        self._exec_context = evaluation_context if evaluation_context is not None else TEDEvaluationContext()

    @property
    def metric_name(self) -> str:
        return "normalized_structural_score"

    def evaluate(self, candidate_ast: Sequence[ASTNode], ground_truth_ast: Sequence[ASTNode]) -> MetricScoreDTO:
        if not candidate_ast and not ground_truth_ast:
            return MetricScoreDTO(metric_name=self.metric_name, primary_score=1.0, diagnostics=None)

        # 1. Reconciliación analítica externa de hitos lógicos
        alignment = self._aligner.align(candidate_ast, ground_truth_ast)

        # 2. Segmentación del dominio en bosques ordenados contextuados
        windows = self._partitioner.partition(candidate_ast, ground_truth_ast, alignment)

        accumulated_distance = 0.0
        overflow_triggered = False
        windows_evaluated = 0

        # 3. Flujo continuo sobre el pipeline estructurado
        for window in windows:
            if window.candidate.size > self._exec_context.max_node_threshold or window.ground_truth.size > self._exec_context.max_node_threshold:
                overflow_triggered = True
                accumulated_distance += self._overflow_handler.handle_overflow(window, self._cost_context)
                continue

            accumulated_distance += self._engine.compute(window.candidate, window.ground_truth, self._cost_context)
            windows_evaluated += 1

        # 4. Cómputo atómico de costos base sin usar métodos agregados del puerto
        total_gt_cost = float(sum(self._cost_context.deletion_cost(n) for n in ground_truth_ast))
        total_candidate_cost = float(sum(self._cost_context.insertion_cost(n) for n in candidate_ast))

        norm_input = NormalizationInput(
            accumulated_distance=accumulated_distance,
            total_gt_destructive_cost=total_gt_cost,
            total_candidate_constructive_cost=total_candidate_cost
        )

        norm_result = self._normalizer.normalize(norm_input)

        diagnostics = TedDiagnostics(
            global_ted=accumulated_distance,
            total_windows_evaluated=windows_evaluated,
            overflow_triggered=overflow_triggered,
            normalization=norm_result.diagnostics
        )

        return MetricScoreDTO(metric_name=self.metric_name, primary_score=norm_result.score, diagnostics=diagnostics)