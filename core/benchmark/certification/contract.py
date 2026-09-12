"""Contrato de ejecucion de certificacion (NADR-24 SS5.1 R1-R5).

Tres capas distinguibles (R5):
  (a) ExecutionOutcome: SUCCESS / EXECUTION_FAILURE
  (b) ScientificResult: ACCEPTED / REJECTED
  (c) CertificationStatus: CERTIFIED / REJECTED / EXECUTION_FAILURE

CERTIFIED es condicion compuesta (R4): requiere simultaneamente ejecucion
exitosa, resultado cientifico aceptado, evidencia completa y invariantes
satisfechas. La ausencia de cualquier componente impide CERTIFIED.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionOutcome(Enum):
    """Capa (a): resultado operacional de la ejecucion."""

    SUCCESS = "SUCCESS"
    EXECUTION_FAILURE = "EXECUTION_FAILURE"


class ScientificResult(Enum):
    """Capa (b): resultado cientifico de la evaluacion."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class CertificationStatus(Enum):
    """Capa (c): estado logico de la certificacion."""

    CERTIFIED = "CERTIFIED"
    REJECTED = "REJECTED"
    EXECUTION_FAILURE = "EXECUTION_FAILURE"


class ExecutionMode(Enum):
    """Modo de ejecucion (trazabilidad R31 con evaluation_kind de Wave 3.3)."""

    SANITY_VALIDATION = "SANITY_VALIDATION"
    FINAL_EVALUATION = "FINAL_EVALUATION"


@dataclass(frozen=True)
class CertificationExecutionContract:
    """Contrato de ejecucion explicito y verificable (R1-R2)."""

    corpus_identity: str
    configuration_identity: str
    frozen_parameters_identity: str
    execution_mode: ExecutionMode


def compose_certification_status(
    execution: ExecutionOutcome,
    scientific: ScientificResult | None,
    evidence_complete: bool,
    invariants_satisfied: bool,
) -> CertificationStatus:
    """Compone el estado logico de certificacion (R4-R5)."""
    if execution is ExecutionOutcome.EXECUTION_FAILURE:
        return CertificationStatus.EXECUTION_FAILURE
    if not evidence_complete or not invariants_satisfied:
        return CertificationStatus.EXECUTION_FAILURE
    if scientific is None:
        # R4: ausencia de cualquier componente impide CERTIFIED; sin resultado
        # cientifico no hay rechazo cientifico, hay fallo de ejecucion.
        return CertificationStatus.EXECUTION_FAILURE
    if scientific is ScientificResult.ACCEPTED:
        return CertificationStatus.CERTIFIED
    return CertificationStatus.REJECTED
