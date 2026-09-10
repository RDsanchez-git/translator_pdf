"""Tests de ConfigurationFingerprintCalculator y CanonicalEngineConfiguration.

NADR-22 §5.6 R19: Identificador criptografico de configuracion.
NADR-22 §5.6 R20: Congelamiento de la configuracion.
NADR-22 §5.6 R21: Toda modificacion invalida certificacion vigente.
"""
from __future__ import annotations

import pytest

from core.benchmark.topology.regression.configuration import (
    CanonicalEngineConfiguration,
    ConfigurationFingerprintCalculator,
)


def _make_config(
    cost_weights=(5.0, 2.0, 1.0),
    nss_hard_fail=0.80,
    nss_warning=0.95,
    warning_threshold=1,
):
    """Helper para construir una configuracion de prueba.

    El engine_type usa el qualified name real del motor canonico
    (module.qualname), no un string libre, para garantizar
    consistencia con from_components.
    """
    return CanonicalEngineConfiguration(
        engine_type="core.benchmark.topology.engines.zhang_shasha.engine.ZhangShashaEngine",
        cost_weights=cost_weights,
        partition_strategy="core.benchmark.topology.partitioning.heading.HeadingAnchorPartitionStrategy",
        alignment_strategy="core.benchmark.topology.alignment.strategy.LCSAnchorAlignmentStrategy",
        normalization_policy="core.benchmark.topology.policies.normalization.MaxBoundNormalizationPolicy",
        overflow_strategy="core.benchmark.topology.policies.overflow.WorstCaseOverflowStrategy",
        matching_policy="bootstrap.topology.DefaultNodeMatchingPolicy",
        nss_hard_fail=nss_hard_fail,
        nss_warning=nss_warning,
        warning_threshold=warning_threshold,
    )


class TestConfigurationFingerprintDeterminism:
    def test_same_config_same_hash(self):
        config = _make_config()
        hash1 = ConfigurationFingerprintCalculator.calculate(config)
        hash2 = ConfigurationFingerprintCalculator.calculate(config)
        assert hash1 == hash2

    def test_hash_is_valid_sha256(self):
        config = _make_config()
        h = ConfigurationFingerprintCalculator.calculate(config)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestConfigurationFingerprintSensitivity:
    def test_engine_type_change_produces_different_hash(self):
        config1 = _make_config()
        config2 = CanonicalEngineConfiguration(
            engine_type="other_module.APTEDEngine",
            cost_weights=config1.cost_weights,
            partition_strategy=config1.partition_strategy,
            alignment_strategy=config1.alignment_strategy,
            normalization_policy=config1.normalization_policy,
            overflow_strategy=config1.overflow_strategy,
            matching_policy=config1.matching_policy,
            nss_hard_fail=config1.nss_hard_fail,
            nss_warning=config1.nss_warning,
            warning_threshold=config1.warning_threshold,
        )
        assert ConfigurationFingerprintCalculator.calculate(config1) != ConfigurationFingerprintCalculator.calculate(config2)

    def test_cost_weights_change_produces_different_hash(self):
        config1 = _make_config(cost_weights=(5.0, 2.0, 1.0))
        config2 = _make_config(cost_weights=(5.0, 2.0, 1.1))
        assert ConfigurationFingerprintCalculator.calculate(config1) != ConfigurationFingerprintCalculator.calculate(config2)

    def test_nss_hard_fail_change_produces_different_hash(self):
        config1 = _make_config(nss_hard_fail=0.80)
        config2 = _make_config(nss_hard_fail=0.75)
        assert ConfigurationFingerprintCalculator.calculate(config1) != ConfigurationFingerprintCalculator.calculate(config2)

    def test_nss_warning_change_produces_different_hash(self):
        config1 = _make_config(nss_warning=0.95)
        config2 = _make_config(nss_warning=0.90)
        assert ConfigurationFingerprintCalculator.calculate(config1) != ConfigurationFingerprintCalculator.calculate(config2)

    def test_warning_threshold_change_produces_different_hash(self):
        config1 = _make_config(warning_threshold=1)
        config2 = _make_config(warning_threshold=2)
        assert ConfigurationFingerprintCalculator.calculate(config1) != ConfigurationFingerprintCalculator.calculate(config2)

    def test_partition_strategy_change_produces_different_hash(self):
        config1 = _make_config()
        config2 = CanonicalEngineConfiguration(
            engine_type=config1.engine_type,
            cost_weights=config1.cost_weights,
            partition_strategy="other_module.DifferentPartitionStrategy",
            alignment_strategy=config1.alignment_strategy,
            normalization_policy=config1.normalization_policy,
            overflow_strategy=config1.overflow_strategy,
            matching_policy=config1.matching_policy,
            nss_hard_fail=config1.nss_hard_fail,
            nss_warning=config1.nss_warning,
            warning_threshold=config1.warning_threshold,
        )
        assert ConfigurationFingerprintCalculator.calculate(config1) != ConfigurationFingerprintCalculator.calculate(config2)


class TestCanonicalEngineConfigurationImmutability:
    def test_config_is_frozen(self):
        config = _make_config()
        with pytest.raises(AttributeError):
            # Usar setattr() para evitar falso positivo de Pyright
            # (Pyright detecta que engine_type es readonly y reporta error,
            # pero no entiende el contexto de pytest.raises)
            setattr(config, "engine_type", "other_module.APTEDEngine")

    def test_config_is_hashable(self):
        config = _make_config()
        assert hash(config) is not None


class TestFromComponents:
    def test_from_components_extracts_module_qualname_for_all_components(self):
        class FakePartitioner:
            pass

        class FakeAligner:
            pass

        class FakeNormalizer:
            pass

        class FakeOverflow:
            pass

        class FakeMatchingPolicy:
            pass

        class FakeEngine:
            pass

        config = CanonicalEngineConfiguration.from_components(
            engine=FakeEngine(),
            cost_weights=(5.0, 2.0, 1.0),
            partitioner=FakePartitioner(),
            aligner=FakeAligner(),
            normalizer=FakeNormalizer(),
            overflow=FakeOverflow(),
            matching_policy=FakeMatchingPolicy(),
            nss_hard_fail=0.80,
            nss_warning=0.95,
            warning_threshold=1,
        )
        assert "FakeEngine" in config.engine_type
        assert "FakePartitioner" in config.partition_strategy
        assert "FakeAligner" in config.alignment_strategy
        assert "FakeNormalizer" in config.normalization_policy
        assert "FakeOverflow" in config.overflow_strategy
        assert "FakeMatchingPolicy" in config.matching_policy

    def test_from_components_includes_module_path(self):
        """El qualified name debe incluir el modulo para unicidad absoluta."""
        class MyPolicy:
            pass

        class MyEngine:
            pass

        config = CanonicalEngineConfiguration.from_components(
            engine=MyEngine(),
            cost_weights=(5.0, 2.0, 1.0),
            partitioner=MyPolicy(),
            aligner=MyPolicy(),
            normalizer=MyPolicy(),
            overflow=MyPolicy(),
            matching_policy=MyPolicy(),
            nss_hard_fail=0.80,
            nss_warning=0.95,
            warning_threshold=1,
        )
        assert "test_configuration_fingerprint" in config.partition_strategy
        assert "test_configuration_fingerprint" in config.engine_type
