"""Reporte de Continuous Verification con identity chain completa (NADR-F17BIS-28).

NADR-F17BIS-28 §5.3 R14: Cada ejecución MUST producir evidencia persistente
suficiente para reconstruir su contexto de evaluación.

NADR-F17BIS-28 §5.6 R31: La evidencia MUST permitir distinguir el resultado
de las condiciones que hicieron posible producirlo.

Este módulo crea un wrapper que compone:
- RegressionReport (resultado científico, NADR-19) — opcional si no hay evaluación
- ContinuousVerificationResult (resultado operacional, NADR-27)
- IdentityChain (identidad de ejecución, NADR-28)
- schema_version (versionado del esquema, NADR-28 §5.4 R24)

Resuelve GAP-6.3-02: configuration_fingerprint ahora se serializa.

Separación de bounded contexts:
- core/benchmark/topology/regression/report.py → RegressionReport (NADR-19)
- core/benchmark/verification/report.py → ContinuousVerificationReport (NADR-28)
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from core.benchmark.topology.regression.report import (
    RegressionReport,
    serialize_evaluation_report,
)
from core.benchmark.verification.identity_chain import (
    IdentityChain
)
from core.benchmark.verification.outcome import ContinuousVerificationResult

from core.benchmark.topology.criticality.models import NodeCriticality

from core.benchmark.verification.execution_metadata import ExecutionMetadata

@dataclass(frozen=True)
class ContinuousVerificationReport:
    """Reporte completo de Continuous Verification con identity chain.

    NADR-F17BIS-28 §5.3 R14: Evidencia persistente suficiente para
    reconstruir el contexto de evaluación.

    NADR-F17BIS-28 §5.6 R31: Permite distinguir resultado de condiciones.

    regression_report es opcional: None para BASELINE_INTEGRITY_FAILURE
    y EXECUTION_FAILURE (NADR-27 §5.2 R8, R9).

    Inmutable y determinista (ENGINEERING_PRINCIPLES §II, §III).
    """

    schema_version: str
    identity_chain: IdentityChain
    operational_result: ContinuousVerificationResult
    coverage: tuple[str, ...]
    regression_report: RegressionReport | None = None
    execution_metadata: ExecutionMetadata | None = None  # NUEVO (DF-13)


@dataclass(frozen=True)
class EvaluationArtifacts:
    """Artefactos producidos por la evaluación (Pasos 3-7).

    NADR-F17BIS-28: encapsula lo que el Imperative Shell necesita para
    componer la identity chain y el ContinuousVerificationReport.

    Ajuste de diseño (Task 2.2.3): se usa dataclass en lugar de
    tuple[RegressionReport, str] porque main() también necesita
    cost_weights para construir la IdentityChain. Una tupla de 3
    elementos posicionales sería frágil.
    """

    regression_report: RegressionReport
    config_fingerprint: str
    cost_weights: dict[NodeCriticality, float]


@runtime_checkable
class ContinuousVerificationReportFormatter(Protocol):
    """Protocolo para formateadores de ContinuousVerificationReport.

    OCP: nuevos formatos se agregan como nuevas clases sin modificar
    las existentes. Consistente con RegressionReportFormatter.
    """

    def format(self, report: ContinuousVerificationReport) -> str:
        ...


class JsonContinuousVerificationReportFormatter(
    ContinuousVerificationReportFormatter
):
    """Formateador JSON que serializa identity chain completa.

    Resuelve GAP-6.3-02: configuration_fingerprint ahora se serializa
    dentro del regression_report.

    NADR-F17BIS-28 §5.3 R14-R19: Evidencia persistente con identity chain.
    NADR-F17BIS-28 §5.6 R31-R34: Resultado vinculado a condiciones.
    """

    def format(self, report: ContinuousVerificationReport) -> str:
        data: dict[str, object] = {
            "schema_version": report.schema_version,
            "identity_chain": report.identity_chain.to_mapping(),
            # NUEVO (DF-13): metadata operacional separada de científica
            "execution_metadata": (
                {
                    "model_de_execution": report.execution_metadata.model_de_execution,
                    "execution_timestamp_iso8601": report.execution_metadata.execution_timestamp_iso8601,
                    "telemetry_execution_id": report.execution_metadata.telemetry_execution_id,
                }
                if report.execution_metadata is not None
                else None
            ),
            "operational_result": {
                "outcome": report.operational_result.outcome.value,
                "scientific_verdict": (
                    report.operational_result.scientific_verdict.value
                    if report.operational_result.scientific_verdict is not None
                    else None
                ),
                "exit_code": report.operational_result.exit_code,
                "reason": report.operational_result.reason,
            },
            "coverage": list(report.coverage),  # ← NUEVO
        }

        if report.regression_report is not None:
            data["regression_report"] = _serialize_regression_report(
                report.regression_report
            )

        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)


def _serialize_regression_report(
    report: RegressionReport,
) -> dict[str, object]:
    """Serializa RegressionReport a dict, incluyendo configuration_fingerprint.

    Resuelve GAP-6.3-02: configuration_fingerprint ahora se serializa.
    Usa serialize_evaluation_report pública (no función privada).
    """
    result: dict[str, object] = {
        "corpus_version": report.corpus_version,
        "corpus_verdict": report.corpus_verdict.value,
        "corpus_nss": report.corpus_nss,
        "total_documents": report.total_documents,
        "pass_count": report.pass_count,
        "warning_count": report.warning_count,
        "hard_fail_count": report.hard_fail_count,
        "total_critical_false_negatives": report.total_critical_false_negatives,
        "total_warning_false_negatives": report.total_warning_false_negatives,
        "total_info_false_negatives": report.total_info_false_negatives,
        "generated_at": report.generated_at,
        "documents": [
            serialize_evaluation_report(r) for r in report.document_reports
        ],
    }

    # GAP-6.3-02: configuration_fingerprint ahora se serializa
    if report.configuration_fingerprint is not None:
        result["configuration_fingerprint"] = report.configuration_fingerprint

    return result

__all__ = [
    "ContinuousVerificationReport",
    "ContinuousVerificationReportFormatter",
    "JsonContinuousVerificationReportFormatter",
    "EvaluationArtifacts",
]