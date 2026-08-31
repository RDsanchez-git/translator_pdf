# ============================================================================
# ARCHIVO 1: core/benchmark/topology/criticality/verdict.py
# Tasks: 1.3.1, 1.3.2, 1.3.3
# NADRs: NADR-18 §5.4 R16, R17, R18, R19
# ============================================================================

"""
Emisor de veredictos por criticidad (NADR-F17BIS-18 §5.4).

Este módulo implementa la detección de pérdidas de nodos clasificadas
por nivel de criticidad, emitiendo señales de fallo absoluto (CRITICAL),
advertencia (WARNING) u observación (INFO).

El veredicto se deriva de los `false_negatives` de `RecallDiagnostics`
por tipo de nodo, clasificados mediante `CriticalityPolicy`.

La integración con EntityRecallEvaluator es directa: el pipeline de
evaluación produce MetricScoreDTO con RecallDiagnostics por tipo de nodo,
y este componente los consume para emitir el veredicto.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from core.ast.enums import ContentNodeType
from core.benchmark.topology.models import RecallDiagnostics

from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.criticality.ports import CriticalityPolicy
from core.benchmark.topology.criticality.policy import DefaultCriticalityPolicy


@dataclass(frozen=True)
class RecallByNodeType:
    """Resultado de recall para un tipo de nodo específico.

    Este DTO encapsula la información necesaria para que
    CriticalityVerdictEmitter evalúe pérdidas por criticidad.

    Se construye a partir de los MetricScoreDTO producidos por
    EntityRecallEvaluator, extrayendo el node_type del metric_name
    y las RecallDiagnostics del campo diagnostics.
    """
    node_type: ContentNodeType
    diagnostics: RecallDiagnostics


@dataclass(frozen=True)
class CriticalityVerdict:
    """Veredicto por criticidad derivado de pérdidas detectadas en recall.

    NADR-18 §5.4 R16-R19: Clasifica las pérdidas por nivel de criticidad
    y determina si constituyen un fallo absoluto, advertencia u observación.

    Inmutable y determinista: mismos inputs → mismo veredicto.
    """
    has_critical_loss: bool
    has_warning_loss: bool
    has_info_loss: bool
    critical_false_negatives: int
    warning_false_negatives: int
    info_false_negatives: int

    @property
    def is_absolute_failure(self) -> bool:
        """NADR-18 §5.4 R16: Pérdida de CRITICAL = fallo absoluto."""
        return self.has_critical_loss

    @property
    def is_warning(self) -> bool:
        """NADR-18 §5.4 R18: Pérdida de WARNING que supera umbral."""
        return self.has_warning_loss and not self.is_absolute_failure

    @property
    def is_pass_with_observation(self) -> bool:
        """NADR-18 §5.4 R19: Solo pérdida de INFO = PASS con observación."""
        return self.has_info_loss and not self.is_absolute_failure and not self.has_warning_loss

    @property
    def total_false_negatives(self) -> int:
        """Suma total de falsos negativos across todos los niveles."""
        return (
            self.critical_false_negatives
            + self.warning_false_negatives
            + self.info_false_negatives
        )


class CriticalityVerdictEmitter:
    """Emisor de veredictos por criticidad basado en recall por tipo de nodo.

    NADR-18 §5.4 R16: Pérdida de nodo CRITICAL → fallo absoluto.
    NADR-18 §5.4 R17: Precedencia sobre métricas agregadas.
    NADR-18 §5.4 R18: Pérdida WARNING → umbral configurable.
    NADR-18 §5.4 R19: Pérdida INFO → PASS con observación.

    Diseño:
    - Componente puro sin estado mutable (ENGINEERING_PRINCIPLES §II).
    - Configurable mediante inyección de policy y umbral.
    - Determinista: mismos inputs → mismo output.
    - Integra con EntityRecallEvaluator vía RecallByNodeType.
    """

    __slots__ = ("_policy", "_warning_threshold")

    def __init__(
        self,
        policy: CriticalityPolicy | None = None,
        warning_threshold: int = 1,
    ) -> None:
        """Inicializa el emisor de veredictos.

        Args:
            policy: Política de clasificación de criticidad.
                Si None, usa DefaultCriticalityPolicy.
            warning_threshold: Cantidad mínima de falsos negativos WARNING
                para emitir señal de advertencia. Default: 1.
                Debe ser >= 1. Semántica: "threshold o más FNs = WARNING".
        """
        if warning_threshold < 1:
            raise ValueError(
                f"warning_threshold must be >= 1, got {warning_threshold}"
            )
        self._policy = policy or DefaultCriticalityPolicy()
        self._warning_threshold = warning_threshold

    def evaluate(
        self, recall_results: Sequence[RecallByNodeType]
    ) -> CriticalityVerdict:
        """Evalúa las pérdidas detectadas y emite un veredicto por criticidad.

        Args:
            recall_results: Secuencia de resultados de recall por tipo de nodo.

        Returns:
            CriticalityVerdict con las pérdidas clasificadas por nivel.
        """
        critical_fn = 0
        warning_fn = 0
        info_fn = 0

        for result in recall_results:
            fn = result.diagnostics.false_negatives
            if fn <= 0:
                continue

            criticality = self._policy.criticality_of(result.node_type)
            if criticality == NodeCriticality.CRITICAL:
                critical_fn += fn
            elif criticality == NodeCriticality.WARNING:
                warning_fn += fn
            elif criticality == NodeCriticality.INFO:
                info_fn += fn

        return CriticalityVerdict(
            has_critical_loss=critical_fn > 0,
            has_warning_loss=warning_fn >= self._warning_threshold,
            has_info_loss=info_fn > 0,
            critical_false_negatives=critical_fn,
            warning_false_negatives=warning_fn,
            info_false_negatives=info_fn,
        )

    @property
    def warning_threshold(self) -> int:
        """Retorna el umbral de advertencia configurado."""
        return self._warning_threshold

    @property
    def policy(self) -> CriticalityPolicy:
        """Retorna la política de clasificación utilizada."""
        return self._policy