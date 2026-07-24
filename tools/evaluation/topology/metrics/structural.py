from dataclasses import dataclass
from typing import Sequence
from apted import APTED, Config
from apted.helpers import Tree

from core.ast.models import ASTNode
from tools.evaluation.topology.fingerprint import ASTFingerprintPolicy
from tools.evaluation.topology.models import MetricName, MetricResult
from tools.evaluation.topology.ports import TopologyMetric


@dataclass(frozen=True)
class CostMatrix:
    """
    Value Object inmutable que encapsula los pesos numéricos de edición
    conforme a la especificación Cost Matrix Spec Version 1.0-draft (ADR 0017).
    """

    delete_cost: float = 1.0
    insert_cost: float = 1.0
    rename_same_type_cost: float = 0.5
    rename_diff_type_cost: float = 2.0

    @classmethod
    def default_v1(cls) -> "CostMatrix":
        """Matriz canónica de producción para la especificación Spec v1.0."""
        return cls()


class CustomAPTEDConfig(Config):
    """Adaptador de configuración para APTED orientado a CostMatrix."""

    def __init__(self, matrix: CostMatrix) -> None:
        self._matrix = matrix

    def delete(self, node: Tree) -> float:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        return self._matrix.delete_cost

    def insert(self, node: Tree) -> float:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        return self._matrix.insert_cost

    def rename(self, node1: Tree, node2: Tree) -> float:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        type1, content1 = node1.name
        type2, content2 = node2.name

        if type1 == type2 and content1 == content2:
            return 0.0
        if type1 == type2:
            return self._matrix.rename_same_type_cost
        return self._matrix.rename_diff_type_cost


class StructuralTopologyMetric(TopologyMetric):
    """
    Métrica de similaridad estructural jerárquica basada en Tree Edit Distance (TED).

    Reconstruye la jerarquía profunda del árbol AST V2 indexando parent_node_id
    y garantizando el cumplimiento de las invariantes del ADR 0017.
    """

    def __init__(self, cost_matrix: CostMatrix | None = None) -> None:
        self._matrix = cost_matrix or CostMatrix.default_v1()
        self._config = CustomAPTEDConfig(matrix=self._matrix)

    @property
    def name(self) -> MetricName:
        return MetricName.STRUCTURAL

    def evaluate(
        self,
        candidate: Sequence[ASTNode],
        ground_truth: Sequence[ASTNode],
    ) -> MetricResult:
        cand_tree, total_cand_nodes = self._build_apted_tree(candidate)
        gt_tree, total_gt_nodes = self._build_apted_tree(ground_truth)

        # Invariante 3: Casos borde vacíos
        if total_cand_nodes == 0 and total_gt_nodes == 0:
            return MetricResult(metric_name=self.name, value=1.0)

        # Cálculo de distancia mediante APTED
        apted = APTED(cand_tree, gt_tree, self._config)
        distance = float(apted.compute_edit_distance())

        # Cálculo de MaxCost (ADR 0017 Section 4.4)
        max_cost = (self._matrix.delete_cost * total_gt_nodes) + (
            self._matrix.insert_cost * total_cand_nodes
        )

        if max_cost == 0.0 or distance == 0.0:
            score = 1.0
        else:
            score = max(0.0, 1.0 - (distance / max_cost))

        return MetricResult(
            metric_name=self.name,
            value=score,
            details={
                "edit_distance": distance,
                "candidate_nodes": total_cand_nodes,
                "ground_truth_nodes": total_gt_nodes,
                "max_cost": max_cost,
            },
        )

    def _build_apted_tree(self, nodes: Sequence[ASTNode]) -> tuple[Tree, int]:
        """
        Reconstruye el árbol APTED indexando parent_node_id.
        Envuelve la estructura en una raíz virtual uniforme y cuenta los nodos en O(N).
        """
        if not nodes:
            return Tree(("", "")), 0

        node_ids = {node.node_id for node in nodes}
        children_map: dict[str | None, list[ASTNode]] = {}

        for node in nodes:
            parent_key = (
                node.parent_node_id if node.parent_node_id in node_ids else None
            )
            children_map.setdefault(parent_key, []).append(node)

        roots = children_map.get(None, [])
        children_trees: list[Tree] = []
        total_count = 0

        for root in roots:
            subtree, count = self._build_apted_subtree(root, children_map)
            children_trees.append(subtree)
            total_count += count

        return Tree(("Document", "root"), *children_trees), total_count

    def _build_apted_subtree(
        self,
        node: ASTNode,
        children_map: dict[str | None, list[ASTNode]],
    ) -> tuple[Tree, int]:
        """Transforma recursivamente un ASTNode y sus descendientes usando children_map."""
        label = ASTFingerprintPolicy.semantic_fingerprint(node)
        children = children_map.get(node.node_id, [])

        children_trees: list[Tree] = []
        child_count = 0

        for child in children:
            subtree, count = self._build_apted_subtree(child, children_map)
            children_trees.append(subtree)
            child_count += count

        return Tree(label, *children_trees), 1 + child_count