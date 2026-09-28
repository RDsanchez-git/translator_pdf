"""Tests de IdentityChain (NADR-F17BIS-28 §5.1, §5.2).

Tests unitarios para las funciones de construcción de identity chain.
Verifican determinismo, composición y limitaciones observables.
"""
from __future__ import annotations

import pytest

from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.verification.identity_chain import (
    SCHEMA_VERSION,
    build_execution_id,
    build_identity_chain,
    build_parameter_identity,
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
        # Ejecutar múltiples veces
        results = [build_parameter_identity(weights) for _ in range(10)]
        assert len(set(results)) == 1


@pytest.mark.unit
class TestBuildExecutionId:
    """NADR-F17BIS-28 §5.1 R1, §5.2 R8: execution_id determinista."""

    def test_deterministic_for_same_inputs(self) -> None:
        """R8: Mismos inputs → mismo execution_id."""
        first = build_execution_id(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
        )
        second = build_execution_id(
            baseline_identity="a" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
        )
        assert first == second

    def test_none_subject_identity_is_handled(self) -> None:
        """R29: subject_identity=None es válido y produce hash determinista."""
        exec_id = build_execution_id(
            baseline_identity="a" * 64,
            subject_identity=None,
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
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
        )
        id_b = build_execution_id(
            baseline_identity="x" * 64,
            subject_identity="commit123",
            configuration_identity="b" * 64,
            parameter_identity="c" * 64,
        )
        assert id_a != id_b


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
    """NADR-F17BIS-28 §5.1 R6, §5.5 R29: identity chain completa."""

    def test_complete_chain_has_all_components(self) -> None:
        """R6: Cadena completa Execution → Subject → Baseline → Config → Params → Result."""
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
            result_identity="c" * 64,
        )
        assert chain.schema_version == SCHEMA_VERSION
        assert chain.baseline_identity == "a" * 64
        assert chain.subject_identity == "commit123"
        assert chain.configuration_identity == "b" * 64
        assert chain.parameter_identity  # Calculado
        assert chain.execution_id  # Calculado
        assert chain.result_identity == "c" * 64
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
            result_identity="c" * 64,
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
            result_identity="c" * 64,
        )
        mapping = chain.to_mapping()
        assert mapping["schema_version"] == SCHEMA_VERSION
        assert mapping["baseline_identity"] == "a" * 64
        assert mapping["subject_identity"] == "commit123"
        assert isinstance(mapping["limitations"], list)