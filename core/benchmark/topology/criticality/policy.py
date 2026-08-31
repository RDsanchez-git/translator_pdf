"""
Política canónica de clasificación de criticidad (NADR-F17BIS-18 §5.1, §5.2).

Implementa el mapeo determinista de ContentNodeType → NodeCriticality.
Declarativo, centralizado y extensible (NADR-18 §5.1 R6).
"""
from __future__ import annotations

from core.ast.enums import ContentNodeType

from core.benchmark.topology.criticality.models import NodeCriticality


# Mapeo canónico: ContentNodeType → NodeCriticality
# NADR-18 §5.1 R3-R7: Declarativo, centralizado, extensible.
_CRITICALITY_MAP: dict[ContentNodeType, NodeCriticality] = {
    # CRITICAL: Pérdida inaceptable, HARD_FAIL absoluto
    ContentNodeType.DISPLAY_EQUATION: NodeCriticality.CRITICAL,
    ContentNodeType.INLINE_EQUATION: NodeCriticality.CRITICAL,
    ContentNodeType.TABLE_SIMPLE: NodeCriticality.CRITICAL,
    ContentNodeType.TABLE_COMPLEX: NodeCriticality.CRITICAL,
    # WARNING: Pérdida tolerable bajo umbrales configurables
    ContentNodeType.HEADING: NodeCriticality.WARNING,
    ContentNodeType.PARAGRAPH: NodeCriticality.WARNING,
    ContentNodeType.CODE: NodeCriticality.WARNING,
    # INFO: Pérdida observable sin impacto en veredicto
    ContentNodeType.IMAGE: NodeCriticality.INFO,
    ContentNodeType.CAPTION: NodeCriticality.INFO,
    ContentNodeType.LIST: NodeCriticality.INFO,
    ContentNodeType.COMPOSITE_BLOCK: NodeCriticality.INFO,
}


class DefaultCriticalityPolicy:
    """Política canónica de clasificación de criticidad.

    Implementa CriticalityPolicy (Protocol) con el mapeo canónico inicial.

    NADR-18 §5.1 R1: Todo tipo de nodo debe tener clasificación.
    NADR-18 §5.1 R3-R7: Definición declarativa de cada nivel.
    NADR-18 §5.2 R8: Extensible mediante composición.
    NADR-18 §5.2 R9: Fallo explícito ante tipo sin clasificación.
    NADR-18 §5.2 R10: Clasificación por tipo, no por contenido.
    """

    __slots__ = ()

    def criticality_of(self, node_type: ContentNodeType) -> NodeCriticality:
        """Retorna el nivel de criticidad para un tipo de nodo dado.

        Args:
            node_type: El tipo estructural del nodo AST.

        Returns:
            El nivel de criticidad correspondiente.

        Raises:
            ValueError: Si el tipo de nodo no tiene clasificación asignada.
                Esto garantiza extensibilidad segura (NADR-18 §5.2 R9).
        """
        try:
            return _CRITICALITY_MAP[node_type]
        except KeyError:
            raise ValueError(
                f"ContentNodeType '{node_type.value}' has no criticality classification. "
                f"This violates NADR-18 §5.1 R1 (every node type MUST have a classification). "
                f"Add an entry to _CRITICALITY_MAP in "
                f"core/benchmark/topology/criticality/policy.py"
            ) from None

    @staticmethod
    def all_classified_types() -> frozenset[ContentNodeType]:
        """Retorna el conjunto de tipos actualmente clasificados.

        Útil para verificar cobertura exhaustiva en tests y auditorías.
        """
        return frozenset(_CRITICALITY_MAP.keys())