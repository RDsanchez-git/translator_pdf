"""Tests de identidades de provenance y parameter freeze (Wave 3.3).

NADR-23 SS5.5 R18-R22, SS5.6 R23-R25, SS5.8 R29-R31.
"""
from __future__ import annotations

import inspect
from typing import Any
import pytest

from core.benchmark.topology.regression.provenance import (
    CalibrationProvenanceRecord,
    EvaluationProvenanceRecord,
    ExperimentIdentityCalculator,
    FrozenParameters,
    ParameterIdentityCalculator,
    ResultIdentityCalculator,
)


def _params(**overrides: Any) -> FrozenParameters:
    base: dict[str, Any] = dict(
        nss_hard_fail=0.80,
        nss_warning=0.95,
        cost_weights=(5.0, 2.0, 1.0),
        warning_threshold=1,
    )
    base.update(overrides)
    return FrozenParameters(**base)


class TestParameterIdentity:
    def test_determinism(self):
        assert ParameterIdentityCalculator.calculate(_params()) == \
            ParameterIdentityCalculator.calculate(_params())

    def test_valid_sha256(self):
        h = ParameterIdentityCalculator.calculate(_params())
        assert len(h) == 64 and all(c in '0123456789abcdef' for c in h)

    @pytest.mark.parametrize('field,value', [
        ('nss_hard_fail', 0.75),
        ('nss_warning', 0.90),
        ('cost_weights', (5.0, 2.0, 1.5)),
        ('warning_threshold', 2),
    ])
    def test_sensitivity_per_field(self, field: str, value: Any) -> None:
        overrides: dict[str, Any] = {field: value}
        assert ParameterIdentityCalculator.calculate(_params()) != \
            ParameterIdentityCalculator.calculate(_params(**overrides))

    def test_invariant_thresholds(self):
        with pytest.raises(ValueError):
            _params(nss_hard_fail=0.95, nss_warning=0.95)

    def test_cost_weights_cardinality(self) -> None:
        bad_weights: Any = (5.0, 2.0)
        with pytest.raises(ValueError):
            FrozenParameters(0.8, 0.95, bad_weights, 1)


class TestExperimentIdentity:
    def test_timestamp_is_not_an_input(self):
        sig = inspect.signature(ExperimentIdentityCalculator.calculate)
        assert 'timestamp' not in sig.parameters

    def test_determinism(self):
        a = ExperimentIdentityCalculator.calculate(
            corpus_identity='c', protocol_identity='p', configuration_identity='m')
        b = ExperimentIdentityCalculator.calculate(
            corpus_identity='c', protocol_identity='p', configuration_identity='m')
        assert a == b

    @pytest.mark.parametrize('kwarg,value', [
        ('corpus_identity', 'otro'),
        ('protocol_identity', 'otra'),
        ('configuration_identity', 'otra'),
        ('search_configuration', 'grid'),
        ('seed', 7),
    ])
    def test_sensitivity(self, kwarg: str, value: Any) -> None:
        base: dict[str, Any] = dict(
            corpus_identity='c', protocol_identity='p', configuration_identity='m')
        variant: dict[str, Any] = {**base, kwarg: value}
        assert ExperimentIdentityCalculator.calculate(**base) != \
            ExperimentIdentityCalculator.calculate(**variant)


class TestResultIdentity:
    def test_determinism_and_sensitivity(self):
        assert ResultIdentityCalculator.calculate_from_bytes(b'x') == \
            ResultIdentityCalculator.calculate_from_bytes(b'x')
        assert ResultIdentityCalculator.calculate_from_bytes(b'x') != \
            ResultIdentityCalculator.calculate_from_bytes(b'y')


class TestIdentityDistinction:
    def test_parameter_identity_differs_from_configuration_identity(self):
        from bootstrap.topology import build_canonical_engine_configuration
        from core.benchmark.topology.criticality.costs import CriticalityAwareCostContext
        from core.benchmark.topology.regression.configuration import (
            ConfigurationFingerprintCalculator,
        )
        config = build_canonical_engine_configuration(cost_context=CriticalityAwareCostContext())
        config_id = ConfigurationFingerprintCalculator.calculate(config)
        param_id = ParameterIdentityCalculator.calculate(
            FrozenParameters(config.nss_hard_fail, config.nss_warning,
                             config.cost_weights, config.warning_threshold))
        assert param_id != config_id


class TestRecordsImmutable:
    def test_calibration_record_frozen(self):
        rec = CalibrationProvenanceRecord(
            corpus_identity='c', metric_configuration='m', parameters=_params(),
            result='r', timestamp='t', parameter_identity='pi',
            experiment_identity='ei', result_identity='ri',
            protocol_identity='p', calibration_run='NONE',
            parameters_origin='NORMATIVE_DESIGN')
        with pytest.raises(AttributeError):
            setattr(rec, 'result', 'otro')

    def test_evaluation_record_frozen(self):
        rec = EvaluationProvenanceRecord(
            corpus_identity='c', configuration_identity='m',
            frozen_parameters_identity='pi', result='r', timestamp='t',
            result_identity='ri', evaluation_kind='SANITY_VALIDATION',
            calibration_provenance_reference='ei')
        with pytest.raises(AttributeError):
            setattr(rec, 'result', 'otro')
