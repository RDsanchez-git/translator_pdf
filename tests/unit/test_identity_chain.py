"""Tests de IdentityChain (NADR-F17BIS-28 §5.1, §5.2, NADR-F17BIS-29 §5.6).

Tests unitarios para las funciones de construcción de identity chain.
Verifican determinismo, composición, limitaciones observables,
y distinguibilidad por perfil de ejecución.
"""
from __future__ import annotations

import pytest

from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.verification.identity_chain import (
    SCHEMA_VERSION,
    build_execution_id,
    build_identity_chain,
    build_parameter_identity,
    build_profile_identity,
    build_result_identity,
)


@pytest.mark.unit
class TestBuildParameterIdentity:
    """NADR-F17BIS-28 §5.1 R5, §5.2 R8: parameter_identity determinista."""

    def test_deterministic_for_same_inputs(self) -> None:
        """R8: Mismos inputs → mismo hash."""
        weights = {
            NodeCriticality.CRITICAL: 5.0,
            NodeCriticality.WARNING: 2.0,
            NodeCriticality.INFO: 1.0,
        }
        first = build_parameter_identity(weights)
        second = build_parameter_identity(weights)
        assert first == second

    def test_different_weights_produce_different_identity(self) -> None:
        """R8: Diferentes pesos → diferente identidad."""
        weights_a = {
            NodeCriticality.CRITICAL: 5.0,
            NodeCriticality.WARNING: 2.0,
            NodeCriticality.INFO: 1.0,
        }
        weights_b = {
            NodeCriticality.CRITICAL: 10.0,
            NodeCriticality.WARNING: 2.0,
            NodeCriticality.INFO: 1.0,
        }
        assert build_parameter_identity(weights_a) != build_parameter_identity(weights_b)

    def test_order_is_deterministic(self) -> None:
        """R8: Orden fijo CRITICAL, WARNING, INFO."""
        weights = {
            NodeCriticality.CRITICAL: 5.0,
            NodeCriticality.WARNING: 2.0,
            NodeCriticality.INFO: 1.0,
        }
        results = [build_parameter_identity(weights) for _ in range(10)]
        assert len(set(results)) == 1


@pytest.mark.unit
class TestBuildExecutionId:
    """NADR-F17BIS-28 §5.1 R1, §5.2 R8, NADR-F17BIS-29 §5.6 R31."""

    def test_deterministic_for_same_inputs(self) -> None:
        """R8: Mismos inputs → mismo execution_id."""
        first = build_execution_id(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
            profile_identity="d" * 64,
        )
        second = build_execution_id(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
            profile_identity="d" * 64,
        )
        assert first == second

    def test_none_subject_identity_is_handled(self) -> None:
        """R29: subject_identity=None es válido y produce hash determinista."""
        exec_id = build_execution_id(
            baseline_identity="a" * 64,
            subject_identity=None,
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
            profile_identity="d" * 64,
        )
        assert isinstance(exec_id, str)
        assert len(exec_id) == 64

    def test_different_baseline_produces_different_execution_id(self) -> None:
        """R11: Identidad de ejecución ≠ identidad de baseline."""
        id_a = build_execution_id(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
            profile_identity="d" * 64,
        )
        id_b = build_execution_id(
            baseline_identity="x" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
            profile_identity="d" * 64,
        )
        assert id_a != id_b

    def test_different_profile_produces_different_execution_id(self) -> None:
        """NADR-29 §5.6 R31: Perfiles diferentes → execution_id diferente."""
        id_full = build_execution_id(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
            profile_identity="full_hash" + "0" * 55,
        )
        id_smoke = build_execution_id(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
            profile_identity="smoke_hash" + "0" * 55,
        )
        assert id_full != id_smoke


@pytest.mark.unit
class TestBuildResultIdentity:
    """NADR-F17BIS-28 §5.2 R13: result_identity no sustituye entradas."""

    def test_deterministic_for_same_inputs(self) -> None:
        """R8: Mismos inputs → mismo result_identity."""
        first = build_result_identity(
            outcome_value="PASS",
            scientific_verdict_value="PASS",
            regression_report_json='{"corpus_verdict": "PASS"}',
        )
        second = build_result_identity(
            outcome_value="PASS",
            scientific_verdict_value="PASS",
            regression_report_json='{"corpus_verdict": "PASS"}',
        )
        assert first == second

    def test_none_scientific_verdict_is_handled(self) -> None:
        """R9: scientific_verdict=None es válido (EXECUTION_FAILURE)."""
        result_id = build_result_identity(
            outcome_value="EXECUTION_FAILURE",
            scientific_verdict_value=None,
            regression_report_json=None,
        )
        assert isinstance(result_id, str)
        assert len(result_id) == 64

    def test_none_regression_report_is_handled(self) -> None:
        """NADR-27 §5.2 R8: BASELINE_INTEGRITY_FAILURE sin regression_report."""
        result_id = build_result_identity(
            outcome_value="BASELINE_INTEGRITY_FAILURE",
            scientific_verdict_value=None,
            regression_report_json=None,
        )
        assert isinstance(result_id, str)
        assert len(result_id) == 64


@pytest.mark.unit
class TestBuildIdentityChain:
    """NADR-F17BIS-28 §5.1 R6, §5.5 R29, NADR-F17BIS-29 §5.6 R28-R31."""

    def test_complete_chain_has_all_components(self) -> None:
        """R6: Cadena completa Execution → Subject → Baseline → Config → Params → Profile → Result."""
        weights = {
            NodeCriticality.CRITICAL: 5.0,
            NodeCriticality.WARNING: 2.0,
            NodeCriticality.INFO: 1.0,
        }
        chain = build_identity_chain(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            cost_weights=weights,
            profile_identity="d" * 64,
            result_identity="e" * 64,
        )
        assert chain.schema_version == SCHEMA_VERSION
        assert chain.baseline_identity == "a" * 64
        assert chain.subject_identity == "commit123"
        assert chain.configuration_identity == "b" * 64
        assert chain.parameter_identity  # Calculado
        assert chain.profile_identity == "d" * 64
        assert chain.execution_id  # Calculado
        assert chain.result_identity == "e" * 64
        assert chain.limitations == ()

    def test_missing_subject_identity_adds_limitation(self) -> None:
        """R29: Limitación observable cuando subject_identity es None."""
        weights = {
            NodeCriticality.CRITICAL: 5.0,
            NodeCriticality.WARNING: 2.0,
            NodeCriticality.INFO: 1.0,
        }
        chain = build_identity_chain(
            baseline_identity="a" * 64,
            subject_identity=None,
            configuration_identity="b" * 64,
            cost_weights=weights,
            profile_identity="d" * 64,
            result_identity="e" * 64,
        )
        assert chain.subject_identity is None
        assert any("subject_identity unavailable" in lim for lim in chain.limitations)

    def test_missing_result_identity_adds_limitation(self) -> None:
        """R29: Limitación observable cuando result_identity es None."""
        weights = {
            NodeCriticality.CRITICAL: 5.0,
            NodeCriticality.WARNING: 2.0,
            NodeCriticality.INFO: 1.0,
        }
        chain = build_identity_chain(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            cost_weights=weights,
            profile_identity="d" * 64,
            result_identity=None,
        )
        assert chain.result_identity is None
        assert any("result_identity unavailable" in lim for lim in chain.limitations)

    def test_to_mapping_serializes_correctly(self) -> None:
        """Serialización a dict para JSON."""
        weights = {
            NodeCriticality.CRITICAL: 5.0,
            NodeCriticality.WARNING: 2.0,
            NodeCriticality.INFO: 1.0,
        }
        chain = build_identity_chain(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            cost_weights=weights,
            profile_identity="d" * 64,
            result_identity="e" * 64,
        )
        mapping = chain.to_mapping()
        assert mapping["schema_version"] == SCHEMA_VERSION
        assert mapping["baseline_identity"] == "a" * 64
        assert mapping["subject_identity"] == "commit123"
        assert mapping["profile_identity"] == "d" * 64
        assert isinstance(mapping["limitations"], list)

    def test_different_profiles_produce_different_execution_ids(self) -> None:
        """NADR-29 §5.6 R31: Perfiles diferentes → execution_ids diferentes."""
        weights = {
            NodeCriticality.CRITICAL: 5.0,
            NodeCriticality.WARNING: 2.0,
            NodeCriticality.INFO: 1.0,
        }
        chain_full = build_identity_chain(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            cost_weights=weights,
            profile_identity="full_hash" + "0" * 55,
            result_identity="e" * 64,
        )
        chain_smoke = build_identity_chain(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            cost_weights=weights,
            profile_identity="smoke_hash" + "0" * 55,
            result_identity="e" * 64,
        )
        assert chain_full.execution_id != chain_smoke.execution_id


@pytest.mark.unit
class TestBuildProfileIdentity:
    """NADR-F17BIS-29 §5.6 R28-R31."""

    def test_deterministic_for_same_inputs(self) -> None:
        """R28: Mismos inputs → mismo profile_identity."""
        first = build_profile_identity(
            profile_name="FULL",
            document_ids=frozenset({"doc_01", "doc_02", "doc_03"}),
        )
        second = build_profile_identity(
            profile_name="FULL",
            document_ids=frozenset({"doc_01", "doc_02", "doc_03"}),
        )
        assert first == second

    def test_different_profile_name_produces_different_identity(self) -> None:
        """R31: Perfiles diferentes → identidad diferente."""
        full_id = build_profile_identity(
            profile_name="FULL",
            document_ids=frozenset({"doc_01", "doc_02", "doc_03"}),
        )
        smoke_id = build_profile_identity(
            profile_name="SMOKE",
            document_ids=frozenset({"doc_01", "doc_02", "doc_03"}),
        )
        assert full_id != smoke_id

    def test_different_document_ids_produces_different_identity(self) -> None:
        """R30: Coberturas diferentes → identidad diferente."""
        id_a = build_profile_identity(
            profile_name="SMOKE",
            document_ids=frozenset({"doc_01", "doc_02"}),
        )
        id_b = build_profile_identity(
            profile_name="SMOKE",
            document_ids=frozenset({"doc_01", "doc_03"}),
        )
        assert id_a != id_b

    def test_document_order_does_not_affect_identity(self) -> None:
        """frozenset no depende del orden (determinismo garantizado)."""
        id_a = build_profile_identity(
            profile_name="SMOKE",
            document_ids=frozenset({"doc_01", "doc_02", "doc_03"}),
        )
        id_b = build_profile_identity(
            profile_name="SMOKE",
            document_ids=frozenset({"doc_03", "doc_01", "doc_02"}),
        )
        assert id_a == id_b

    def test_empty_document_ids_produces_valid_hash(self) -> None:
        """Edge case: manifest vacío produce hash válido."""
        result = build_profile_identity(
            profile_name="SMOKE",
            document_ids=frozenset(),
        )
        assert isinstance(result, str)
        assert len(result) == 64