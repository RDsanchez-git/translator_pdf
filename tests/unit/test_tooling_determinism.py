"""Tests de determinismo operacional de tooling (NADR-24 R32, Task 4.4.1).

R32: dadas las mismas condiciones certificables (corpus, configuracion,
parametros congelados, execution version), el tooling produce el mismo
resultado operacional. Distinto de reproducibilidad cientifica (NADR-23).
"""
from __future__ import annotations

import json

from core.benchmark.certification.evidence import (
    CertificationEvidence,
    DocumentResultEvidence,
    compute_corpus_content_identity,
    serialize_evidence,
)


def _evidence(corpus_id: str = "C") -> CertificationEvidence:
    return CertificationEvidence(
        corpus_identity=corpus_id,
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


class TestToolingDeterminism:
    def test_evidence_serialization_is_byte_identical_across_runs(self):
        ev1 = _evidence()
        ev2 = _evidence()
        assert serialize_evidence(ev1) == serialize_evidence(ev2)

    def test_corpus_content_identity_is_order_independent(self):
        sha_a = "a" * 64
        sha_b = "b" * 64
        assert compute_corpus_content_identity((sha_a, sha_b)) == \
            compute_corpus_content_identity((sha_b, sha_a))

    def test_json_dumps_sort_keys_is_deterministic(self):
        data = {"z": 1, "a": 2, "m": 3}
        s1 = json.dumps(data, sort_keys=True)
        s2 = json.dumps(data, sort_keys=True)
        assert s1 == s2 == '{"a": 2, "m": 3, "z": 1}'
