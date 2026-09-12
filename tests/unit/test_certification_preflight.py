"""Tests de contrato de certificacion y PREFLIGHT puro (NADR-24 R4-R9)."""
from __future__ import annotations

from typing import Any

from core.benchmark.certification.contract import (
    CertificationStatus,
    ExecutionOutcome,
    ScientificResult,
    compose_certification_status,
)
from core.benchmark.certification.preflight import (
    PreflightCondition,
    evaluate_preflight,
)

_OK: dict[str, Any] = dict(
    manifest_load_error=None,
    computed_manifest_hash="H",
    expected_manifest_hash="H",
    completeness_violations=(),
    sealed_violations=(),
    oracle_hash_violations=(),
    current_configuration_identity="C",
    expected_configuration_identity="C",
    frozen_parameter_identity_in_artifact="P",
    expected_parameter_identity="P",
    calibration_provenance_available=True,
    calibration_partition_identities=frozenset(),
    corpus_sha256_identities=frozenset({"S1"}),
)


class TestComposeCertificationStatus:
    def test_certified_requires_all_components(self):
        assert compose_certification_status(
            ExecutionOutcome.SUCCESS, ScientificResult.ACCEPTED, True, True
        ) is CertificationStatus.CERTIFIED

    def test_execution_failure_dominates(self):
        assert compose_certification_status(
            ExecutionOutcome.EXECUTION_FAILURE, ScientificResult.ACCEPTED, True, True
        ) is CertificationStatus.EXECUTION_FAILURE

    def test_missing_evidence_is_execution_failure(self):
        assert compose_certification_status(
            ExecutionOutcome.SUCCESS, ScientificResult.ACCEPTED, False, True
        ) is CertificationStatus.EXECUTION_FAILURE

    def test_absent_scientific_result_is_execution_failure(self):
        assert compose_certification_status(
            ExecutionOutcome.SUCCESS, None, True, True
        ) is CertificationStatus.EXECUTION_FAILURE

    def test_rejected_scientific_is_rejected(self):
        assert compose_certification_status(
            ExecutionOutcome.SUCCESS, ScientificResult.REJECTED, True, True
        ) is CertificationStatus.REJECTED


class TestEvaluatePreflight:
    def test_all_conditions_satisfied(self):
        assert evaluate_preflight(**_OK).is_pass

    def test_idempotent_same_input_same_report(self):
        assert evaluate_preflight(**_OK) == evaluate_preflight(**_OK)

    def test_manifest_load_error_short_circuits(self):
        report = evaluate_preflight(**{**_OK, "manifest_load_error": "no existe"})
        assert not report.is_pass
        assert report.violations[0].condition is PreflightCondition.MANIFEST_FORMAT_VALID
        assert len(report.violations) == 1

    def test_manifest_hash_mismatch(self):
        report = evaluate_preflight(**{**_OK, "computed_manifest_hash": "OTRO"})
        assert report.violations[0].condition is PreflightCondition.CORPUS_IDENTITY_MATCHES

    def test_sealed_and_oracle_violations(self):
        report = evaluate_preflight(**{**_OK,
            "sealed_violations": ("doc_x no sealed",),
            "oracle_hash_violations": ("doc_x sin hash",)})
        conditions = {v.condition for v in report.violations}
        assert conditions == {
            PreflightCondition.GROUND_TRUTHS_SEALED,
            PreflightCondition.ORACLE_HASHES_VERIFIABLE,
        }

    def test_configuration_mismatch(self):
        report = evaluate_preflight(**{**_OK, "current_configuration_identity": "OTRA"})
        assert report.violations[0].condition is PreflightCondition.CONFIGURATION_CANONICAL

    def test_freeze_artifact_absent_and_mismatch(self):
        absent = evaluate_preflight(**{**_OK, "frozen_parameter_identity_in_artifact": None})
        assert absent.violations[0].condition is PreflightCondition.PARAMETERS_FROZEN
        mismatch = evaluate_preflight(**{**_OK, "frozen_parameter_identity_in_artifact": "OTRO"})
        assert mismatch.violations[0].condition is PreflightCondition.PARAMETERS_FROZEN

    def test_provenance_absent(self):
        report = evaluate_preflight(**{**_OK, "calibration_provenance_available": False})
        assert report.violations[0].condition is PreflightCondition.CALIBRATION_PROVENANCE_AVAILABLE

    def test_partition_leakage_detected(self):
        report = evaluate_preflight(**{**_OK, "calibration_partition_identities": frozenset({"S1"})})
        assert report.violations[0].condition is PreflightCondition.NO_PARTITION_LEAKAGE
