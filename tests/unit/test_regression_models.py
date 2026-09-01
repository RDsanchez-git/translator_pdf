"""Tests de RegressionVerdict, RegressionThresholds, Report y Signal.

CORRECCIÓN P1: overall_score es obligatorio, los tests se ajustan.
"""
from __future__ import annotations

import pytest

from core.benchmark.topology.regression.models import (
    DEFAULT_REGRESSION_THRESHOLDS,
    RegressionCriticalitySignal,
    RegressionEvaluationReport,
    RegressionThresholds,
    RegressionVerdict,
)


class TestRegressionVerdict:
    def test_exactly_three_levels(self):
        assert len(list(RegressionVerdict)) == 3

    def test_canonical_values(self):
        assert RegressionVerdict.HARD_FAIL == "HARD_FAIL"
        assert RegressionVerdict.WARNING == "WARNING"
        assert RegressionVerdict.PASS == "PASS"

    def test_str_subclass(self):
        assert isinstance(RegressionVerdict.PASS, str)

    def test_severity_rank_ordering(self):
        assert RegressionVerdict.HARD_FAIL.severity_rank > RegressionVerdict.WARNING.severity_rank
        assert RegressionVerdict.WARNING.severity_rank > RegressionVerdict.PASS.severity_rank

    def test_immutable(self):
        with pytest.raises(AttributeError):
            RegressionVerdict.PASS = "MODIFIED"  # type: ignore[misc]


class TestRegressionCriticalitySignal:
    def test_three_signals(self):
        assert len(list(RegressionCriticalitySignal)) == 3

    def test_canonical_values(self):
        assert RegressionCriticalitySignal.ABSOLUTE_FAIL == "ABSOLUTE_FAIL"
        assert RegressionCriticalitySignal.WARNING == "WARNING"
        assert RegressionCriticalitySignal.PASS == "PASS"

    def test_is_str_subclass(self):
        assert isinstance(RegressionCriticalitySignal.PASS, str)


class TestRegressionThresholds:
    def test_default_values(self):
        t = DEFAULT_REGRESSION_THRESHOLDS
        assert t.nss_hard_fail == 0.80
        assert t.nss_warning == 0.95

    def test_valid_custom(self):
        t = RegressionThresholds(nss_hard_fail=0.70, nss_warning=0.90)
        assert t.nss_hard_fail < t.nss_warning

    def test_invariant_violation_raises(self):
        with pytest.raises(ValueError, match="Invariant failure"):
            RegressionThresholds(nss_hard_fail=0.95, nss_warning=0.80)

    def test_equal_values_raises(self):
        with pytest.raises(ValueError, match="Invariant failure"):
            RegressionThresholds(nss_hard_fail=0.90, nss_warning=0.90)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="Invariant failure"):
            RegressionThresholds(nss_hard_fail=-0.1, nss_warning=0.90)

    def test_above_one_raises(self):
        with pytest.raises(ValueError, match="Invariant failure"):
            RegressionThresholds(nss_hard_fail=0.80, nss_warning=1.5)

    def test_immutable(self):
        with pytest.raises(AttributeError):
            DEFAULT_REGRESSION_THRESHOLDS.nss_hard_fail = 0.99  # type: ignore[misc]


class TestRegressionEvaluationReport:
    # P1: overall_score es obligatorio. Todos los tests lo proporcionan.

    def test_default_verdict_is_pass(self):
        report = RegressionEvaluationReport(
            document_id="doc1",
            metrics=(),
            overall_score=0.95,
        )
        assert report.verdict == RegressionVerdict.PASS
        assert report.is_pass is True

    def test_nss_score_is_alias_for_overall_score(self):
        report = RegressionEvaluationReport(
            document_id="doc1",
            metrics=(),
            overall_score=0.92,
        )
        assert report.nss_score == 0.92
        assert report.nss_score == report.overall_score

    def test_single_source_of_truth(self):
        """No hay divergencia: overall_score es la única fuente."""
        report = RegressionEvaluationReport(
            document_id="doc1",
            metrics=(),
            overall_score=0.92,
            verdict=RegressionVerdict.WARNING,
        )
        assert report.overall_score == report.nss_score == 0.92

    def test_to_topological_report_propagates_nss(self):
        report = RegressionEvaluationReport(
            document_id="doc1",
            metrics=(),
            overall_score=0.92,
            verdict=RegressionVerdict.WARNING,
        )
        topo = report.to_topological_report()
        assert topo.document_id == "doc1"
        assert topo.overall_score == 0.92

    def test_to_topological_report_loses_verdict(self):
        """El veredicto se pierde en la conversión a TopologicalEvaluationReport."""
        report = RegressionEvaluationReport(
            document_id="doc1",
            metrics=(),
            overall_score=0.50,
            verdict=RegressionVerdict.HARD_FAIL,
        )
        topo = report.to_topological_report()
        # TopologicalEvaluationReport no tiene campo verdict.
        assert not hasattr(topo, "verdict")

    def test_hard_fail_properties(self):
        report = RegressionEvaluationReport(
            document_id="doc1",
            metrics=(),
            overall_score=0.50,
            verdict=RegressionVerdict.HARD_FAIL,
        )
        assert report.is_hard_fail is True
        assert report.is_pass is False
        assert report.is_warning is False

    def test_immutable(self):
        report = RegressionEvaluationReport(
            document_id="doc1",
            metrics=(),
            overall_score=0.95,
        )
        with pytest.raises(AttributeError):
            report.document_id = "doc2"  # type: ignore[misc]

    def test_overall_score_is_required(self):
        """P1: overall_score es obligatorio (fail-fast)."""
        with pytest.raises(TypeError):
            RegressionEvaluationReport(document_id="doc1", metrics=())  # type: ignore[call-arg]