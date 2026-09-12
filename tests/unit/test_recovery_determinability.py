"""Tests de recovery determinable post-fallo (NADR-24 R34, Task 4.4.3).

R34: tras fallo parcial, el estado resultante permite determinar:
(a) que unidades fueron evaluadas, (b) que artefactos quedaron en disco,
(c) si son reutilizables o descartables, (d) si re-ejecucion reemplaza.
"""
from __future__ import annotations

from core.benchmark.certification.evidence import (
    CertificationEvidence,
    DocumentResultEvidence,
)
from core.benchmark.certification.post_run import (
    ELEMENT_PER_DOCUMENT_RESULTS,
    validate_post_run,
)


def _partial_evidence() -> CertificationEvidence:
    return CertificationEvidence(
        corpus_identity="C",
        manifest_identity="M",
        configuration_identity="K",
        frozen_parameters_identity="P",
        evaluation_provenance_reference="provenance.json",
        per_document_results=(
            DocumentResultEvidence(document_id="doc-1", verdict="PASS", nss_score=1.0),
        ),
        aggregate_result="PARTIAL",
        evaluation_kind="SANITY_VALIDATION",
        result_identity="R",
    )


class TestRecoveryDeterminability:
    def test_missing_documents_are_named_in_violation(self):
        report = validate_post_run(
            evidence=_partial_evidence(),
            expected_corpus_identity="C",
            expected_manifest_identity="M",
            expected_configuration_identity="K",
            expected_parameter_identity="P",
            manifest_document_ids=frozenset({"doc-1", "doc-2", "doc-3"}),
            evaluation_provenance_available=True,
        )
        assert not report.is_pass
        violation = next(v for v in report.violations if v.element == ELEMENT_PER_DOCUMENT_RESULTS)
        assert "doc-2" in violation.detail
        assert "doc-3" in violation.detail

    def test_absent_evidence_is_named(self):
        report = validate_post_run(
            evidence=None,
            expected_corpus_identity="C",
            expected_manifest_identity="M",
            expected_configuration_identity="K",
            expected_parameter_identity="P",
            manifest_document_ids=frozenset(),
            evaluation_provenance_available=True,
        )
        assert not report.is_pass
        assert any(v.element == ELEMENT_PER_DOCUMENT_RESULTS for v in report.violations)
