# ============================================================================
# ARCHIVO 2: core/benchmark/topology/criticality/traceability.py
# Task: 1.3.4
# NADRs: NADR-18 §5.5 R20, R21, R22
# ============================================================================

"""
Trazabilidad de clasificaciones de criticidad (NADR-F17BIS-18 §5.5).

Este módulo implementa el registro de las clasificaciones aplicadas
a cada nodo evaluado y los eventos de gobernanza para reclasificaciones.

NADR-18 §5.5 R20: Toda evaluación topológica que use la taxonomía
    MUST registrar la clasificación aplicada a cada nodo evaluado.
NADR-18 §5.5 R21: La taxonomía MUST estar documentada con la
    justificación de cada clasificación.
NADR-18 §5.5 R22: Toda reclasificación MUST registrarse como un
    evento de gobernanza con trazabilidad completa.

Diseño:
- Componente STATELESS (ENGINEERING_PRINCIPLES §II).
- Funciones puras: mismos inputs → mismo output.
- Sin acumulación interna de estado.
- El almacenamiento persistente es responsabilidad del pipeline
  de evaluación (Gate 2) o la infraestructura (Gate 3).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode

from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.criticality.ports import CriticalityPolicy
from core.benchmark.topology.criticality.policy import DefaultCriticalityPolicy


# Identificador de versión de la política de criticidad.
# Se usa para trazabilidad: permite saber qué versión de la taxonomía
# se aplicó en cada evaluación.
CRITICALITY_POLICY_VERSION: str = "1.0.0"


@dataclass(frozen=True)
class ClassificationRecord:
    """Registro inmutable de la clasificación aplicada a un nodo.

    NADR-18 §5.5 R20: Trazabilidad de clasificación por nodo.
    """
    node_id: str
    node_type: ContentNodeType
    criticality: NodeCriticality
    policy_version: str = CRITICALITY_POLICY_VERSION


@dataclass(frozen=True)
class ClassificationTrace:
    """Trazabilidad completa de clasificaciones para una evaluación.

    NADR-18 §5.5 R20: "La trazabilidad de la clasificación MUST estar
    disponible para auditoría posterior."
    """
    records: tuple[ClassificationRecord, ...] = field(default_factory=tuple)
    total_nodes: int = 0
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0

    @property
    def is_empty(self) -> bool:
        """True si no hay registros."""
        return len(self.records) == 0


@dataclass(frozen=True)
class ReclassificationEvent:
    """Evento de gobernanza para reclasificación de un tipo de nodo.

    NADR-18 §5.5 R22: "Toda reclasificación de un tipo de nodo MUST
    registrarse como un evento de gobernanza con trazabilidad completa.
    Las reclasificaciones MUST NOT aplicarse silenciosamente."

    Atributos:
        node_type: Tipo de nodo reclasificado.
        previous_criticality: Criticidad anterior.
        new_criticality: Criticidad nueva.
        justification: Justificación textual de la reclasificación.
            NADR-18 §5.2 R10: "Toda reclasificación MUST estar
            respaldada por un análisis de impacto sobre la baseline."
        timestamp: Marca temporal inyectada (no generada internamente).
            MUST ser inyectada como parámetro externo para determinismo
            (NADR-19 §5.7 R29).
    """
    node_type: ContentNodeType
    previous_criticality: NodeCriticality
    new_criticality: NodeCriticality
    justification: str
    timestamp: str


class ClassificationTracer:
    """Registra la clasificación de criticidad aplicada a nodos evaluados.

    NADR-18 §5.5 R20: Toda evaluación topológica que use la taxonomía
    de criticidad MUST registrar la clasificación aplicada a cada nodo.

    Diseño:
    - Componente STATELESS (ENGINEERING_PRINCIPLES §II).
    - Función pura: mismos inputs → mismo trace.
    - Sin acumulación interna de estado.
    """

    __slots__ = ("_policy",)

    def __init__(self, policy: CriticalityPolicy | None = None) -> None:
        """Inicializa el tracer de clasificaciones.

        Args:
            policy: Política de clasificación de criticidad.
                Si None, usa DefaultCriticalityPolicy.
        """
        self._policy = policy or DefaultCriticalityPolicy()

    def trace_nodes(self, nodes: Sequence[ASTNode]) -> ClassificationTrace:
        """Registra la clasificación de cada nodo evaluado.

        NADR-18 §5.5 R20: "Toda evaluación topológica que use la
        taxonomía de criticidad MUST registrar la clasificación
        aplicada a cada nodo evaluado."

        Args:
            nodes: Secuencia de nodos evaluados.

        Returns:
            ClassificationTrace inmutable con los registros de clasificación.
        """
        if not nodes:
            return ClassificationTrace()

        records: list[ClassificationRecord] = []
        critical_count = 0
        warning_count = 0
        info_count = 0

        for node in nodes:
            criticality = self._policy.criticality_of(node.node_type)
            records.append(
                ClassificationRecord(
                    node_id=node.node_id,
                    node_type=node.node_type,
                    criticality=criticality,
                )
            )

            if criticality is NodeCriticality.CRITICAL:
                critical_count += 1
            elif criticality is NodeCriticality.WARNING:
                warning_count += 1
            else:
                info_count += 1

        return ClassificationTrace(
            records=tuple(records),
            total_nodes=len(records),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
        )

    @property
    def policy(self) -> CriticalityPolicy:
        """Retorna la política de clasificación utilizada."""
        return self._policy


def create_reclassification_event(
    node_type: ContentNodeType,
    previous_criticality: NodeCriticality,
    new_criticality: NodeCriticality,
    justification: str,
    timestamp: str,
) -> ReclassificationEvent:
    """Crea un evento de gobernanza para reclasificación.

    NADR-18 §5.5 R22: "Toda reclasificación de un tipo de nodo MUST
    registrarse como un evento de gobernanza con trazabilidad completa."

    NADR-18 §5.2 R10: "Toda reclasificación MUST estar respaldada
    por un análisis de impacto sobre la baseline canónica."

    Args:
        node_type: Tipo de nodo reclasificado.
        previous_criticality: Criticidad anterior.
        new_criticality: Criticidad nueva.
        justification: Justificación textual (análisis de impacto).
        timestamp: Marca temporal inyectada (determinismo).

    Returns:
        ReclassificationEvent inmutable.

    Raises:
        ValueError: Si previous_criticality == new_criticality
            (no es una reclasificación real).
        ValueError: Si justification está vacía.
    """
    if previous_criticality is new_criticality:
        raise ValueError(
            f"Reclassification requires different criticalities. "
            f"Got {previous_criticality.value} == {new_criticality.value}"
        )
    if not justification.strip():
        raise ValueError(
            "Reclassification justification MUST NOT be empty. "
            "NADR-18 §5.2 R10 requires impact analysis."
        )

    return ReclassificationEvent(
        node_type=node_type,
        previous_criticality=previous_criticality,
        new_criticality=new_criticality,
        justification=justification,
        timestamp=timestamp,
    )