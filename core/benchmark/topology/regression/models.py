"""
Modelos de dominio del subsistema de regresión topológica graduada.

NADR-F17BIS-19:
- §5.1 R1: RegressionVerdict con exactamente 3 niveles.
- §5.1 R4-R7: Umbrales de NSS configurables.
- §5.3 R12-R14: Umbrales deterministas con valores por defecto
  documentados como propuesta inicial.

Diseño:
- overall_score es la ÚNICA fuente de verdad (NSS).
- nss_score es un property alias para claridad semántica.
- RegressionCriticalitySignal es un enum tipado (no string libre).

CORRECCIÓN P1 (fail-fast):
- overall_score es OBLIGATORIO (sin default).
- Construir un reporte sin NSS es un error de programación,
  no un estado válido del dominio.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from core.benchmark.topology.models import MetricScoreDTO, TopologicalEvaluationReport


class RegressionVerdict(str, Enum):
    """Veredicto de regresión graduado (NADR-19 §5.1 R1).

    Niveles en orden de severidad descendente:
    - HARD_FAIL: Pérdida de nodos CRITICAL o NSS < umbral crítico.
    - WARNING: Pérdida WARNING por encima de umbral o NSS entre umbrales.
    - PASS: Sin desviación significativa.
    """

    HARD_FAIL = "HARD_FAIL"
    WARNING = "WARNING"
    PASS = "PASS"

    @property
    def severity_rank(self) -> int:
        """Rank numérico para agregación por corpus (mayor = más severo)."""
        _RANKS = {
            RegressionVerdict.HARD_FAIL: 2,
            RegressionVerdict.WARNING: 1,
            RegressionVerdict.PASS: 0,
        }
        return _RANKS[self]


class RegressionCriticalitySignal(str, Enum):
    """Señal de criticidad emitida por el doble mecanismo.

    Enum tipado para evitar strings libres (ENGINEERING_PRINCIPLES §III).
    """

    ABSOLUTE_FAIL = "ABSOLUTE_FAIL"
    WARNING = "WARNING"
    PASS = "PASS"


@dataclass(frozen=True)
class RegressionThresholds:
    """Umbrales de NSS para veredicto de regresión (NADR-19 §5.3 R12-R14).

    Semántica:
    - NSS < nss_hard_fail → HARD_FAIL
    - nss_hard_fail <= NSS < nss_warning → WARNING
    - NSS >= nss_warning → PASS (si no hay pérdida CRITICAL/WARNING)

    Invariante: 0.0 <= nss_hard_fail < nss_warning <= 1.0

    NADR-19 §5.3 R12: Valores por defecto documentados como propuesta
    inicial sujeta a validación empírica sobre la baseline canónica.
    NO son valores óptimos calibrados.
    """

    nss_hard_fail: float = 0.80
    nss_warning: float = 0.95

    def __post_init__(self) -> None:
        if not (0.0 <= self.nss_hard_fail < self.nss_warning <= 1.0):
            raise ValueError(
                f"Invariant failure: thresholds must satisfy "
                f"0.0 <= nss_hard_fail < nss_warning <= 1.0. "
                f"Got nss_hard_fail={self.nss_hard_fail}, "
                f"nss_warning={self.nss_warning}."
            )


DEFAULT_REGRESSION_THRESHOLDS = RegressionThresholds(
    nss_hard_fail=0.80,
    nss_warning=0.95,
)


@dataclass(frozen=True)
class RegressionEvaluationReport:
    """Reporte de evaluación de regresión con veredicto graduado.

    ÚNICA FUENTE DE VERDAD: overall_score es el NSS.
    nss_score es un property alias para claridad semántica.

    CORRECCIÓN P1: overall_score es OBLIGATORIO (sin default).
    Construir un reporte sin NSS es un error de programación.
    Esto garantiza fail-fast: no existe un estado válido del dominio
    donde el NSS sea desconocido o esté ausente.

    Nota de consumo:
    - evaluate_run() retorna TopologicalEvaluationReport (protocolo).
      El veredicto se pierde en esa conversión.
    - evaluate_regression() retorna RegressionEvaluationReport (completo).
      El veredicto está disponible.
    - Gate 3 debe usar evaluate_regression() para el entry point.
    """

    # Campos OBLIGATORIOS (sin default) — orden primero
    document_id: str
    metrics: Tuple[MetricScoreDTO, ...]
    overall_score: float

    # Campos OPCIONALES (con default) — orden después
    verdict: RegressionVerdict = RegressionVerdict.PASS
    criticality_signal: RegressionCriticalitySignal = RegressionCriticalitySignal.PASS
    critical_false_negatives: int = 0
    warning_false_negatives: int = 0
    info_false_negatives: int = 0

    @property
    def nss_score(self) -> float:
        """Alias semántico para overall_score. NSS es el overall_score."""
        return self.overall_score

    @property
    def is_hard_fail(self) -> bool:
        return self.verdict is RegressionVerdict.HARD_FAIL

    @property
    def is_warning(self) -> bool:
        return self.verdict is RegressionVerdict.WARNING

    @property
    def is_pass(self) -> bool:
        return self.verdict is RegressionVerdict.PASS

    def to_topological_report(self) -> TopologicalEvaluationReport:
        """Convierte a TopologicalEvaluationReport estándar.

        El overall_score (NSS) se propaga correctamente.
        El veredicto y la señal de criticidad se pierden en esta
        conversión. Para acceso completo, usar evaluate_regression().
        """
        return TopologicalEvaluationReport(
            document_id=self.document_id,
            metrics=self.metrics,
            overall_score=self.overall_score,
        )