"""
tests/unit/test_score_policy.py

Suite de pruebas unitarias para ScorePolicy (Hito 1 - ADR F17.5).
"""

from dataclasses import FrozenInstanceError
import pytest

from core.benchmark.score_policy import (
    InvalidMetricValueError,
    InvalidPolicyConfigurationError,
    MetricDirection,
    MetricName,
    MetricRule,
    MissingMetricError,
    ScorePolicy,
    UnknownMetricRuleError,
)


def test_apply_direction_higher_and_lower_is_better() -> None:
    policy = ScorePolicy(
        rules={
            MetricName("recall"): MetricRule(weight=0.5, direction=MetricDirection.HIGHER_IS_BETTER),
            MetricName("ted"): MetricRule(weight=0.5, direction=MetricDirection.LOWER_IS_BETTER),
        }
    )
    assert policy.apply_direction(MetricName("recall"), 0.8) == 0.8
    assert policy.apply_direction(MetricName("ted"), 0.2) == 0.8


def test_out_of_bounds_and_non_finite_values_raise_invalid_metric_value_error() -> None:
    policy = ScorePolicy(
        rules={
            MetricName("ted"): MetricRule(weight=1.0, direction=MetricDirection.LOWER_IS_BETTER)
        }
    )
    with pytest.raises(InvalidMetricValueError):
        policy.apply_direction(MetricName("ted"), 1.2)

    with pytest.raises(InvalidMetricValueError):
        policy.apply_direction(MetricName("ted"), -0.1)

    with pytest.raises(InvalidMetricValueError):
        policy.apply_direction(MetricName("ted"), float("nan"))


def test_unregistered_metric_raises_unknown_metric_rule_error() -> None:
    policy = ScorePolicy(
        rules={
            MetricName("ted"): MetricRule(weight=1.0, direction=MetricDirection.LOWER_IS_BETTER)
        }
    )
    metrics = {
        MetricName("ted"): 0.2,
        MetricName("unregistered_metric"): 0.5,
    }
    with pytest.raises(UnknownMetricRuleError) as exc_info:
        policy.compute_composite_score(metrics)
    assert "unregistered_metric" in str(exc_info.value)


def test_policy_rejects_missing_required_metric() -> None:
    policy = ScorePolicy(
        rules={
            MetricName("ted"): MetricRule(weight=0.6, direction=MetricDirection.LOWER_IS_BETTER),
            MetricName("recall"): MetricRule(weight=0.4, direction=MetricDirection.HIGHER_IS_BETTER),
        }
    )
    metrics = {MetricName("ted"): 0.2}
    with pytest.raises(MissingMetricError) as exc_info:
        policy.compute_composite_score(metrics)
    assert "recall" in str(exc_info.value)


def test_empty_rules_policy_raises_configuration_error() -> None:
    with pytest.raises(InvalidPolicyConfigurationError):
        ScorePolicy(rules={})


def test_invalid_individual_weight_raises_configuration_error() -> None:
    with pytest.raises(InvalidPolicyConfigurationError):
        MetricRule(weight=-0.1, direction=MetricDirection.HIGHER_IS_BETTER)

    with pytest.raises(InvalidPolicyConfigurationError):
        MetricRule(weight=float("nan"), direction=MetricDirection.HIGHER_IS_BETTER)


def test_invalid_weight_sum_raises_configuration_error() -> None:
    rules = {
        MetricName("m1"): MetricRule(weight=0.5, direction=MetricDirection.HIGHER_IS_BETTER),
        MetricName("m2"): MetricRule(weight=0.8, direction=MetricDirection.LOWER_IS_BETTER),
    }
    with pytest.raises(InvalidPolicyConfigurationError):
        ScorePolicy(rules=rules)


def test_policy_and_rules_mapping_are_strictly_immutable() -> None:
    raw_rules = {
        MetricName("m1"): MetricRule(weight=1.0, direction=MetricDirection.HIGHER_IS_BETTER)
    }
    policy = ScorePolicy(rules=raw_rules)

    with pytest.raises(FrozenInstanceError):
        policy.rules = {}  # type: ignore

    with pytest.raises(TypeError):
        policy.rules[MetricName("m1")] = MetricRule(weight=0.5, direction=MetricDirection.LOWER_IS_BETTER)  # type: ignore


def test_compute_composite_score_exact_precision() -> None:
    policy = ScorePolicy(
        rules={
            MetricName("ted"): MetricRule(weight=0.6, direction=MetricDirection.LOWER_IS_BETTER),
            MetricName("recall"): MetricRule(weight=0.4, direction=MetricDirection.HIGHER_IS_BETTER),
        }
    )
    # ted = 0.1234 -> transformed = 0.8766 -> weighted = 0.52596
    # recall = 0.5678 -> transformed = 0.5678 -> weighted = 0.22712
    # total exact = 0.75308
    metrics = {
        MetricName("ted"): 0.1234,
        MetricName("recall"): 0.5678,
    }
    composite = policy.compute_composite_score(metrics)
    assert composite == pytest.approx(0.75308, abs=1e-9)