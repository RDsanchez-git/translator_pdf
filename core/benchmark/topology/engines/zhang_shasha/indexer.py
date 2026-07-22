from typing import Sequence, List, Dict
from collections import defaultdict
from core.ast.models import ASTNode, ParagraphPayload
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.benchmark.topology.models import PostorderIndex

class IndexConsistencyError(ValueError):
    """Excepción unificada para cualquier corrupción o asimetría de invariantes del índice."""
    pass

VIRTUAL_ROOT_ID = "__virtual_root__"

class PostorderIndexer:
    """
    Construye los vectores paralelos de indexación en tiempo O(N).
    Garantiza la invariante matemática de Ordered Trees mediante una barrera estricta
    y sintetiza una raíz virtual neutra cuando se procesan bosques de múltiples raíces.
    """
    def build(self, forest: Sequence[ASTNode]) -> PostorderIndex:
        if not forest:
            return PostorderIndex(nodes=(), leftmost=(), keyroots=(), postorder=())

        slice_node_ids = {node.node_id for node in forest}
        children_map: Dict[str, List[ASTNode]] = defaultdict(list)
        
        for node in forest:
            if node.parent_node_id and node.parent_node_id in slice_node_ids:
                children_map[node.parent_node_id].append(node)

        # Validación rígida de consistencia de ordenamiento total
        self._validate_sibling_order(children_map)

        roots = [n for n in forest if not n.parent_node_id or n.parent_node_id not in slice_node_ids]

        # SOTA FIX: Si hay múltiples raíces, unificar bajo un contenedor virtual de costo cero
        if len(roots) > 1:
            virtual_root = ASTNode(
                node_id=VIRTUAL_ROOT_ID,
                sequence_id=-1,
                node_type=ContentNodeType.PARAGRAPH,
                strategy=TranslationStrategy.TRANSLATE,
                payload=ParagraphPayload(content="__virtual__")
            )
            children_map[VIRTUAL_ROOT_ID] = roots
            roots = [virtual_root]

        nodes: List[ASTNode] = []
        leftmost: List[int] = []

        for root_node in roots:
            self._traverse_node(root_node, children_map, nodes, leftmost)

        highest_for_lm: Dict[int, int] = {}
        for k, lm in enumerate(leftmost):
            highest_for_lm[lm] = k
        
        keyroots = tuple(sorted(highest_for_lm.values()))
        postorder = tuple(range(len(nodes)))

        if len(nodes) != len(leftmost):
            raise IndexConsistencyError(f"Asimetría de vectores: {len(nodes)} nodos vs {len(leftmost)} leftmost.")
        if len(keyroots) > len(nodes):
            raise IndexConsistencyError("El volumen de keyroots corrompe las dimensiones del bosque.")

        return PostorderIndex(nodes=tuple(nodes), leftmost=tuple(leftmost), keyroots=keyroots, postorder=postorder)

    def _validate_sibling_order(self, children_map: Dict[str, List[ASTNode]]) -> None:
        """Fuerza la invariante de orden total uniforme sobre los nodos hermanos de cada sub-bosque."""
        for parent_id, siblings in children_map.items():
            if not siblings or parent_id == VIRTUAL_ROOT_ID:
                continue
            
            has_seq_flags = [s.has_valid_sequence for s in siblings]
            if any(has_seq_flags) and not all(has_seq_flags):
                raise IndexConsistencyError(
                    f"Orden parcial inválido en parent '{parent_id}': "
                    f"Se detectó una mezcla de nodos con y sin secuencias válidas."
                )
            
            if has_seq_flags[0]:
                for i in range(1, len(siblings)):
                    prev, curr = siblings[i - 1], siblings[i]
                    if prev.sequence_id >= curr.sequence_id:
                        raise IndexConsistencyError(
                            f"Invariante de Sibling Order rota en parent '{parent_id}': "
                            f"El orden secuencial decrece o se duplica ({prev.sequence_id} >= {curr.sequence_id})."
                        )

    def _traverse_node(
        self, 
        node: ASTNode, 
        children_map: Dict[str, List[ASTNode]], 
        nodes: List[ASTNode], 
        leftmost: List[int]
    ) -> int:
        first_child_lm: int | None = None
        local_children = children_map.get(node.node_id, [])
        
        for idx, child in enumerate(local_children):
            child_lm = self._traverse_node(child, children_map, nodes, leftmost)
            if idx == 0:
                first_child_lm = child_lm
        
        curr_idx = len(nodes)
        nodes.append(node)
        lm = first_child_lm if first_child_lm is not None else curr_idx
        leftmost.append(lm)
        return lm