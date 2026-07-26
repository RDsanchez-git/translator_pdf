"""
core/benchmark/score_policy.py

Política declarativa, inmutable y Fail-Fast de puntuación para benchmarking.
Desacopla la ponderación y dirección de optimización respecto a los evaluadores de dominio.
"""

from dataclasses import dataclass
from enum import Enum
import math
from types import MappingProxyType
from typing import Mapping, NewType

MetricName = NewType("MetricName", str)


class MetricDirection(str, Enum):
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"


class ScorePolicyError(ValueError):
    """Excepción base para fallas de la política de puntuación."""
    pass


class UnknownMetricRuleError(ScorePolicyError):
    """Falla Fail-Fast al intentar evaluar una métrica no registrada en la política."""
    pass


class MissingMetricError(ScorePolicyError):
    """Falla Fail-Fast cuando falta una métrica requerida por la política."""
    pass


class InvalidMetricValueError(ScorePolicyError):
    """Falla Fail-Fast cuando el valor de una métrica está fuera del rango [0.0, 1.0]."""
    pass


class InvalidPolicyConfigurationError(ScorePolicyError):
    """Falla Fail-Fast cuando la configuración de reglas de la política es inválida."""
    pass


@dataclass(frozen=True, slots=True)
class MetricRule:
    weight: float
    direction: MetricDirection

    def __post_init__(self) -> None:
        if not math.isfinite(self.weight) or not (0.0 <= self.weight <= 1.0):
            raise InvalidPolicyConfigurationError(
                f"El peso de una regla debe ser un número finito en el rango [0.0, 1.0]. Obtenido: {self.weight}"
            )


@dataclass(frozen=True, slots=True)
class ScorePolicy:
    """Política inmutable y agnóstica a métricas concretas del dominio."""
    rules: Mapping[MetricName, MetricRule]

    def __post_init__(self) -> None:
        if not self.rules:
            raise InvalidPolicyConfigurationError(
                "La política de puntuación no puede construirse con un conjunto de reglas vacío."
            )

        total_weight = sum(rule.weight for rule in self.rules.values())
        if not math.isclose(total_weight, 1.0, rel_tol=1e-5):
            raise InvalidPolicyConfigurationError(
                f"La suma de los pesos de la política debe ser exactamente 1.0. Obtenido: {total_weight}"
            )

        # Copia defensiva e inmutabilización estricta del Mapping
        immutable_rules = MappingProxyType(dict(self.rules))
        object.__setattr__(self, "rules", immutable_rules)

    def apply_direction(self, metric_name: MetricName, normalized_value: float) -> float:
        """Aplica la dirección de optimización a un valor validado estrictamente en [0.0, 1.0]."""
        if metric_name not in self.rules:
            raise UnknownMetricRuleError(
                f"Falla de Configuración Fail-Fast: La métrica '{metric_name}' "
                f"no está definida en la política de puntuación."
            )

        if not math.isfinite(normalized_value) or not (0.0 <= normalized_value <= 1.0):
            raise InvalidMetricValueError(
                f"Falla de Invariante Fail-Fast: El valor normalizado de '{metric_name}' "
                f"debe ser un número finito en [0.0, 1.0]. Obtenido: {normalized_value}"
            )

        rule = self.rules[metric_name]
        return normalized_value if rule.direction == MetricDirection.HIGHER_IS_BETTER else (1.0 - normalized_value)

    def calculate_weighted_score(self, metric_name: MetricName, normalized_value: float) -> float:
        """Calcula el score ponderado para una métrica individual."""
        transformed = self.apply_direction(metric_name, normalized_value)
        return transformed * self.rules[metric_name].weight

    def compute_composite_score(self, metrics: Mapping[MetricName, float]) -> float:
        """Calcula la suma ponderada exacta en precisión flotante IEEE 754."""
        expected_keys = set(self.rules.keys())
        provided_keys = set(metrics.keys())

        missing_keys = expected_keys - provided_keys
        if missing_keys:
            sorted_missing = sorted(list(missing_keys))
            raise MissingMetricError(
                f"Falla de Evaluación Fail-Fast: Faltan las siguientes métricas requeridas "
                f"por la política: {sorted_missing}"
            )

        unexpected_keys = provided_keys - expected_keys
        if unexpected_keys:
            sorted_unexpected = sorted(list(unexpected_keys))
            raise UnknownMetricRuleError(
                f"Falla de Configuración Fail-Fast: Se recibieron métricas no registradas "
                f"en la política: {sorted_unexpected}"
            )

        total_score = 0.0
        for name, value in metrics.items():
            total_score += self.calculate_weighted_score(name, value)
            
        return total_score