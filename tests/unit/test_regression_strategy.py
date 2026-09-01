"""Tests de RegressionEvaluationStrategy (strategy REAL de producción).

CORRECCIONES P2:
- spec=EntityRecallEvaluator en mocks para que fallen si la interfaz cambia.
- spec=TreeEditDistanceEvaluator en mock de TED.
- Test de recall_evaluators vacío (fail-fast en __init__).
"""
from __future__ import annotations

from typing import Mapping
from unittest.mock import MagicMock

import pytest

from core.ast.enums import ContentNodeType
from core.benchmark.topology.criticality.verdict import CriticalityVerdictEmitter
from core.benchmark.topology.evaluators.recall import EntityRecallEvaluator
from core.benchmark.topology.evaluators.ted import TreeEditDistanceEvaluator
from core.benchmark.topology.models import (
    MetricScoreDTO,
    RecallDiagnostics,
    TedDiagnostics,
    TopologicalEvaluationReport,
)
from core.benchmark.topology.regression.mechanism import DoubleProtectionMechanism
from core.benchmark.topology.regression.models import (
    RegressionCriticalitySignal,
    RegressionThresholds,
    RegressionVerdict,
)
from core.benchmark.topology.regression.strategy import RegressionEvaluationStrategy


def _make_mock_ted(nss_score: float) -> MagicMock:
    """Crea un mock de TreeEditDistanceEvaluator con NSS controlado."""
    # P2: spec=TreeEditDistanceEvaluator para que el test falle
    # si la interfaz cambia.
    mock = MagicMock(spec=TreeEditDistanceEvaluator)
    mock.evaluate.return_value = MetricScoreDTO(
        metric_name="normalized_structural_score",
        primary_score=nss_score,
        diagnostics=TedDiagnostics(
            global_ted=10.0,
            total_windows_evaluated=1,
            overflow_triggered=False,
        ),
    )
    return mock


def _make_mock_recall_evaluators(
    false_negatives_by_type: dict[ContentNodeType, int] | None = None,
) -> Mapping[ContentNodeType, MagicMock]:
    """Crea mocks de EntityRecallEvaluator mapeados por tipo."""
    if false_negatives_by_type is None:
        false_negatives_by_type = {}

    evaluators: dict[ContentNodeType, MagicMock] = {}
    for node_type in ContentNodeType:
        fn = false_negatives_by_type.get(node_type, 0)
        # P2: spec=EntityRecallEvaluator para que el test falle
        # si la interfaz cambia.
        mock = MagicMock(spec=EntityRecallEvaluator)
        mock.evaluate.return_value = MetricScoreDTO(
            metric_name=f"f1_score_{node_type.value}",
            primary_score=0.95,
            diagnostics=RecallDiagnostics(
                precision=0.95,
                recall=0.95,
                true_positives=10,
                false_positives=0,
                false_negatives=fn,
            ),
        )
        evaluators[node_type] = mock
    return evaluators


class TestRegressionEvaluationStrategyInit:
    """Tests de validación en __init__."""

    def test_empty_recall_evaluators_raises(self):
        """P2: recall_evaluators vacío → ValueError (fail-fast)."""
        with pytest.raises(ValueError, match="must not be empty"):
            RegressionEvaluationStrategy(
                ted_evaluator=_make_mock_ted(nss_score=0.98),
                recall_evaluators={},
            )


class TestRegressionEvaluationStrategy:
    def test_pass_when_no_losses_high_nss(self):
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.98),
            recall_evaluators=_make_mock_recall_evaluators(),
        )
        report = strategy.evaluate_regression("doc1", [], [])
        assert report.verdict == RegressionVerdict.PASS
        assert report.is_pass is True
        assert report.nss_score == 0.98
        assert report.criticality_signal == RegressionCriticalitySignal.PASS

    def test_hard_fail_on_critical_loss(self):
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.99),
            recall_evaluators=_make_mock_recall_evaluators(
                false_negatives_by_type={ContentNodeType.DISPLAY_EQUATION: 1}
            ),
        )
        report = strategy.evaluate_regression("doc1", [], [])
        assert report.verdict == RegressionVerdict.HARD_FAIL
        assert report.criticality_signal == RegressionCriticalitySignal.ABSOLUTE_FAIL
        assert report.critical_false_negatives == 1

    def test_warning_on_low_nss(self):
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.90),
            recall_evaluators=_make_mock_recall_evaluators(),
        )
        report = strategy.evaluate_regression("doc1", [], [])
        assert report.verdict == RegressionVerdict.WARNING

    def test_hard_fail_on_very_low_nss(self):
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.50),
            recall_evaluators=_make_mock_recall_evaluators(),
        )
        report = strategy.evaluate_regression("doc1", [], [])
        assert report.verdict == RegressionVerdict.HARD_FAIL

    def test_warning_on_warning_loss(self):
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.98),
            recall_evaluators=_make_mock_recall_evaluators(
                false_negatives_by_type={ContentNodeType.PARAGRAPH: 2}
            ),
        )
        report = strategy.evaluate_regression("doc1", [], [])
        assert report.verdict == RegressionVerdict.WARNING
        assert report.warning_false_negatives == 2

    def test_info_loss_does_not_fail(self):
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.98),
            recall_evaluators=_make_mock_recall_evaluators(
                false_negatives_by_type={ContentNodeType.IMAGE: 10}
            ),
        )
        report = strategy.evaluate_regression("doc1", [], [])
        assert report.verdict == RegressionVerdict.PASS
        assert report.info_false_negatives == 10

    def test_evaluate_run_returns_topological_report(self):
        """evaluate_run cumple el protocolo EvaluationStrategy."""
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.98),
            recall_evaluators=_make_mock_recall_evaluators(),
        )
        report = strategy.evaluate_run("doc1", [], [])
        assert isinstance(report, TopologicalEvaluationReport)
        assert report.document_id == "doc1"
        assert report.overall_score == 0.98

    def test_evaluate_run_propagates_nss(self):
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.92),
            recall_evaluators=_make_mock_recall_evaluators(),
        )
        topo = strategy.evaluate_run("doc1", [], [])
        assert topo.overall_score == 0.92

    def test_evaluate_run_loses_verdict(self):
        """El veredicto se pierde en evaluate_run (usar evaluate_regression)."""
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.50),
            recall_evaluators=_make_mock_recall_evaluators(),
        )
        topo = strategy.evaluate_run("doc1", [], [])
        # TopologicalEvaluationReport no tiene campo verdict.
        assert not hasattr(topo, "verdict")

    def test_metrics_include_ted_and_recall(self):
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.98),
            recall_evaluators=_make_mock_recall_evaluators(),
        )
        report = strategy.evaluate_regression("doc1", [], [])
        metric_names = [m.metric_name for m in report.metrics]
        assert "normalized_structural_score" in metric_names
        assert any("f1_score_" in name for name in metric_names)

    def test_recall_evaluators_called_exactly_once(self):
        """P0-1: Cada evaluador se llama UNA sola vez."""
        recall_evaluators = _make_mock_recall_evaluators()
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.98),
            recall_evaluators=recall_evaluators,
        )
        strategy.evaluate_regression("doc1", [], [])

        for node_type, evaluator in recall_evaluators.items():
            assert evaluator.evaluate.call_count == 1, (
                f"EntityRecallEvaluator for {node_type} was called "
                f"{evaluator.evaluate.call_count} times, expected 1."
            )

    def test_deterministic(self):
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.90),
            recall_evaluators=_make_mock_recall_evaluators(),
        )
        r1 = strategy.evaluate_regression("doc1", [], [])
        r2 = strategy.evaluate_regression("doc1", [], [])
        assert r1 == r2

    def test_custom_thresholds(self):
        thresholds = RegressionThresholds(nss_hard_fail=0.50, nss_warning=0.70)
        mechanism = DoubleProtectionMechanism(thresholds=thresholds)
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.60),
            recall_evaluators=_make_mock_recall_evaluators(),
            mechanism=mechanism,
        )
        report = strategy.evaluate_regression("doc1", [], [])
        assert report.verdict == RegressionVerdict.WARNING

    def test_custom_verdict_emitter(self):
        emitter = CriticalityVerdictEmitter(warning_threshold=5)
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.98),
            recall_evaluators=_make_mock_recall_evaluators(
                false_negatives_by_type={ContentNodeType.PARAGRAPH: 3}
            ),
            verdict_emitter=emitter,
        )
        report = strategy.evaluate_regression("doc1", [], [])
        # 3 FNs < threshold 5 → no warning loss
        assert report.verdict == RegressionVerdict.PASS

    def test_no_string_parsing_for_node_type(self):
        """El dict mapping evita parsing de metric_name."""
        strategy = RegressionEvaluationStrategy(
            ted_evaluator=_make_mock_ted(nss_score=0.98),
            recall_evaluators=_make_mock_recall_evaluators(
                false_negatives_by_type={ContentNodeType.DISPLAY_EQUATION: 1}
            ),
        )
        report = strategy.evaluate_regression("doc1", [], [])
        # El tipo se extrae del dict, no del metric_name
        assert report.critical_false_negatives == 1