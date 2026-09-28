"""Tests de ContinuousVerificationReport (NADR-F17BIS-28 §5.3, §5.6)."""
from __future__ import annotations

import json

import pytest

from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.regression.models import RegressionVerdict
from core.benchmark.topology.regression.report import (
    RegressionEvaluationReport,
    RegressionReport,
)
from core.benchmark.topology.models import MetricScoreDTO
from core.benchmark.verification.identity_chain import (
    SCHEMA_VERSION,
    IdentityChain,
    build_identity_chain,
)
from core.benchmark.verification.outcome import (
    ContinuousVerificationResult,
    VerificationOutcome,
)
from core.benchmark.verification.report import (
    ContinuousVerificationReport,
    JsonContinuousVerificationReportFormatter,
)


def _build_sample_regression_report(
    config_fingerprint: str | None = "a" * 64,
) -> RegressionReport:
    """Helper: construye un RegressionReport mínimo para tests."""
    metric = MetricScoreDTO(
        metric_name="normalized_structural_score",
        primary_score=0.95,
        diagnostics=None,
    )
    eval_report = RegressionEvaluationReport(
        document_id="doc_01",
        metrics=(metric,),
        overall_score=0.95,
        verdict=RegressionVerdict.PASS,
    )
    return RegressionReport(
        corpus_version="v3.9",
        corpus_verdict=RegressionVerdict.PASS,
        corpus_nss=0.95,
        total_documents=1,
        pass_count=1,
        warning_count=0,
        hard_fail_count=0,
        document_reports=(eval_report,),
        total_critical_false_negatives=0,
        total_warning_false_negatives=0,
        total_info_false_negatives=0,
        generated_at=None,
        configuration_fingerprint=config_fingerprint,
    )


def _build_sample_identity_chain() -> IdentityChain:
    """Helper: construye una IdentityChain de prueba."""
    weights = {
        NodeCriticality.CRITICAL: 5.0,
        NodeCriticality.WARNING: 2.0,
        NodeCriticality.INFO: 1.0,
    }
    return build_identity_chain(
        baseline_identity="b" * 64,
        subject_identity="commit123",
        configuration_identity="c" * 64,
        cost_weights=weights,
        result_identity="d" * 64,
    )


def _build_sample_cv_result() -> ContinuousVerificationResult:
    """Helper: construye un ContinuousVerificationResult de prueba."""
    return ContinuousVerificationResult(
        outcome=VerificationOutcome.PASS,
        scientific_verdict=RegressionVerdict.PASS,
        reason="",
    )


@pytest.mark.unit
class TestContinuousVerificationReport:
    """NADR-F17BIS-28 §5.3 R14: reporte compuesto."""

    def test_report_has_all_components(self) -> None:
        """R14: Reporte tiene schema, identity, result, regression."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(),
        )
        assert report.schema_version == SCHEMA_VERSION
        assert report.identity_chain is not None
        assert report.operational_result is not None
        assert report.regression_report is not None

    def test_report_is_frozen(self) -> None:
        """Inmutable (ENGINEERING_PRINCIPLES §II)."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(),
        )
        with pytest.raises(AttributeError):
            report.schema_version = "modified"  # type: ignore[misc]

    def test_baseline_integrity_failure_has_no_regression_report(self) -> None:
        """R9: BASELINE_INTEGRITY_FAILURE no tiene regression_report."""
        result = ContinuousVerificationResult(
            outcome=VerificationOutcome.BASELINE_INTEGRITY_FAILURE,
            scientific_verdict=None,
            reason="manifest hash mismatch",
        )
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=result,
            regression_report=None,
        )
        assert report.regression_report is None


@pytest.mark.unit
class TestJsonFormatter:
    """NADR-F17BIS-28 §5.3 R14-R19, §5.6 R31-R34."""

    def test_json_contains_schema_version(self) -> None:
        """R24: schema_version está en el JSON."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(),
        )
        formatter = JsonContinuousVerificationReportFormatter()
        output = json.loads(formatter.format(report))
        assert output["schema_version"] == SCHEMA_VERSION

    def test_json_contains_identity_chain(self) -> None:
        """R15: identity chain está en el JSON."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(),
        )
        formatter = JsonContinuousVerificationReportFormatter()
        output = json.loads(formatter.format(report))
        chain = output["identity_chain"]
        assert "execution_id" in chain
        assert "baseline_identity" in chain
        assert "subject_identity" in chain
        assert "configuration_identity" in chain
        assert "parameter_identity" in chain
        assert "result_identity" in chain
        assert "limitations" in chain

    def test_json_contains_operational_result(self) -> None:
        """R16: resultado operacional está en el JSON."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(),
        )
        formatter = JsonContinuousVerificationReportFormatter()
        output = json.loads(formatter.format(report))
        result = output["operational_result"]
        assert result["outcome"] == "PASS"
        assert result["scientific_verdict"] == "PASS"
        assert result["exit_code"] == 0

    def test_json_contains_regression_report(self) -> None:
        """R17: regression_report con todos sus campos."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(),
        )
        formatter = JsonContinuousVerificationReportFormatter()
        output = json.loads(formatter.format(report))
        reg = output["regression_report"]
        assert reg["corpus_version"] == "v3.9"
        assert reg["corpus_verdict"] == "PASS"
        assert reg["corpus_nss"] == 0.95

    def test_configuration_fingerprint_is_serialized(self) -> None:
        """GAP-6.3-02: configuration_fingerprint ahora se serializa."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(
                config_fingerprint="abc123" * 10 + "abcd"
            ),
        )
        formatter = JsonContinuousVerificationReportFormatter()
        output = json.loads(formatter.format(report))
        assert "configuration_fingerprint" in output["regression_report"]
        assert output["regression_report"]["configuration_fingerprint"] == "abc123" * 10 + "abcd"

    def test_configuration_fingerprint_absent_when_none(self) -> None:
        """Backward compatibility: si None, no se incluye."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(
                config_fingerprint=None
            ),
        )
        formatter = JsonContinuousVerificationReportFormatter()
        output = json.loads(formatter.format(report))
        assert "configuration_fingerprint" not in output["regression_report"]

    def test_json_is_deterministic(self) -> None:
        """R8: Mismos inputs → mismo JSON."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(),
        )
        formatter = JsonContinuousVerificationReportFormatter()
        first = formatter.format(report)
        second = formatter.format(report)
        assert first == second

    def test_json_is_valid(self) -> None:
        """El output es JSON válido."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(),
        )
        formatter = JsonContinuousVerificationReportFormatter()
        output = formatter.format(report)
        parsed = json.loads(output)  # No lanza excepción
        assert isinstance(parsed, dict)

    def test_json_distinguishes_result_from_conditions(self) -> None:
        """R31: Resultado distinguible de condiciones."""
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=_build_sample_cv_result(),
            regression_report=_build_sample_regression_report(),
        )
        formatter = JsonContinuousVerificationReportFormatter()
        data = json.loads(formatter.format(report))

        # El resultado operacional está separado de la identity chain
        assert "operational_result" in data
        assert "identity_chain" in data
        assert "outcome" not in data["identity_chain"]
        assert "baseline_identity" not in data["operational_result"]

    def test_json_excludes_regression_report_when_none(self) -> None:
        """R9: Sin regression_report si no hay evaluación científica."""
        result = ContinuousVerificationResult(
            outcome=VerificationOutcome.BASELINE_INTEGRITY_FAILURE,
            scientific_verdict=None,
            reason="baseline corrupt",
        )
        report = ContinuousVerificationReport(
            schema_version=SCHEMA_VERSION,
            identity_chain=_build_sample_identity_chain(),
            operational_result=result,
            regression_report=None,
        )
        formatter = JsonContinuousVerificationReportFormatter()
        data = json.loads(formatter.format(report))
        assert "regression_report" not in data