from core.benchmark.topology.ports import OverflowStrategy, TreeEditCostContext
from core.benchmark.topology.models import EvaluationWindow

class WorstCaseOverflowStrategy(OverflowStrategy):
    """
    Garantiza un fallback de penalización lineal O(N) ante desbordamientos de ventanas.
    Calcula la demeritación sumando iterativamente los costos atómicos del puerto.
    """
    def handle_overflow(self, window: EvaluationWindow, cost_context: TreeEditCostContext) -> float:
        return (
            float(sum(cost_context.deletion_cost(n) for n in window.ground_truth.nodes)) +
            float(sum(cost_context.insertion_cost(n) for n in window.candidate.nodes))
        )