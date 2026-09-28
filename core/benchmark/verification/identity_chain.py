"""Identity Chain para Continuous Verification (NADR-F17BIS-28).

NADR-F17BIS-28 §5.1 R6: La identity chain MUST permitir establecer la
relación entre: Execution → Subject → Baseline → Configuration →
Parameters → Evaluation → Result.

NADR-F17BIS-28 §5.2 R8: Las identidades derivadas de entradas
equivalentes MUST ser deterministas.

Este módulo compone los calculadores existentes en regression/provenance.py
para construir una identity chain completa. No los redefine (Reuse Before
Invent, ENGINEERING_PRINCIPLES §I).

Separación de bounded contexts:
- core/benchmark/topology/regression/provenance.py → calculadores (NADR-23)
- core/benchmark/verification/identity_chain.py → composición (NADR-28)
"""
from __future__ import annotations

from dataclasses import dataclass

from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.regression.models import DEFAULT_REGRESSION_THRESHOLDS
from core.benchmark.topology.regression.provenance import (
    FrozenParameters,
    ParameterIdentityCalculator,
)
from core.shared.crypto import compute_sha256


# Constante para schema version (NADR-28 §5.4 R24)
SCHEMA_VERSION = "cv-1.0.0"


@dataclass(frozen=True)
class IdentityChain:
    """Identity chain completa de una ejecución de Continuous Verification.

    NADR-F17BIS-28 §5.1 R6: Cadena completa Execution → Subject → Baseline →
    Configuration → Parameters → Evaluation → Result.

    Todos los campos son strings (hashes SHA-256) excepto subject_identity
    que puede ser None si git no está accesible.

    Invariante: execution_id es hash determinista de los componentes de
    identidad (baseline, subject, config, params). NO incluye result para
    evitar circularidad.
    """

    schema_version: str
    execution_id: str
    baseline_identity: str  # manifest_hash
    subject_identity: str | None  # commit_sha o None
    configuration_identity: str  # config_fingerprint
    parameter_identity: str  # hash de FrozenParameters
    result_identity: str | None  # hash del resultado, None si no se completó
    limitations: tuple[str, ...]  # limitaciones observables (R29)

    def to_mapping(self) -> dict[str, object]:
        """Serializa a dict para JSON."""
        return {
            "schema_version": self.schema_version,
            "execution_id": self.execution_id,
            "baseline_identity": self.baseline_identity,
            "subject_identity": self.subject_identity,
            "configuration_identity": self.configuration_identity,
            "parameter_identity": self.parameter_identity,
            "result_identity": self.result_identity,
            "limitations": list(self.limitations),
        }


def build_parameter_identity(
    cost_weights: dict[NodeCriticality, float],
    warning_threshold: int = 1,
    nss_hard_fail: float | None = None,
    nss_warning: float | None = None,
) -> str:
    """Construye parameter_identity desde los parámetros de evaluación.

    NADR-F17BIS-28 §5.1 R5: Los parámetros que afectan el resultado MUST
    estar representados en la identidad.

    NADR-F17BIS-28 §5.2 R8: Determinista. Orden fijo: CRITICAL, WARNING, INFO.

    Args:
        cost_weights: Dict de pesos por criticidad.
        warning_threshold: Umbral de advertencia (default 1).
        nss_hard_fail: Umbral NSS para HARD_FAIL (default desde DEFAULT_REGRESSION_THRESHOLDS).
        nss_warning: Umbral NSS para WARNING (default desde DEFAULT_REGRESSION_THRESHOLDS).

    Returns:
        Hash SHA-256 determinista de los parámetros.
    """
    if nss_hard_fail is None:
        nss_hard_fail = DEFAULT_REGRESSION_THRESHOLDS.nss_hard_fail
    if nss_warning is None:
        nss_warning = DEFAULT_REGRESSION_THRESHOLDS.nss_warning

    # Orden determinista: CRITICAL, WARNING, INFO
    cost_weights_tuple = (
        cost_weights[NodeCriticality.CRITICAL],
        cost_weights[NodeCriticality.WARNING],
        cost_weights[NodeCriticality.INFO],
    )

    frozen = FrozenParameters(
        nss_hard_fail=nss_hard_fail,
        nss_warning=nss_warning,
        cost_weights=cost_weights_tuple,
        warning_threshold=warning_threshold,
    )
    return ParameterIdentityCalculator.calculate(frozen)


def build_execution_id(
    baseline_identity: str,
    subject_identity: str | None,
    configuration_identity: str,
    parameter_identity: str,
) -> str:
    """Construye execution_id determinista (NADR-28 §5.1 R1, §5.2 R8).

    El execution_id es hash de los componentes de identidad de entrada.
    NO incluye result para evitar circularidad.

    NADR-28 §5.2 R8: Dos ejecuciones con mismas entradas producen el
    mismo execution_id.

    NADR-28 §5.4 R21: Para evitar sobrescritura, el filename incluye
    execution_id + timestamp_shell (generado por Imperative Shell).

    Args:
        baseline_identity: manifest_hash del corpus.
        subject_identity: commit_sha o None.
        configuration_identity: config_fingerprint.
        parameter_identity: hash de FrozenParameters.

    Returns:
        Hash SHA-256 determinista.
    """
    payload = (
        f"{baseline_identity}|"
        f"{subject_identity if subject_identity is not None else 'NONE'}|"
        f"{configuration_identity}|"
        f"{parameter_identity}"
    )
    return compute_sha256(payload.encode("utf-8"))


def build_result_identity(
    outcome_value: str,
    scientific_verdict_value: str | None,
    regression_report_json: str | None = None,
) -> str:
    """Construye result_identity (NADR-F17BIS-28 §5.2 R13).

    Hash del resultado operacional + científico. NO incluye la identity
    chain para evitar circularidad.

    regression_report_json es opcional: para BASELINE_INTEGRITY_FAILURE y
    EXECUTION_FAILURE no hay reporte científico (NADR-27 §5.2 R8, R9).

    Args:
        outcome_value: Valor de VerificationOutcome.
        scientific_verdict_value: Valor de RegressionVerdict o None.
        regression_report_json: JSON del RegressionReport o None.

    Returns:
        Hash SHA-256 del resultado.
    """
    payload = (
        f"{regression_report_json if regression_report_json is not None else 'NONE'}|"
        f"{outcome_value}|"
        f"{scientific_verdict_value if scientific_verdict_value is not None else 'NONE'}"
    )
    return compute_sha256(payload.encode("utf-8"))


def build_identity_chain(
    baseline_identity: str,
    subject_identity: str | None,
    configuration_identity: str,
    cost_weights: dict[NodeCriticality, float],
    warning_threshold: int = 1,
    nss_hard_fail: float | None = None,
    nss_warning: float | None = None,
    result_identity: str | None = None,
) -> IdentityChain:
    """Construye la identity chain completa (NADR-28 §5.1 R6).

    Función pura que compone todos los componentes. El Imperative Shell
    obtiene subject_identity via git y llama esta función.

    Args:
        baseline_identity: manifest_hash.
        subject_identity: commit_sha o None.
        configuration_identity: config_fingerprint.
        cost_weights: Pesos de criticidad.
        warning_threshold: Umbral de advertencia.
        nss_hard_fail: Umbral NSS para HARD_FAIL.
        nss_warning: Umbral NSS para WARNING.
        result_identity: Hash del resultado (None si no se completó).

    Returns:
        IdentityChain completa.
    """
    parameter_identity = build_parameter_identity(
        cost_weights=cost_weights,
        warning_threshold=warning_threshold,
        nss_hard_fail=nss_hard_fail,
        nss_warning=nss_warning,
    )

    execution_id = build_execution_id(
        baseline_identity=baseline_identity,
        subject_identity=subject_identity,
        configuration_identity=configuration_identity,
        parameter_identity=parameter_identity,
    )

    # Construir limitaciones observables (NADR-28 §5.5 R29)
    limitations: list[str] = []
    if subject_identity is None:
        limitations.append("subject_identity unavailable (git not accessible)")
    if result_identity is None:
        limitations.append("result_identity unavailable (evaluation did not complete)")

    return IdentityChain(
        schema_version=SCHEMA_VERSION,
        execution_id=execution_id,
        baseline_identity=baseline_identity,
        subject_identity=subject_identity,
        configuration_identity=configuration_identity,
        parameter_identity=parameter_identity,
        result_identity=result_identity,
        limitations=tuple(limitations),
    )