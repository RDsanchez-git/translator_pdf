"""
Tests unitarios del reporte de regresión (NADR-19 §5.7).

Verifica:
- NADR-19 §5.7 R26: Reporte incluye veredicto por documento y por corpus.
- NADR-19 §5.7 R27: NSS calculado, formato JSON válido.
- NADR-19 §5.7 R28: Formato Markdown legible.
- NADR-19 §5.7 R29: Determinismo y ausencia de timestamps no inyectados.
"""
from __future__ import annotations

import json

import pytest

from core.benchmark.topology.models import MetricScoreDTO, RecallDiagnostics
from core.benchmark.topology.regression.models import (
    RegressionCriticalitySignal,
    RegressionEvaluationReport,
    RegressionVerdict,
)
from core.benchmark.topology.regression.report import (
    JsonRegressionReportFormatter,
    MarkdownRegressionReportFormatter,
    RegressionReport,
    build_regression_report,
)


# =====================================================================
# Helpers
# =====================================================================


def _make_metric(
    metric_name: str = "normalized_structural_score",
    primary_score: float = 0.95,
) -> MetricScoreDTO:
    """Helper para crear MetricScoreDTO con RecallDiagnostics."""
    return MetricScoreDTO(
        metric_name=metric_name,
        primary_score=primary_score,
        diagnostics=RecallDiagnostics(
            precision=0.95,
            recall=0.90,
            true_positives=10,
            false_positives=1,
            false_negatives=1,
        ),
    )


def _make_eval_report(
    document_id: str = "doc1",
    nss_score: float = 0.95,
    verdict: RegressionVerdict = RegressionVerdict.PASS,
    signal: RegressionCriticalitySignal = RegressionCriticalitySignal.PASS,
    critical_fn: int = 0,
    warning_fn: int = 0,
    info_fn: int = 0,
) -> RegressionEvaluationReport:
    """Helper para construir RegressionEvaluationReport de prueba."""
    return RegressionEvaluationReport(
        document_id=document_id,
        metrics=(_make_metric(primary_score=nss_score),),
        overall_score=nss_score,
        verdict=verdict,
        criticality_signal=signal,
        critical_false_negatives=critical_fn,
        warning_false_negatives=warning_fn,
        info_false_negatives=info_fn,
    )


# =====================================================================
# build_regression_report()
# =====================================================================


class TestBuildRegressionReport:
    """Tests de build_regression_report()."""

    def test_single_document_pass(self):
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report()],
        )
        assert report.corpus_verdict is RegressionVerdict.PASS
        assert report.total_documents == 1
        assert report.pass_count == 1
        assert report.warning_count == 0
        assert report.hard_fail_count == 0

    def test_corpus_verdict_is_worst(self):
        """NADR-19 §5.1 R3: veredicto por corpus = peor veredicto."""
        reports = [
            _make_eval_report(document_id="doc1", verdict=RegressionVerdict.PASS),
            _make_eval_report(document_id="doc2", verdict=RegressionVerdict.WARNING),
            _make_eval_report(document_id="doc3", verdict=RegressionVerdict.HARD_FAIL),
        ]
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=reports,
        )
        assert report.corpus_verdict is RegressionVerdict.HARD_FAIL

    def test_corpus_nss_is_average(self):
        """NADR-19 §5.7 R27: NSS calculado como promedio."""
        reports = [
            _make_eval_report(document_id="doc1", nss_score=0.90),
            _make_eval_report(document_id="doc2", nss_score=0.80),
        ]
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=reports,
        )
        assert report.corpus_nss == pytest.approx(0.85)

    def test_all_warning_no_hard_fail_returns_warning(self):
        reports = [
            _make_eval_report(document_id="doc1", verdict=RegressionVerdict.PASS),
            _make_eval_report(document_id="doc2", verdict=RegressionVerdict.WARNING),
        ]
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=reports,
        )
        assert report.corpus_verdict is RegressionVerdict.WARNING

    def test_empty_reports_raises(self):
        with pytest.raises(ValueError, match="empty"):
            build_regression_report(
                corpus_version="calibration_v1",
                evaluation_reports=[],
            )

    def test_false_negatives_summed(self):
        reports = [
            _make_eval_report(document_id="doc1", critical_fn=1, warning_fn=2, info_fn=3),
            _make_eval_report(document_id="doc2", critical_fn=0, warning_fn=1, info_fn=5),
        ]
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=reports,
        )
        assert report.total_critical_false_negatives == 1
        assert report.total_warning_false_negatives == 3
        assert report.total_info_false_negatives == 8

    def test_report_is_immutable(self):
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report()],
        )
        with pytest.raises(AttributeError):
            report.corpus_version = "modified"  # type: ignore[misc]

    def test_document_reports_preserve_order(self):
        reports = [
            _make_eval_report(document_id="doc1"),
            _make_eval_report(document_id="doc2"),
            _make_eval_report(document_id="doc3"),
        ]
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=reports,
        )
        doc_ids = [r.document_id for r in report.document_reports]
        assert doc_ids == ["doc1", "doc2", "doc3"]

    def test_corpus_version_preserved(self):
        report = build_regression_report(
            corpus_version="calibration_v2",
            evaluation_reports=[_make_eval_report()],
        )
        assert report.corpus_version == "calibration_v2"

    def test_generated_at_default_none(self):
        """NADR-19 §5.7 R29: default None → determinismo total."""
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report()],
        )
        assert report.generated_at is None

    def test_generated_at_injected(self):
        """NADR-19 §5.7 R29: timestamp inyectado externamente."""
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report()],
            generated_at="2026-08-30T00:00:00Z",
        )
        assert report.generated_at == "2026-08-30T00:00:00Z"

    def test_deterministic(self):
        """Mismo input → mismo reporte."""
        reports = [_make_eval_report(document_id="doc1")]
        r1 = build_regression_report("v1", reports)
        r2 = build_regression_report("v1", reports)
        assert r1 == r2


# =====================================================================
# JsonRegressionReportFormatter
# =====================================================================


class TestJsonRegressionReportFormatter:
    """Tests de JsonRegressionReportFormatter (NADR-19 §5.7 R27)."""

    @pytest.fixture
    def formatter(self) -> JsonRegressionReportFormatter:
        return JsonRegressionReportFormatter()

    @pytest.fixture
    def report(self) -> RegressionReport:
        return build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report(document_id="doc1")],
        )

    def test_format_is_valid_json(self, formatter, report):
        output = formatter.format(report)
        data = json.loads(output)
        assert isinstance(data, dict)

    def test_json_contains_required_fields(self, formatter, report):
        data = json.loads(formatter.format(report))
        assert data["corpus_version"] == "calibration_v1"
        assert data["corpus_verdict"] == "PASS"
        assert data["total_documents"] == 1
        assert "documents" in data
        assert data["documents"][0]["document_id"] == "doc1"

    def test_json_contains_corpus_nss(self, formatter):
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[
                _make_eval_report(nss_score=0.90),
                _make_eval_report(document_id="doc2", nss_score=0.80),
            ],
        )
        data = json.loads(formatter.format(report))
        assert data["corpus_nss"] == pytest.approx(0.85)

    def test_json_contains_nss_score_per_document(self, formatter):
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report(nss_score=0.92)],
        )
        data = json.loads(formatter.format(report))
        assert data["documents"][0]["overall_score"] == pytest.approx(0.92)

    def test_json_is_deterministic(self, formatter, report):
        """NADR-19 §5.7 R29: mismo input → mismo output."""
        output1 = formatter.format(report)
        output2 = formatter.format(report)
        assert output1 == output2

    def test_json_no_timestamp_when_none(self, formatter, report):
        """NADR-19 §5.7 R29: sin timestamp si no fue inyectado."""
        data = json.loads(formatter.format(report))
        assert data["generated_at"] is None

    def test_json_with_injected_timestamp(self, formatter):
        """NADR-19 §5.7 R29: timestamp inyectado aparece en JSON."""
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report()],
            generated_at="2026-08-30T00:00:00Z",
        )
        data = json.loads(formatter.format(report))
        assert data["generated_at"] == "2026-08-30T00:00:00Z"

    def test_json_contains_serialized_diagnostics(self, formatter, report):
        """Verifica que diagnostics se serializa correctamente."""
        data = json.loads(formatter.format(report))
        diagnostics = data["documents"][0]["metrics"][0]["diagnostics"]
        assert diagnostics["precision"] == pytest.approx(0.95)
        assert diagnostics["recall"] == pytest.approx(0.90)
        assert diagnostics["true_positives"] == 10

    def test_hard_fail_verdict_serialized(self, formatter):
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[
                _make_eval_report(
                    verdict=RegressionVerdict.HARD_FAIL,
                    signal=RegressionCriticalitySignal.ABSOLUTE_FAIL,
                    critical_fn=1,
                )
            ],
        )
        data = json.loads(formatter.format(report))
        assert data["corpus_verdict"] == "HARD_FAIL"
        assert data["documents"][0]["verdict"] == "HARD_FAIL"
        assert data["documents"][0]["criticality_signal"] == "ABSOLUTE_FAIL"
        assert data["documents"][0]["critical_false_negatives"] == 1


# =====================================================================
# MarkdownRegressionReportFormatter
# =====================================================================


class TestMarkdownRegressionReportFormatter:
    """Tests de MarkdownRegressionReportFormatter (NADR-19 §5.7 R28)."""

    @pytest.fixture
    def formatter(self) -> MarkdownRegressionReportFormatter:
        return MarkdownRegressionReportFormatter()

    @pytest.fixture
    def report(self) -> RegressionReport:
        return build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report(document_id="doc1")],
        )

    def test_markdown_contains_header(self, formatter, report):
        output = formatter.format(report)
        assert "# Regression Report" in output
        assert "calibration_v1" in output

    def test_markdown_contains_corpus_nss(self, formatter):
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report(nss_score=0.92)],
        )
        output = formatter.format(report)
        assert "0.9200" in output

    def test_markdown_contains_verdict(self, formatter):
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[
                _make_eval_report(verdict=RegressionVerdict.HARD_FAIL)
            ],
        )
        output = formatter.format(report)
        assert "HARD_FAIL" in output

    def test_markdown_contains_document_table(self, formatter, report):
        output = formatter.format(report)
        assert "| Document |" in output
        assert "`doc1`" in output

    def test_markdown_contains_criticality_summary(self, formatter):
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[
                _make_eval_report(critical_fn=2, warning_fn=1, info_fn=3)
            ],
        )
        output = formatter.format(report)
        assert "## Criticality Loss Summary" in output
        assert "| CRITICAL | 2 |" in output
        assert "| WARNING | 1 |" in output
        assert "| INFO | 3 |" in output

    def test_markdown_is_deterministic(self, formatter, report):
        """NADR-19 §5.7 R29: mismo input → mismo output."""
        output1 = formatter.format(report)
        output2 = formatter.format(report)
        assert output1 == output2

    def test_markdown_no_timestamp_when_none(self, formatter, report):
        """NADR-19 §5.7 R29: sin timestamp si no fue inyectado."""
        output = formatter.format(report)
        assert "Generated At" not in output

    def test_markdown_with_injected_timestamp(self, formatter):
        """NADR-19 §5.7 R29: timestamp inyectado aparece en Markdown."""
        report = build_regression_report(
            corpus_version="calibration_v1",
            evaluation_reports=[_make_eval_report()],
            generated_at="2026-08-30T00:00:00Z",
        )
        output = formatter.format(report)
        assert "Generated At" in output
        assert "2026-08-30T00:00:00Z" in output