"""Tests de taxonomía operacional (NADR-F17BIS-27 §5.1, §5.2, §5.6)."""
from __future__ import annotations

import pytest

from core.benchmark.topology.regression.models import RegressionVerdict
from core.benchmark.verification.outcome import (
    EXIT_BASELINE_INTEGRITY_FAILURE,
    EXIT_EXECUTION_FAILURE,
    EXIT_HARD_FAIL,
    EXIT_PASS,
    EXIT_WARNING,
    VerificationOutcome,
    map_scientific_verdict,
    outcome_to_exit_code,
)


from core.benchmark.verification.outcome import (
    ContinuousVerificationResult,
    resolve_operational_outcome,
)



@pytest.mark.unit
class TestVerificationOutcomeTaxonomy:
    """NADR-27 §5.2 R6-R7: taxonomía de 4 estados mutuamente distinguibles."""

    def test_exactly_four_outcomes(self) -> None:
        """R6: exactamente 4 estados."""
        assert len(VerificationOutcome) == 4

    def test_canonical_values(self) -> None:
        """R6: valores canónicos."""
        assert VerificationOutcome.PASS.value == "PASS"
        assert VerificationOutcome.REGRESSION.value == "REGRESSION"
        assert VerificationOutcome.BASELINE_INTEGRITY_FAILURE.value == "BASELINE_INTEGRITY_FAILURE"
        assert VerificationOutcome.EXECUTION_FAILURE.value == "EXECUTION_FAILURE"

    def test_outcomes_are_mutually_distinguishable(self) -> None:
        """R7: estados mutuamente distinguibles."""
        outcomes = list(VerificationOutcome)
        for i, a in enumerate(outcomes):
            for b in outcomes[i + 1:]:
                assert a is not b
                assert a != b

    def test_outcome_is_str_subclass(self) -> None:
        """Consistente con RegressionVerdict (ENGINEERING_PRINCIPLES §III)."""
        assert issubclass(VerificationOutcome, str)


@pytest.mark.unit
class TestMapScientificVerdict:
    """NADR-27 §5.1 R1: separación científico/operacional."""

    def test_pass_maps_to_pass(self) -> None:
        assert map_scientific_verdict(RegressionVerdict.PASS) is VerificationOutcome.PASS

    def test_warning_maps_to_regression(self) -> None:
        assert map_scientific_verdict(RegressionVerdict.WARNING) is VerificationOutcome.REGRESSION

    def test_hard_fail_maps_to_regression(self) -> None:
        assert map_scientific_verdict(RegressionVerdict.HARD_FAIL) is VerificationOutcome.REGRESSION


@pytest.mark.unit
class TestOutcomeToExitCode:
    """NADR-27 §5.6 R29-R33: traducción determinista."""

    def test_pass_returns_zero(self) -> None:
        assert outcome_to_exit_code(
            VerificationOutcome.PASS, RegressionVerdict.PASS
        ) == EXIT_PASS

    def test_regression_warning_returns_one(self) -> None:
        assert outcome_to_exit_code(
            VerificationOutcome.REGRESSION, RegressionVerdict.WARNING
        ) == EXIT_WARNING

    def test_regression_hard_fail_returns_two(self) -> None:
        assert outcome_to_exit_code(
            VerificationOutcome.REGRESSION, RegressionVerdict.HARD_FAIL
        ) == EXIT_HARD_FAIL

    def test_baseline_integrity_failure_returns_three(self) -> None:
        assert outcome_to_exit_code(
            VerificationOutcome.BASELINE_INTEGRITY_FAILURE
        ) == EXIT_BASELINE_INTEGRITY_FAILURE

    def test_execution_failure_returns_four(self) -> None:
        assert outcome_to_exit_code(
            VerificationOutcome.EXECUTION_FAILURE
        ) == EXIT_EXECUTION_FAILURE

    def test_exit_codes_are_mutually_distinct(self) -> None:
        """R30: exit codes mutuamente distintos."""
        codes = {EXIT_PASS, EXIT_WARNING, EXIT_HARD_FAIL,
                 EXIT_BASELINE_INTEGRITY_FAILURE, EXIT_EXECUTION_FAILURE}
        assert len(codes) == 5

    def test_outcome_to_exit_code_is_deterministic(self) -> None:
        """R29, R33: misma entrada → mismo exit code.

        Nota honesta: outcome_to_exit_code es una función pura sin I/O ni
        estado, por lo que este test es trivialmente verdadero. Su valor es
        documentar el contrato de determinismo de NADR-27 §5.6 R29/R33, no
        proveer una verificación robusta contra no-determinismo. La garantía
        real de determinismo proviene de que la función es pura por construcción.
        """
        test_cases = [
            (VerificationOutcome.PASS, RegressionVerdict.PASS),
            (VerificationOutcome.REGRESSION, RegressionVerdict.WARNING),
            (VerificationOutcome.REGRESSION, RegressionVerdict.HARD_FAIL),
            (VerificationOutcome.BASELINE_INTEGRITY_FAILURE, None),
            (VerificationOutcome.EXECUTION_FAILURE, None),
        ]
        for outcome, verdict in test_cases:
            first = outcome_to_exit_code(outcome, verdict)
            for _ in range(10):
                assert outcome_to_exit_code(outcome, verdict) == first


@pytest.mark.unit
class TestOutcomeInvariants:
    """NADR-27 §5.2 R8-R10: invariantes de separación."""

    def test_baseline_integrity_failure_rejects_scientific_verdict(self) -> None:
        """R8: BASELINE_INTEGRITY_FAILURE no lleva scientific_verdict."""
        with pytest.raises(ValueError, match="MUST NOT carry"):
            outcome_to_exit_code(
                VerificationOutcome.BASELINE_INTEGRITY_FAILURE,
                RegressionVerdict.PASS,
            )

    def test_execution_failure_rejects_scientific_verdict(self) -> None:
        """R9: EXECUTION_FAILURE no lleva scientific_verdict."""
        with pytest.raises(ValueError, match="MUST NOT carry"):
            outcome_to_exit_code(
                VerificationOutcome.EXECUTION_FAILURE,
                RegressionVerdict.PASS,
            )

    def test_regression_requires_scientific_verdict(self) -> None:
        """REGRESSION requiere scientific_verdict coherente."""
        with pytest.raises(ValueError, match="requires scientific_verdict"):
            outcome_to_exit_code(VerificationOutcome.REGRESSION)

    def test_pass_requires_pass_verdict(self) -> None:
        """PASS requiere scientific_verdict=PASS."""
        with pytest.raises(ValueError, match="requires scientific_verdict=PASS"):
            outcome_to_exit_code(
                VerificationOutcome.PASS, RegressionVerdict.WARNING
            )


@pytest.mark.unit
class TestContinuousVerificationResult:
    """NADR-27 §5.1 R1: resultado compuesto científico/operacional."""

    def test_pass_result_has_exit_code_zero(self) -> None:
        result = ContinuousVerificationResult(
            outcome=VerificationOutcome.PASS,
            scientific_verdict=RegressionVerdict.PASS,
            reason="",
        )
        assert result.exit_code == EXIT_PASS

    def test_exit_code_is_property_not_field(self) -> None:
        """DRY: exit_code es @property calculado, no campo almacenado."""
        result = ContinuousVerificationResult(
            outcome=VerificationOutcome.PASS,
            scientific_verdict=RegressionVerdict.PASS,
            reason="",
        )
        # exit_code no está en __dict__ del dataclass
        assert "exit_code" not in result.__dict__

    def test_baseline_integrity_failure_rejects_scientific_verdict(self) -> None:
        """R8: BASELINE_INTEGRITY_FAILURE no lleva scientific_verdict."""
        with pytest.raises(ValueError, match="MUST NOT carry"):
            ContinuousVerificationResult(
                outcome=VerificationOutcome.BASELINE_INTEGRITY_FAILURE,
                scientific_verdict=RegressionVerdict.PASS,
                reason="",
            )

    def test_execution_failure_rejects_scientific_verdict(self) -> None:
        """R9: EXECUTION_FAILURE no lleva scientific_verdict."""
        with pytest.raises(ValueError, match="MUST NOT carry"):
            ContinuousVerificationResult(
                outcome=VerificationOutcome.EXECUTION_FAILURE,
                scientific_verdict=RegressionVerdict.PASS,
                reason="",
            )


@pytest.mark.unit
class TestResolveOperationalOutcome:
    """NADR-27 §5.3 R11-R15: precedencia de evaluación."""

    def test_baseline_integrity_failure_has_precedence(self) -> None:
        """R11, R13: fallo de baseline tiene precedencia sobre todo."""
        result = resolve_operational_outcome(
            baseline_integrity_failed=True,
            execution_failed=True,
            scientific_verdict=RegressionVerdict.PASS,
            reason="baseline corrupt",
        )
        assert result.outcome is VerificationOutcome.BASELINE_INTEGRITY_FAILURE
        assert result.scientific_verdict is None
        assert result.exit_code == EXIT_BASELINE_INTEGRITY_FAILURE

    def test_execution_failure_has_precedence_over_scientific(self) -> None:
        """R14: fallo de ejecución tiene precedencia sobre evaluación."""
        result = resolve_operational_outcome(
            baseline_integrity_failed=False,
            execution_failed=True,
            scientific_verdict=RegressionVerdict.PASS,
            reason="pipeline crash",
        )
        assert result.outcome is VerificationOutcome.EXECUTION_FAILURE
        assert result.scientific_verdict is None
        assert result.exit_code == EXIT_EXECUTION_FAILURE

    def test_scientific_verdict_produces_outcome(self) -> None:
        """R12: evaluación científica produce PASS/REGRESSION."""
        result = resolve_operational_outcome(
            baseline_integrity_failed=False,
            execution_failed=False,
            scientific_verdict=RegressionVerdict.PASS,
        )
        assert result.outcome is VerificationOutcome.PASS
        assert result.scientific_verdict is RegressionVerdict.PASS
        assert result.exit_code == EXIT_PASS

    def test_no_scientific_verdict_is_execution_failure_not_pass(self) -> None:
        """R15: resultado parcial no es evaluación completa.

        scientific_verdict=None produce EXECUTION_FAILURE, no PASS.
        Esto previene interpretar "sin evaluación" como "sin regresión".
        """
        result = resolve_operational_outcome(
            baseline_integrity_failed=False,
            execution_failed=False,
            scientific_verdict=None,
            reason="no verdict produced",
        )
        assert result.outcome is VerificationOutcome.EXECUTION_FAILURE
        assert result.scientific_verdict is None
        assert result.exit_code == EXIT_EXECUTION_FAILURE

    def test_regression_verdict_maps_to_regression_outcome(self) -> None:
        """R12: HARD_FAIL científico produce REGRESSION operacional."""
        result = resolve_operational_outcome(
            baseline_integrity_failed=False,
            execution_failed=False,
            scientific_verdict=RegressionVerdict.HARD_FAIL,
        )
        assert result.outcome is VerificationOutcome.REGRESSION
        assert result.scientific_verdict is RegressionVerdict.HARD_FAIL
        assert result.exit_code == EXIT_HARD_FAIL