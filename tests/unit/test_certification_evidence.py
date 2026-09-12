"""Tests de Certification Evidence y POST-RUN VALIDATION (NADR-24 R29-R31, R36-R37)."""
from __future__ import annotations

import json
from typing import Any

import pytest

from core.benchmark.certification.evidence import (
    CertificationEvidence,
    DocumentResultEvidence,
    compute_corpus_content_identity,
    serialize_evidence,
)
from core.benchmark.certification.post_run import (
    ELEMENT_AGGREGATE_RESULT,
    ELEMENT_CONFIGURATION_IDENTITY,
    ELEMENT_CORPUS_IDENTITY,
    ELEMENT_EVALUATION_PROVENANCE,
    ELEMENT_FROZEN_PARAMETERS_IDENTITY,
    ELEMENT_MANIFEST_IDENTITY,
    ELEMENT_PER_DOCUMENT_RESULTS,
    PostRunReport,
    validate_post_run,
)

SHA_A = "a" * 64
SHA_B = "b" * 64


def _evidence(**overrides: Any) -> CertificationEvidence:
    base: dict[str, Any] = dict(
        corpus_identity="C",
        manifest_identity="M",
        configuration_identity="K",
        frozen_parameters_identity="P",
        evaluation_provenance_reference="reports/calibration/evaluation_provenance_record_SANITY_VALIDATION.json",
        per_document_results=(
            DocumentResultEvidence(document_id="doc-1", verdict="PASS", nss_score=1.0),
            DocumentResultEvidence(document_id="doc-2", verdict="HARD_FAIL", nss_score=0.4),
        ),
        aggregate_result="HARD_FAIL",
        evaluation_kind="SANITY_VALIDATION",
        result_identity="R",
    )
    base.update(overrides)
    return CertificationEvidence(**base)


def _post_run(evidence: CertificationEvidence | None, **overrides: Any) -> PostRunReport:
    base: dict[str, Any] = dict(
        evidence=evidence,
        expected_corpus_identity="C",
        expected_manifest_identity="M",
        expected_configuration_identity="K",
        expected_parameter_identity="P",
        manifest_document_ids=frozenset({"doc-1", "doc-2"}),
        evaluation_provenance_available=True,
    )
    base.update(overrides)
    return validate_post_run(**base)


class TestCorpusContentIdentity:
    def test_order_insensitive(self) -> None:
        assert compute_corpus_content_identity((SHA_A, SHA_B)) == \
            compute_corpus_content_identity((SHA_B, SHA_A))

    def test_sensitive_to_content_change(self) -> None:
        assert compute_corpus_content_identity((SHA_A, SHA_B)) != \
            compute_corpus_content_identity((SHA_A, "c" * 64))

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            compute_corpus_content_identity(())

    def test_valid_sha256(self) -> None:
        h = compute_corpus_content_identity((SHA_A,))
        assert len(h) == 64


class TestEvidenceSerialization:
    def test_deterministic(self) -> None:
        assert serialize_evidence(_evidence()) == serialize_evidence(_evidence())

    def test_valid_json_with_seven_r29_elements(self) -> None:
        data = json.loads(serialize_evidence(_evidence()))
        for key in (
            "corpus_identity", "manifest_identity", "configuration_identity",
            "frozen_parameters_identity", "evaluation_provenance_reference",
            "per_document_results", "aggregate_result",
        ):
            assert key in data
        assert len(data["per_document_results"]) == 2

    def test_immutable(self) -> None:
        with pytest.raises(Exception):
            _evidence().aggregate_result = "OTRO"  # type: ignore[misc]


class TestPostRunValidation:
    def test_complete_evidence_passes(self) -> None:
        assert _post_run(_evidence()).is_pass

    def test_missing_provenance_named(self) -> None:
        report = _post_run(_evidence(), evaluation_provenance_available=False)
        assert not report.is_pass
        assert report.violations[0].element == ELEMENT_EVALUATION_PROVENANCE

    def test_absent_evidence_named(self) -> None:
        report = _post_run(None)
        assert not report.is_pass
        assert any(v.element == ELEMENT_PER_DOCUMENT_RESULTS for v in report.violations)

    def test_document_without_verdict_named(self) -> None:
        report = _post_run(
            _evidence(per_document_results=(
                DocumentResultEvidence(document_id="doc-1", verdict="PASS", nss_score=1.0),
            )),
        )
        assert not report.is_pass
        violation = next(v for v in report.violations if v.element == ELEMENT_PER_DOCUMENT_RESULTS)
        assert "doc-2" in violation.detail

    def test_orphan_verdict_named(self) -> None:
        report = _post_run(
            _evidence(per_document_results=(
                DocumentResultEvidence(document_id="doc-1", verdict="PASS", nss_score=1.0),
                DocumentResultEvidence(document_id="doc-2", verdict="PASS", nss_score=1.0),
                DocumentResultEvidence(document_id="doc-x", verdict="PASS", nss_score=1.0),
            )),
        )
        assert not report.is_pass
        violation = next(v for v in report.violations if v.element == ELEMENT_PER_DOCUMENT_RESULTS)
        assert "doc-x" in violation.detail

    def test_empty_aggregate_named(self) -> None:
        report = _post_run(_evidence(aggregate_result=""))
        assert report.violations[0].element == ELEMENT_AGGREGATE_RESULT

    @pytest.mark.parametrize("field,element", [
        ("manifest_identity", ELEMENT_MANIFEST_IDENTITY),
        ("configuration_identity", ELEMENT_CONFIGURATION_IDENTITY),
        ("frozen_parameters_identity", ELEMENT_FROZEN_PARAMETERS_IDENTITY),
    ])
    def test_identity_mismatch_named(self, field: str, element: str) -> None:
        report = _post_run(_evidence(**{field: "DISTINTA"}))
        assert not report.is_pass
        assert any(v.element == element for v in report.violations)

    def test_corpus_identity_mismatch_named(self) -> None:
        report = _post_run(_evidence(), expected_corpus_identity="DISTINTA")
        assert not report.is_pass
        assert any(v.element == ELEMENT_CORPUS_IDENTITY for v in report.violations)

    def test_deterministic_report(self) -> None:
        assert _post_run(_evidence(aggregate_result="")) == _post_run(_evidence(aggregate_result=""))
