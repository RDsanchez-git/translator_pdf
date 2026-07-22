from core.ast.models import ASTNode
from core.benchmark.topology.ports import TreeEditCostContext

class UnitCostContext(TreeEditCostContext):
    """Contexto estricto de costos unitarios deterministas para pruebas de correctitud."""
    def deletion_cost(self, node: ASTNode) -> float:
        return 1.0

    def insertion_cost(self, node: ASTNode) -> float:
        return 1.0

    def substitution_cost(self, candidate: ASTNode, ground_truth: ASTNode) -> float:
        return 0.0 if candidate.text_content == ground_truth.text_content else 1.0