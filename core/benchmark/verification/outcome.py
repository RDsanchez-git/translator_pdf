"""Semántica operacional de Continuous Verification (NADR-F17BIS-27).

NADR-F17BIS-27 §5.1 R1: Continuous Verification MUST distinguir entre el
resultado de la evaluación científica y el estado operacional de la ejecución.

NADR-F17BIS-27 §5.2 R6: El resultado de Continuous Verification MUST
pertenecer a una taxonomía determinista que distinga, como mínimo:
- PASS: evaluación completada y sin condición de divergencia.
- REGRESSION: evaluación completada y evidencia de divergencia.
- BASELINE_INTEGRITY_FAILURE: la referencia no pudo demostrarse íntegra.
- EXECUTION_FAILURE: la evaluación no pudo completarse.

Separación de bounded contexts:
- core/benchmark/topology/regression/ → NADR-F17BIS-19 (mecanismo científico)
- core/benchmark/verification/ → NADR-F17BIS-27 (semántica operacional)

Nota sobre §5.4 R16-R23 (Conformance/Regression):
Estas reglas establecen que Conformance y Regression son dimensiones
conceptualmente distintas. Actualmente solo existe Regression (NADR-19).
Esta taxonomía permite representar ambas independientemente si Conformance
se agrega en el futuro, sin colapsar dimensiones. No se implementa
Conformance ahora (YAGNI — no hay necesidad demostrada).
"""
from __future__ import annotations

from enum import Enum

from core.benchmark.topology.regression.models import RegressionVerdict

from dataclasses import dataclass


class VerificationOutcome(str, Enum):
    """Taxonomía operacional de Continuous Verification (NADR-27 §5.2 R6).

    Cuatro estados mutuamente distinguibles (R7):
    - PASS: evaluación completada, sin divergencia que active criterio de fallo.
    - REGRESSION: evaluación completada, evidencia de divergencia.
    - BASELINE_INTEGRITY_FAILURE: referencia no demostrada íntegra.
    - EXECUTION_FAILURE: evaluación no completada por condición operacional.

    Invariantes (R8, R9, R10):
    - BASELINE_INTEGRITY_FAILURE ≠ REGRESSION (R8)
    - EXECUTION_FAILURE ≠ PASS (R9)
    - EXECUTION_FAILURE ≠ REGRESSION (R10)
    """

    PASS = "PASS"
    REGRESSION = "REGRESSION"
    BASELINE_INTEGRITY_FAILURE = "BASELINE_INTEGRITY_FAILURE"
    EXECUTION_FAILURE = "EXECUTION_FAILURE"


# Exit codes (NADR-27 §5.6 R29-R33).
# Traducción determinista outcome → exit code.
# NOTA: estas constantes son la fuente de verdad para Task 2.1.3, que
# refactorizará run_regression.py para importarlas desde aquí y eliminar
# las definiciones locales duplicadas.
EXIT_PASS = 0
EXIT_WARNING = 1  # REGRESSION leve (scientific_verdict=WARNING)
EXIT_HARD_FAIL = 2  # REGRESSION severa (scientific_verdict=HARD_FAIL)
EXIT_BASELINE_INTEGRITY_FAILURE = 3  # Gate 1
EXIT_EXECUTION_FAILURE = 4  # Task 2.1.3 (nuevo)


def map_scientific_verdict(verdict: RegressionVerdict) -> VerificationOutcome:
    """Mapea el veredicto científico (NADR-19) al estado operacional (NADR-27).

    NADR-27 §5.1 R1: separación resultado científico vs estado operacional.
    NADR-27 §5.6 R33: traducción determinista y verificable.

    Mapeo:
    - RegressionVerdict.PASS → VerificationOutcome.PASS
    - RegressionVerdict.WARNING → VerificationOutcome.REGRESSION
    - RegressionVerdict.HARD_FAIL → VerificationOutcome.REGRESSION

    Nota: WARNING y HARD_FAIL son ambos REGRESSION operacionalmente.
    La severidad se preserva en el scientific_verdict que acompaña al
    resultado operacional. CI decide si un REGRESSION leve bloquea merge
    o no (eso es NADR-30, Gate 4).

    Args:
        verdict: Veredicto científico de NADR-19.

    Returns:
        Estado operacional correspondiente.
    """
    if verdict is RegressionVerdict.PASS:
        return VerificationOutcome.PASS
    return VerificationOutcome.REGRESSION


def outcome_to_exit_code(
    outcome: VerificationOutcome,
    scientific_verdict: RegressionVerdict | None = None,
) -> int:
    """Traducción determinista outcome → exit code (NADR-27 §5.6 R29-R33).

    NADR-27 §5.6 R30: un mismo exit code MUST NOT representar
    simultáneamente estados operacionales incompatibles.

    Args:
        outcome: Estado operacional.
        scientific_verdict: Veredicto científico (solo si outcome es PASS
            o REGRESSION). None para BASELINE_INTEGRITY_FAILURE y
            EXECUTION_FAILURE.

    Returns:
        Exit code determinista.

    Raises:
        ValueError: Si outcome es PASS o REGRESSION sin scientific_verdict
            coherente, o si outcome es BASELINE_INTEGRITY_FAILURE o
            EXECUTION_FAILURE con scientific_verdict.
    """
    if outcome is VerificationOutcome.PASS:
        if scientific_verdict is not RegressionVerdict.PASS:
            raise ValueError(
                f"PASS outcome requires scientific_verdict=PASS, "
                f"got {scientific_verdict}."
            )
        return EXIT_PASS

    if outcome is VerificationOutcome.REGRESSION:
        if scientific_verdict not in (
            RegressionVerdict.WARNING,
            RegressionVerdict.HARD_FAIL,
        ):
            raise ValueError(
                f"REGRESSION outcome requires scientific_verdict in "
                f"(WARNING, HARD_FAIL), got {scientific_verdict}."
            )
        if scientific_verdict is RegressionVerdict.HARD_FAIL:
            return EXIT_HARD_FAIL
        return EXIT_WARNING

    if outcome is VerificationOutcome.BASELINE_INTEGRITY_FAILURE:
        if scientific_verdict is not None:
            raise ValueError(
                "BASELINE_INTEGRITY_FAILURE outcome MUST NOT carry "
                "scientific_verdict (NADR-27 §5.2 R8)."
            )
        return EXIT_BASELINE_INTEGRITY_FAILURE

    if outcome is VerificationOutcome.EXECUTION_FAILURE:
        if scientific_verdict is not None:
            raise ValueError(
                "EXECUTION_FAILURE outcome MUST NOT carry "
                "scientific_verdict (NADR-27 §5.2 R9)."
            )
        return EXIT_EXECUTION_FAILURE

    raise ValueError(f"Unknown outcome: {outcome}")




@dataclass(frozen=True)
class ContinuousVerificationResult:
    """Resultado operacional completo de Continuous Verification.

    NADR-F17BIS-27 §5.1 R1: separación resultado científico vs estado
    operacional. Este dataclass encapsula ambos.

    NADR-F17BIS-27 §5.2 R8-R10: invariantes de separación.
    BASELINE_INTEGRITY_FAILURE y EXECUTION_FAILURE MUST NOT llevar
    scientific_verdict.

    El exit_code es un @property calculado, no un campo almacenado.
    Esto mantiene una única fuente de verdad (DRY) y previene divergencia
    entre outcome y exit_code.

    El @property nunca lanza excepción porque __post_init__ valida
    invariantes antes de que el objeto sea construido.
    """

    outcome: VerificationOutcome
    scientific_verdict: RegressionVerdict | None
    reason: str

    def __post_init__(self) -> None:
        """Valida invariantes NADR-27 §5.2 R8-R10."""
        if self.outcome in (
            VerificationOutcome.BASELINE_INTEGRITY_FAILURE,
            VerificationOutcome.EXECUTION_FAILURE,
        ):
            if self.scientific_verdict is not None:
                raise ValueError(
                    f"{self.outcome.value} outcome MUST NOT carry "
                    f"scientific_verdict (NADR-27 §5.2 R8-R9)."
                )

        if self.outcome is VerificationOutcome.PASS:
            if self.scientific_verdict is not RegressionVerdict.PASS:
                raise ValueError(
                    f"PASS outcome requires scientific_verdict=PASS, "
                    f"got {self.scientific_verdict}."
                )

        if self.outcome is VerificationOutcome.REGRESSION:
            if self.scientific_verdict not in (
                RegressionVerdict.WARNING,
                RegressionVerdict.HARD_FAIL,
            ):
                raise ValueError(
                    f"REGRESSION outcome requires scientific_verdict in "
                    f"(WARNING, HARD_FAIL), got {self.scientific_verdict}."
                )

    @property
    def exit_code(self) -> int:
        """Exit code calculado on-demand (DRY).

        Nunca lanza excepción porque __post_init__ valida invariantes.
        """
        return outcome_to_exit_code(self.outcome, self.scientific_verdict)


def resolve_operational_outcome(
    *,
    baseline_integrity_failed: bool,
    execution_failed: bool,
    scientific_verdict: RegressionVerdict | None,
    reason: str = "",
) -> ContinuousVerificationResult:
    """Resuelve el outcome operacional según precedencia (NADR-27 §5.3 R11-R15).

    Precedencia (R11-R15):
    1. Precondiciones de baseline → BASELINE_INTEGRITY_FAILURE (R11, R13)
    2. Ejecución → EXECUTION_FAILURE (R14)
    3. Evaluación científica → PASS/REGRESSION (R12, R15)

    NADR-27 §5.3 R15: un resultado parcial (scientific_verdict=None)
    MUST NOT presentarse como evaluación científica completa. Se traduce
    a EXECUTION_FAILURE, no a PASS. Esto previene interpretar "sin
    evaluación" como "sin regresión".

    Functional Core: usa booleanos en lugar de Exception para no acoplar
    a tipos de runtime. El Imperative Shell captura excepciones y traduce
    a booleanos antes de llamar esta función.

    Args:
        baseline_integrity_failed: True si precondiciones de baseline fallaron.
        execution_failed: True si la ejecución falló.
        scientific_verdict: Veredicto científico, o None si no se completó.
        reason: Motivo del fallo (cuando outcome ≠ PASS).

    Returns:
        ContinuousVerificationResult con el outcome operacional.
    """
    # Precedencia 1: fallo de integridad de baseline (R11, R13)
    if baseline_integrity_failed:
        return ContinuousVerificationResult(
            outcome=VerificationOutcome.BASELINE_INTEGRITY_FAILURE,
            scientific_verdict=None,
            reason=reason,
        )

    # Precedencia 2: fallo de ejecución (R14)
    if execution_failed:
        return ContinuousVerificationResult(
            outcome=VerificationOutcome.EXECUTION_FAILURE,
            scientific_verdict=None,
            reason=reason,
        )

    # Precedencia 3: evaluación científica (R12, R15)
    if scientific_verdict is None:
        # R15: resultado parcial no es evaluación completa
        return ContinuousVerificationResult(
            outcome=VerificationOutcome.EXECUTION_FAILURE,
            scientific_verdict=None,
            reason=reason or "No scientific verdict produced",
        )

    outcome = map_scientific_verdict(scientific_verdict)
    return ContinuousVerificationResult(
        outcome=outcome,
        scientific_verdict=scientific_verdict,
        reason=reason,
    )