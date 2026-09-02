"""
Reporte de regresión topológica graduada (NADR-F17BIS-19 §5.7).

NADR-19 §5.7 R26: RegressionReport incluye veredicto por documento y por corpus.
NADR-19 §5.7 R27: NSS calculado, métricas ponderadas por criticidad.
NADR-19 §5.7 R28: Formato Markdown legible como salida secundaria.
NADR-19 §5.7 R29: Determinismo: ausencia de marcas de tiempo físicas no
    inyectadas. Si se requiere marca temporal, MUST ser inyectada como
    parámetro externo.

Diseño:
- RegressionReport: agregado de corpus inmutable y determinista.
- build_regression_report(): función pura de construcción (Functional Core).
- RegressionReportFormatter: Protocol para formateadores (OCP).
- JsonRegressionReportFormatter: serialización JSON determinista.
- MarkdownRegressionReportFormatter: formato legible para humanos.
- Sin datetime.now() ni time.time() en ningún formatter (R29).
"""
from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from typing import Protocol, Sequence, Tuple, runtime_checkable

from core.benchmark.topology.models import MetricScoreDTO
from core.benchmark.topology.regression.aggregation import aggregate_corpus_verdicts
from core.benchmark.topology.regression.models import (
    RegressionEvaluationReport,
    RegressionVerdict,
)


@dataclass(frozen=True)
class RegressionReport:
    """Reporte agregado de regresión por corpus.

    NADR-19 §5.7 R26: Incluye veredicto por documento y por corpus.
    NADR-19 §5.7 R27: NSS calculado (corpus_nss como promedio).
    NADR-19 §5.7 R29: Determinista. generated_at inyectado externamente.

    Inmutable y determinista (ENGINEERING_PRINCIPLES §II, §III).
    """

    corpus_version: str
    corpus_verdict: RegressionVerdict
    corpus_nss: float
    total_documents: int
    pass_count: int
    warning_count: int
    hard_fail_count: int
    document_reports: Tuple[RegressionEvaluationReport, ...]
    total_critical_false_negatives: int
    total_warning_false_negatives: int
    total_info_false_negatives: int
    # NADR-19 §5.7 R29: inyectado externamente, no generado internamente.
    # Si None, el reporte no incluye timestamp (determinismo total).
    generated_at: str | None = None


def build_regression_report(
    corpus_version: str,
    evaluation_reports: Sequence[RegressionEvaluationReport],
    generated_at: str | None = None,
) -> RegressionReport:
    """Construye el reporte agregado de regresión.

    Función pura (ENGINEERING_PRINCIPLES §II). Sin I/O, sin estado.

    NADR-19 §5.7 R26: Agrega veredictos por documento en veredicto por corpus.
    NADR-19 §5.1 R3: El veredicto por corpus es el peor veredicto de todos
        los documentos individuales.

    Args:
        corpus_version: Versión del corpus evaluado.
        evaluation_reports: Secuencia de reportes por documento. No vacía.
        generated_at: Timestamp inyectado externamente (R29).
            Si None, el reporte no incluye timestamp.

    Returns:
        RegressionReport agregado.

    Raises:
        ValueError: Si la secuencia de reportes está vacía.
    """
    if not evaluation_reports:
        raise ValueError(
            "Cannot build regression report from empty evaluation reports. "
            "At least one document report is required."
        )

    corpus_verdict = aggregate_corpus_verdicts(
        tuple(r.verdict for r in evaluation_reports)
    )

    # NADR-19 §5.7 R27: NSS calculado (promedio del corpus).
    nss_scores = [r.overall_score for r in evaluation_reports]
    corpus_nss = sum(nss_scores) / len(nss_scores)

    pass_count = sum(
        1 for r in evaluation_reports if r.verdict is RegressionVerdict.PASS
    )
    warning_count = sum(
        1 for r in evaluation_reports if r.verdict is RegressionVerdict.WARNING
    )
    hard_fail_count = sum(
        1 for r in evaluation_reports if r.verdict is RegressionVerdict.HARD_FAIL
    )

    total_critical_fn = sum(
        r.critical_false_negatives for r in evaluation_reports
    )
    total_warning_fn = sum(
        r.warning_false_negatives for r in evaluation_reports
    )
    total_info_fn = sum(
        r.info_false_negatives for r in evaluation_reports
    )

    return RegressionReport(
        corpus_version=corpus_version,
        corpus_verdict=corpus_verdict,
        corpus_nss=corpus_nss,
        total_documents=len(evaluation_reports),
        pass_count=pass_count,
        warning_count=warning_count,
        hard_fail_count=hard_fail_count,
        document_reports=tuple(evaluation_reports),
        total_critical_false_negatives=total_critical_fn,
        total_warning_false_negatives=total_warning_fn,
        total_info_false_negatives=total_info_fn,
        generated_at=generated_at,
    )


# =====================================================================
# Formatters (NADR-19 §5.7 R27, R28)
# =====================================================================


@runtime_checkable
class RegressionReportFormatter(Protocol):
    """Protocolo para formateadores de reporte de regresión.

    OCP: nuevos formatos se agregan como nuevas clases sin modificar
    las existentes. Consistente con el patrón de
    tools/evaluation/infrastructure/formatters.py.
    """

    def format(self, report: RegressionReport) -> str:
        ...


class JsonRegressionReportFormatter(RegressionReportFormatter):
    """Formateador serializador a JSON.

    NADR-19 §5.7 R27: Formato JSON estructurado.
    NADR-19 §5.7 R29: Determinista (sort_keys=True, sin timestamp interno).
    """

    def format(self, report: RegressionReport) -> str:
        data: dict[str, object] = {
            "corpus_version": report.corpus_version,
            "corpus_verdict": report.corpus_verdict.value,
            "corpus_nss": report.corpus_nss,
            "total_documents": report.total_documents,
            "pass_count": report.pass_count,
            "warning_count": report.warning_count,
            "hard_fail_count": report.hard_fail_count,
            "total_critical_false_negatives": (
                report.total_critical_false_negatives
            ),
            "total_warning_false_negatives": (
                report.total_warning_false_negatives
            ),
            "total_info_false_negatives": report.total_info_false_negatives,
            "generated_at": report.generated_at,
            "documents": [
                _serialize_evaluation_report(r)
                for r in report.document_reports
            ],
        }
        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)


class MarkdownRegressionReportFormatter(RegressionReportFormatter):
    """Formateador a Markdown legible para humanos.

    NADR-19 §5.7 R28: Formato Markdown como salida secundaria.
    NADR-19 §5.7 R29: Determinista (sin timestamp interno).
    """

    def format(self, report: RegressionReport) -> str:
        lines: list[str] = [
            f"# Regression Report: Corpus `{report.corpus_version}`",
            "",
            f"- **Corpus Verdict:** `{report.corpus_verdict.value}`",
            f"- **Corpus NSS:** {report.corpus_nss:.4f}",
            f"- **Total Documents:** {report.total_documents}",
            f"- **PASS:** {report.pass_count}",
            f"- **WARNING:** {report.warning_count}",
            f"- **HARD_FAIL:** {report.hard_fail_count}",
        ]

        # NADR-19 §5.7 R29: solo incluir timestamp si fue inyectado
        if report.generated_at is not None:
            lines.append(f"- **Generated At:** {report.generated_at}")

        lines.extend([
            "",
            "## Criticality Loss Summary",
            "",
            "| Level | Total False Negatives |",
            "| :--- | :---: |",
            f"| CRITICAL | {report.total_critical_false_negatives} |",
            f"| WARNING | {report.total_warning_false_negatives} |",
            f"| INFO | {report.total_info_false_negatives} |",
            "",
            "## Document Results",
            "",
            "| Document | Verdict | NSS | Critical FN | Warning FN | Info FN |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |",
        ])

        for r in report.document_reports:
            lines.append(
                f"| `{r.document_id}` "
                f"| {r.verdict.value} "
                f"| {r.overall_score:.4f} "
                f"| {r.critical_false_negatives} "
                f"| {r.warning_false_negatives} "
                f"| {r.info_false_negatives} |"
            )

        lines.append("")
        return "\n".join(lines)


# =====================================================================
# Funciones de serialización internas (pragmático para Gate 3)
# =====================================================================


def _serialize_evaluation_report(
    report: RegressionEvaluationReport,
) -> dict[str, object]:
    """Serializa un reporte por documento a dict con tipos primitivos."""
    return {
        "document_id": report.document_id,
        "overall_score": report.overall_score,
        "verdict": report.verdict.value,
        "criticality_signal": report.criticality_signal.value,
        "critical_false_negatives": report.critical_false_negatives,
        "warning_false_negatives": report.warning_false_negatives,
        "info_false_negatives": report.info_false_negatives,
        "metrics": [
            _serialize_metric(m) for m in report.metrics
        ],
    }


def _serialize_metric(metric: MetricScoreDTO) -> dict[str, object]:
    """Serializa una métrica a dict con tipos primitivos.

    ENGINEERING_PRINCIPLES §III: tipado explícito dict[str, object].
    """
    result: dict[str, object] = {
        "metric_name": metric.metric_name,
        "primary_score": metric.primary_score,
    }
    if metric.diagnostics is not None:
        result["diagnostics"] = dataclasses.asdict(metric.diagnostics)
    return result