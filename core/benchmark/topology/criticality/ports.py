"""
Puertos del subsistema de criticidad de nodos (NADR-F17BIS-18 §5.1).

Este módulo define el contrato abstracto (Protocol) que toda política
de clasificación de criticidad debe implementar.

El protocolo es consumido por:
- CriticalityAwareCostContext (para ponderar costos de edición)
- CriticalityVerdictEmitter (para emitir veredictos por criticidad)
- ClassificationTraceability (para registrar clasificaciones)
"""
from __future__ import annotations

from typing import Protocol

from core.ast.enums import ContentNodeType

from core.benchmark.topology.criticality.models import NodeCriticality


class CriticalityPolicy(Protocol):
    """Contrato abstracto para políticas de clasificación de criticidad.

    Toda implementación debe mapear cada ContentNodeType a exactamente
    un nivel de NodeCriticality de forma determinista y exhaustiva.

    NADR-18 §5.1 R1: Todo tipo de nodo debe tener clasificación.
    NADR-18 §5.2 R9: Fallo explícito ante tipo sin clasificación (extensibilidad).
    """

    def criticality_of(self, node_type: ContentNodeType) -> NodeCriticality:
        """Retorna el nivel de criticidad para un tipo de nodo dado.

        Args:
            node_type: El tipo estructural del nodo AST.

        Returns:
            El nivel de criticidad correspondiente.

        Raises:
            ValueError: Si el tipo de nodo no tiene clasificación asignada.
                Esto garantiza extensibilidad segura (NADR-18 §5.2 R9):
                si se agrega un nuevo ContentNodeType, el fallo es explícito.
        """
        ...