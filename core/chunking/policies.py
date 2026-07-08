from typing import Final
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.chunking.models import BoundaryDecision

class StructuralNodeAtomicityPolicy:
    """
    SOTA: Política determinista de indivisibilidad topológica.
    Basada estrictamente en la ontología de ContentNodeType existente.
    """
    
    # Búsqueda O(1) inmutable en tiempo de ejecución.
    # Excluye explícitamente INLINE_EQUATION y TABLE_SIMPLE para permitir 
    # flexibilidad en el empaquetado de texto denso.
    _ATOMIC_TYPES: Final = frozenset({
        ContentNodeType.DISPLAY_EQUATION,
        ContentNodeType.TABLE_COMPLEX,
        ContentNodeType.IMAGE,
        ContentNodeType.CODE,
        ContentNodeType.COMPOSITE_BLOCK,
    })

    def is_atomic(self, node: ASTNode) -> bool:
        """Determina indivisibilidad estructural de un nodo O(1)."""
        return node.node_type in self._ATOMIC_TYPES


class StructuralChunkBoundaryPolicy:
    """
    SOTA: Política de cohesión lógica para el empaquetamiento.
    Actualmente opera de forma permisiva (ALLOW) hasta que el modelo del AST
    incorpore metadata semántica (como idioma o relaciones de títulos).
    """
    
    def can_group(self, current_chunk_nodes: tuple[ASTNode, ...], next_node: ASTNode) -> BoundaryDecision:
        """
        Evalúa si el next_node puede entrar al chunk actual.
        Al no existir restricciones estructurales duras en este momento de la arquitectura,
        se permite la agrupación por defecto.
        """
        if not current_chunk_nodes:
            return BoundaryDecision.ALLOW

        # TODO: Implementar reglas de BoundaryDecision.HARD_BREAK cuando el dominio 
        # AST incorpore semántica de contexto cruzado (ej. cambios de sección).
        return BoundaryDecision.ALLOW