"""Provenance experimental: identidades y registros (NADR-23 SS5.5, SS5.6, SS5.8).

NADR-23 SS5.5 R20: tres tipos de identidad distinguibles:
  (a) experiment identity  -> como se ejecuto el experimento (sin timestamp)
  (b) parameter identity   -> conjunto concreto de parametros congelados
  (c) result identity      -> resultado producido por la ejecucion

NADR-23 SS5.5 R21: artifact provenance (linaje de artefactos, Wave 1.2) es
distinto de calibration-run provenance (identidad de experimentos). Este
modulo implementa el segundo; no duplica el primero.

NADR-23 SS5.6 R24: el parameter freeze es verificable mediante hash
criptografico determinista.

Diseno: Functional Core puro. Sin I/O, sin estado, sin timestamp en las
identidades (R20). El I/O y los timestamps viven en el Imperative Shell
(tools/evaluation/freeze_parameters.py).
"""
from __future__ import annotations

from dataclasses import dataclass

from core.shared.crypto import compute_sha256


@dataclass(frozen=True)
class FrozenParameters:
    """Conjunto de parametros congelables (NADR-23 SS5.6 R23-R25).

    Invariante de thresholds espejada de RegressionThresholds:
    0.0 <= nss_hard_fail < nss_warning <= 1.0
    """

    nss_hard_fail: float
    nss_warning: float
    cost_weights: tuple[float, float, float]
    warning_threshold: int

    def __post_init__(self) -> None:
        if not (0.0 <= self.nss_hard_fail < self.nss_warning <= 1.0):
            raise ValueError(
                f"Invariant failure: thresholds must satisfy "
                f"0.0 <= nss_hard_fail < nss_warning <= 1.0. "
                f"Got nss_hard_fail={self.nss_hard_fail}, "
                f"nss_warning={self.nss_warning}."
            )
        if len(self.cost_weights) != 3:
            raise ValueError(
                f"cost_weights must have exactly 3 entries "
                f"(CRITICAL, WARNING, INFO). Got {len(self.cost_weights)}."
            )
        if any(w <= 0.0 for w in self.cost_weights):
            raise ValueError(
                f"cost_weights must be strictly positive. Got {self.cost_weights}."
            )

    def canonical_bytes(self) -> bytes:
        """Serializacion determinista para hashing (repr explicito de floats).

        Nota de contrato: el formato de serializacion es parte del contrato
        de freeze; modificarlo constituye una nueva parameter identity
        (NADR-23 SS5.6 R25) aunque los valores no cambien.
        """
        canonical = (
            f"nss_hard_fail={self.nss_hard_fail!r}|"
            f"nss_warning={self.nss_warning!r}|"
            f"cost_weights={self.cost_weights[0]!r},{self.cost_weights[1]!r},{self.cost_weights[2]!r}|"
            f"warning_threshold={self.warning_threshold!r}"
        )
        return canonical.encode("utf-8")


class ParameterIdentityCalculator:
    """Parameter identity: hash determinista del conjunto de parametros.

    NADR-23 SS5.6 R24: identificable mediante hash criptografico.
    Payload canonico en orden fijo, separado por pipes. Solo parametros:
    un cambio de motor sin cambio de parametros NO altera esta identidad
    (distincion obligatoria frente a configuration_identity).
    """

    @staticmethod
    def calculate(parameters: FrozenParameters) -> str:
        return compute_sha256(parameters.canonical_bytes())


class ExperimentIdentityCalculator:
    """Experiment identity (NADR-23 SS5.5 R20).

    Deriva de: corpus_identity, protocol_identity, configuration_identity,
    search_configuration y seed cuando aplique. El timestamp MUST NOT
    participar (R20): dos emisiones del mismo experimento con timestamps
    distintos comparten experiment identity.
    """

    @staticmethod
    def calculate(
        *,
        corpus_identity: str,
        protocol_identity: str,
        configuration_identity: str,
        search_configuration: str | None = None,
        seed: int | None = None,
    ) -> str:
        payload = (
            f"{corpus_identity}|"
            f"{protocol_identity}|"
            f"{configuration_identity}|"
            f"{search_configuration if search_configuration is not None else 'NONE'}|"
            f"{seed if seed is not None else 'NONE'}"
        )
        return compute_sha256(payload.encode("utf-8"))


class ResultIdentityCalculator:
    """Result identity: hash del artefacto de resultado (R20(c))."""

    @staticmethod
    def calculate_from_bytes(artifact_bytes: bytes) -> str:
        return compute_sha256(artifact_bytes)


@dataclass(frozen=True)
class CalibrationProvenanceRecord:
    """Calibration Provenance Record (NADR-23 SS5.5 R18-R22).

    Campos minimos R18: corpus_identity, metric_configuration, parameters,
    result, timestamp. Campos adicionales: identidades (R20), referencia al
    protocolo aprobado y condiciones de ejecucion (R19), y distinguibilidad
    de origen de parametros (SS5.7 R28): NORMATIVE_DESIGN vs EMPIRICAL.
    """

    corpus_identity: str
    metric_configuration: str
    parameters: FrozenParameters
    result: str
    timestamp: str
    parameter_identity: str
    experiment_identity: str
    result_identity: str
    protocol_identity: str
    calibration_run: str
    parameters_origin: str

    def to_mapping(self) -> dict[str, object]:
        return {
            "corpus_identity": self.corpus_identity,
            "metric_configuration": self.metric_configuration,
            "parameters": {
                "nss_hard_fail": self.parameters.nss_hard_fail,
                "nss_warning": self.parameters.nss_warning,
                "cost_weights": list(self.parameters.cost_weights),
                "warning_threshold": self.parameters.warning_threshold,
            },
            "result": self.result,
            "timestamp": self.timestamp,
            "parameter_identity": self.parameter_identity,
            "experiment_identity": self.experiment_identity,
            "result_identity": self.result_identity,
            "protocol_identity": self.protocol_identity,
            "calibration_run": self.calibration_run,
            "parameters_origin": self.parameters_origin,
        }


@dataclass(frozen=True)
class EvaluationProvenanceRecord:
    """Evaluation Provenance Record (NADR-23 SS5.8 R29-R31).

    Registro independiente del Calibration Provenance Record, pero trazable
    hacia el experimento que origino los parametros congelados via
    calibration_provenance_reference (experiment identity).
    """

    corpus_identity: str
    configuration_identity: str
    frozen_parameters_identity: str
    result: str
    timestamp: str
    result_identity: str
    evaluation_kind: str
    calibration_provenance_reference: str
    limitations: tuple[str, ...] = ()

    def to_mapping(self) -> dict[str, object]:
        return {
            "corpus_identity": self.corpus_identity,
            "configuration_identity": self.configuration_identity,
            "frozen_parameters_identity": self.frozen_parameters_identity,
            "result": self.result,
            "timestamp": self.timestamp,
            "result_identity": self.result_identity,
            "evaluation_kind": self.evaluation_kind,
            "calibration_provenance_reference": self.calibration_provenance_reference,
            "limitations": list(self.limitations),
        }
