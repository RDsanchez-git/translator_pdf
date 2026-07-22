from typing import Sequence, Tuple
from dataclasses import dataclass
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.benchmark.topology.ports import NodeMatchingPolicy
from core.benchmark.topology.models import MatchingKey

@dataclass(frozen=True)
class IndexedAnchor:
    """Wrapper topológico que preserva la coordenada espacial del ancla dentro del AST original."""
    ast_index: int
    node: ASTNode

class AnchorExtractor:
    """Filtra los nodos calificados y captura su índice original de lectura."""
    def __init__(self, anchor_type: ContentNodeType):
        self._anchor_type = anchor_type

    def extract(self, ast: Sequence[ASTNode]) -> Tuple[IndexedAnchor, ...]:
        return tuple(
            IndexedAnchor(ast_index=i, node=n) 
            for i, n in enumerate(ast) 
            if n.node_type == self._anchor_type
        )

class MatchingKeyMapper:
    def __init__(self, matching_policy: NodeMatchingPolicy):
        self._policy = matching_policy

    def map_to_keys(self, anchors: Sequence[IndexedAnchor]) -> Tuple[MatchingKey, ...]:
        return tuple(self._policy.matching_key(a.node) for a in anchors)