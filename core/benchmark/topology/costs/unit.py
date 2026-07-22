from core.ast.models import ASTNode
from core.benchmark.topology.ports import TreeEditCostContext

class UnitCostContext(TreeEditCostContext):
    """
    Implementación canónica de costos unitarios del subdominio topológico.
    Aplica penalizaciones simétricas atómicas (Insert=1.0, Delete=1.0, Substitution=1.0 si difiere el texto o el tipo estructural).
    """
    def deletion_cost(self, node: ASTNode) -> float:
        return 1.0

    def insertion_cost(self, node: ASTNode) -> float:
        return 1.0

    def substitution_cost(self, candidate: ASTNode, ground_truth: ASTNode) -> float:
        return 0.0 if (
            candidate.node_type == ground_truth.node_type 
            and candidate.text_content == ground_truth.text_content
        ) else 1.0