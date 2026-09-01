"""Tests del doble mecanismo de protección (NADR-19 §5.2 R8-R11)."""
from __future__ import annotations

import pytest

from core.benchmark.topology.criticality.verdict import CriticalityVerdict
from core.benchmark.topology.regression.errors import InvalidNSSScoreError
from core.benchmark.topology.regression.mechanism import DoubleProtectionMechanism
from core.benchmark.topology.regression.models import (
    RegressionCriticalitySignal,
    RegressionThresholds,
    RegressionVerdict,
)


def _make_cv(
    critical_fn: int = 0,
    warning_fn: int = 0,
    info_fn: int = 0,
) -> CriticalityVerdict:
    return CriticalityVerdict(
        has_critical_loss=critical_fn > 0,
        has_warning_loss=warning_fn > 0,
        has_info_loss=info_fn > 0,
        critical_false_negatives=critical_fn,
        warning_false_negatives=warning_fn,
        info_false_negatives=info_fn,
    )


class TestDoubleProtectionMechanism:
    @pytest.fixture
    def mechanism(self) -> DoubleProtectionMechanism:
        return DoubleProtectionMechanism()

    def test_no_loss_high_nss_returns_pass(self, mechanism):
        result = mechanism.evaluate(nss_score=0.98, criticality_verdict=_make_cv())
        assert result.verdict == RegressionVerdict.PASS
        assert result.criticality_signal == RegressionCriticalitySignal.PASS

    def test_critical_loss_hard_fail_regardless_of_nss(self, mechanism):
        """NADR-19 §5.2 R9-R10: Precedencia de CRITICAL."""
        result = mechanism.evaluate(nss_score=0.99, criticality_verdict=_make_cv(critical_fn=1))
        assert result.verdict == RegressionVerdict.HARD_FAIL
        assert result.criticality_signal == RegressionCriticalitySignal.ABSOLUTE_FAIL

    def test_canonical_1_critical_in_1000(self, mechanism):
        """NADR-19 §5.2 R11: Ejemplo canónico."""
        result = mechanism.evaluate(nss_score=0.999, criticality_verdict=_make_cv(critical_fn=1))
        assert result.verdict == RegressionVerdict.HARD_FAIL

    def test_nss_below_hard_fail_returns_hard_fail(self, mechanism):
        result = mechanism.evaluate(nss_score=0.75, criticality_verdict=_make_cv())
        assert result.verdict == RegressionVerdict.HARD_FAIL

    def test_nss_between_thresholds_returns_warning(self, mechanism):
        result = mechanism.evaluate(nss_score=0.90, criticality_verdict=_make_cv())
        assert result.verdict == RegressionVerdict.WARNING

    def test_warning_loss_returns_warning(self, mechanism):
        result = mechanism.evaluate(nss_score=0.98, criticality_verdict=_make_cv(warning_fn=2))
        assert result.verdict == RegressionVerdict.WARNING
        assert result.criticality_signal == RegressionCriticalitySignal.WARNING

    def test_info_loss_only_returns_pass(self, mechanism):
        result = mechanism.evaluate(nss_score=0.98, criticality_verdict=_make_cv(info_fn=5))
        assert result.verdict == RegressionVerdict.PASS

    def test_complementarity_worst_wins(self, mechanism):
        result = mechanism.evaluate(nss_score=0.90, criticality_verdict=_make_cv(warning_fn=1))
        assert result.verdict == RegressionVerdict.WARNING

    def test_custom_thresholds(self):
        custom = RegressionThresholds(nss_hard_fail=0.50, nss_warning=0.70)
        mechanism = DoubleProtectionMechanism(thresholds=custom)
        result = mechanism.evaluate(nss_score=0.60, criticality_verdict=_make_cv())
        assert result.verdict == RegressionVerdict.WARNING

    def test_invalid_nss_negative_raises(self, mechanism):
        with pytest.raises(InvalidNSSScoreError):
            mechanism.evaluate(nss_score=-0.1, criticality_verdict=_make_cv())

    def test_invalid_nss_above_one_raises(self, mechanism):
        with pytest.raises(InvalidNSSScoreError):
            mechanism.evaluate(nss_score=1.5, criticality_verdict=_make_cv())

    def test_invalid_nss_nan_raises(self, mechanism):
        with pytest.raises(InvalidNSSScoreError):
            mechanism.evaluate(nss_score=float("nan"), criticality_verdict=_make_cv())

    def test_invalid_nss_inf_raises(self, mechanism):
        with pytest.raises(InvalidNSSScoreError):
            mechanism.evaluate(nss_score=float("inf"), criticality_verdict=_make_cv())

    def test_boundary_nss_zero(self, mechanism):
        result = mechanism.evaluate(nss_score=0.0, criticality_verdict=_make_cv())
        assert result.verdict == RegressionVerdict.HARD_FAIL

    def test_boundary_nss_one(self, mechanism):
        result = mechanism.evaluate(nss_score=1.0, criticality_verdict=_make_cv())
        assert result.verdict == RegressionVerdict.PASS

    def test_result_is_immutable(self, mechanism):
        result = mechanism.evaluate(nss_score=0.98, criticality_verdict=_make_cv())
        with pytest.raises(AttributeError):
            result.verdict = RegressionVerdict.HARD_FAIL  # type: ignore[misc]

    def test_deterministic(self, mechanism):
        cv = _make_cv(warning_fn=1)
        r1 = mechanism.evaluate(nss_score=0.90, criticality_verdict=cv)
        r2 = mechanism.evaluate(nss_score=0.90, criticality_verdict=cv)
        assert r1 == r2