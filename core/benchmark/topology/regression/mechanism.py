"""
Doble mecanismo de protección para regresión topológica graduada.

NADR-F17BIS-19 §5.2:
- R8: Mecanismo 1 — NSS ponderado por criticidad (protección gradual).
- R9: Mecanismo 2 — Regla absoluta de pérdida CRITICAL (protección absoluta).
- R10: Precedencia del Mecanismo 2 sobre el Mecanismo 1.
- R11: Complementariedad: el veredicto final es el peor resultado de ambos.

Naming: DoubleProtectionMechanism para trazabilidad directa con
el ADR ("Doble Mecanismo de Protección").
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from core.benchmark.topology.criticality.verdict import CriticalityVerdict
from core.benchmark.topology.regression.errors import InvalidNSSScoreError
from core.benchmark.topology.regression.models import (
    RegressionCriticalitySignal,
    RegressionThresholds,
    RegressionVerdict,
    DEFAULT_REGRESSION_THRESHOLDS,
)


@dataclass(frozen=True)
class DoubleProtectionResult:
    """Resultado del doble mecanismo de protección. Inmutable."""

    verdict: RegressionVerdict
    nss_score: float
    criticality_signal: RegressionCriticalitySignal
    critical_false_negatives: int
    warning_false_negatives: int
    info_false_negatives: int

    @property
    def is_hard_fail(self) -> bool:
        return self.verdict is RegressionVerdict.HARD_FAIL


class DoubleProtectionMechanism:
    """Doble mecanismo de protección para regresión topológica.

    Stateless, determinista, sin I/O (ENGINEERING_PRINCIPLES §II).

    Ejemplo canónico (NADR-19 §5.2 R11):
    1 nodo CRITICAL perdido en 1000 nodos → NSS alto (>0.95)
    pero HARD_FAIL por Mecanismo 2.
    """

    __slots__ = ("_thresholds",)

    def __init__(
        self,
        thresholds: RegressionThresholds | None = None,
    ) -> None:
        self._thresholds = thresholds or DEFAULT_REGRESSION_THRESHOLDS

    def evaluate(
        self,
        nss_score: float,
        criticality_verdict: CriticalityVerdict,
    ) -> DoubleProtectionResult:
        """Evalúa el doble mecanismo y emite el veredicto final.

        NADR-19 §5.2 R10: Precedencia del Mecanismo 2 (CRITICAL)
        sobre el Mecanismo 1 (NSS).

        Args:
            nss_score: NSS ponderado por criticidad [0.0, 1.0].
            criticality_verdict: Veredicto de criticidad del Gate 1.

        Returns:
            DoubleProtectionResult con el veredicto final.

        Raises:
            InvalidNSSScoreError: Si nss_score no está en [0.0, 1.0]
                o no es finito (NaN, inf).
        """
        # Fail-fast: validar NSS (NADR-19 §5.2 R14, ENGINEERING_PRINCIPLES §IV)
        if not isfinite(nss_score) or not (0.0 <= nss_score <= 1.0):
            raise InvalidNSSScoreError(nss_score)

        # ── Mecanismo 2: Regla absoluta CRITICAL (R9, R10) ──
        # PRECEDENCIA TOTAL sobre el NSS.
        if criticality_verdict.has_critical_loss:
            return DoubleProtectionResult(
                verdict=RegressionVerdict.HARD_FAIL,
                nss_score=nss_score,
                criticality_signal=RegressionCriticalitySignal.ABSOLUTE_FAIL,
                critical_false_negatives=criticality_verdict.critical_false_negatives,
                warning_false_negatives=criticality_verdict.warning_false_negatives,
                info_false_negatives=criticality_verdict.info_false_negatives,
            )

        # ── Mecanismo 1: NSS ponderado (R8) ──
        nss_verdict = self._evaluate_nss(nss_score)

        # ── Complementariedad (R11): veredicto final = peor resultado ──
        if criticality_verdict.has_warning_loss:
            crit_verdict_enum = RegressionVerdict.WARNING
        else:
            crit_verdict_enum = RegressionVerdict.PASS

        final_verdict = max(
            nss_verdict,
            crit_verdict_enum,
            key=lambda v: v.severity_rank,
        )

        # La señal refleja el peor componente
        if final_verdict is RegressionVerdict.HARD_FAIL:
            final_signal = RegressionCriticalitySignal.ABSOLUTE_FAIL
        elif final_verdict is RegressionVerdict.WARNING:
            final_signal = RegressionCriticalitySignal.WARNING
        else:
            final_signal = RegressionCriticalitySignal.PASS

        return DoubleProtectionResult(
            verdict=final_verdict,
            nss_score=nss_score,
            criticality_signal=final_signal,
            critical_false_negatives=criticality_verdict.critical_false_negatives,
            warning_false_negatives=criticality_verdict.warning_false_negatives,
            info_false_negatives=criticality_verdict.info_false_negatives,
        )

    def _evaluate_nss(self, nss_score: float) -> RegressionVerdict:
        """Evalúa el NSS contra los umbrales (Mecanismo 1)."""
        if nss_score < self._thresholds.nss_hard_fail:
            return RegressionVerdict.HARD_FAIL
        if nss_score < self._thresholds.nss_warning:
            return RegressionVerdict.WARNING
        return RegressionVerdict.PASS

    @property
    def thresholds(self) -> RegressionThresholds:
        return self._thresholds