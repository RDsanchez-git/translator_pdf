"""
Contexto de costos ponderados por criticidad (NADR-F17BIS-18 §5.3).

Implementa TreeEditCostContext con ponderación determinista basada
en la taxonomía de criticidad de nodos.

Los pesos son configurables mediante inyección (NADR-18 §5.3 R11, R13).
Los valores por defecto son una propuesta inicial sujeta a validación
empírica en Fase 5 (NADR-18 §5.3 R12, R14).
"""
from __future__ import annotations

from core.ast.models import ASTNode
from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.criticality.ports import CriticalityPolicy
from core.benchmark.topology.criticality.policy import DefaultCriticalityPolicy


# Pesos por defecto para costos de edición según criticidad.
# NADR-18 §5.3 R12: "Propuesta inicial sujeta a validación empírica".
# NADR-18 §5.3 R14: Garantizan CRITICAL > WARNING > INFO en penalización.
DEFAULT_CRITICALITY_WEIGHTS: dict[NodeCriticality, float] = {
    NodeCriticality.CRITICAL: 5.0,
    NodeCriticality.WARNING: 2.0,
    NodeCriticality.INFO: 1.0,
}


class CriticalityAwareCostContext:
    """Contexto de costos que pondera por criticidad de nodo.

    Implementa TreeEditCostContext (core.benchmark.topology.ports).

    NADR-18 §5.3 R11: Implementa TreeEditCostContext.
    NADR-18 §5.3 R12: Ponderación determinista.
    NADR-18 §5.3 R13: Pesos configurables mediante inyección.
    NADR-18 §5.3 R14: Pesos por defecto documentados como propuesta inicial.
    NADR-18 §5.3 R15: Integración con ZhangShashaEngine sin modificarlo.
    """

    __slots__ = ("_policy", "_weights")

    def __init__(
        self,
        policy: CriticalityPolicy | None = None,
        weights: dict[NodeCriticality, float] | None = None,
    ) -> None:
        """Inicializa el contexto de costos ponderados.

        Args:
            policy: Política de clasificación de criticidad.
                Si None, usa DefaultCriticalityPolicy.
            weights: Pesos por nivel de criticidad.
                Si None, usa DEFAULT_CRITICALITY_WEIGHTS.
                Debe contener exactamente 3 entradas (una por nivel).
        """
        self._policy = policy or DefaultCriticalityPolicy()
        self._weights = dict(weights) if weights else dict(DEFAULT_CRITICALITY_WEIGHTS)

        # Validar que los pesos cubren todos los niveles
        missing = set(NodeCriticality) - set(self._weights.keys())
        if missing:
            raise ValueError(
                f"Missing weights for criticality levels: "
                f"{[m.value for m in missing]}"
            )

    def deletion_cost(self, node: ASTNode) -> float:
        """Costo de eliminar un nodo, ponderado por su criticidad.

        NADR-18 §5.3 R12: Determinista (mismo nodo → mismo costo).
        """
        criticality = self._policy.criticality_of(node.node_type)
        return self._weights[criticality]

    def insertion_cost(self, node: ASTNode) -> float:
        """Costo de insertar un nodo, ponderado por su criticidad.

        NADR-18 §5.3 R12: Determinista (mismo nodo → mismo costo).
        """
        criticality = self._policy.criticality_of(node.node_type)
        return self._weights[criticality]

    def substitution_cost(self, candidate: ASTNode, ground_truth: ASTNode) -> float:
        """Costo de sustituir un nodo por otro.

        Lógica:
        - Si ambos nodos tienen el mismo tipo Y contenido textual: costo 0.0
          (sustitución idéntica, sin penalización).
        - Si difieren en tipo o contenido: el costo es el máximo de las
          criticidades de ambos nodos. Esto garantiza que la pérdida
          de un nodo CRITICAL siempre tenga la mayor penalización,
          incluso si se sustituye por un nodo INFO.

        NADR-18 §5.3 R12: Determinista.
        """
        # Mismo criterio que UnitCostContext: tipo Y contenido deben coincidir
        if (candidate.node_type == ground_truth.node_type
                and candidate.text_content == ground_truth.text_content):
            return 0.0

        # Costo = max de ambas criticidades (conservador, semántica de pérdida)
        cand_crit = self._policy.criticality_of(candidate.node_type)
        gt_crit = self._policy.criticality_of(ground_truth.node_type)
        return max(self._weights[cand_crit], self._weights[gt_crit])

    @property
    def weights(self) -> dict[NodeCriticality, float]:
        """Retorna una copia de los pesos configurados (read-only)."""
        return dict(self._weights)

    @property
    def policy(self) -> CriticalityPolicy:
        """Retorna la política de clasificación utilizada."""
        return self._policy