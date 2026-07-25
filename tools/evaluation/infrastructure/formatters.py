import json
from enum import Enum
from typing import Protocol, runtime_checkable

from tools.evaluation.topology.models import BenchmarkSummaryReport

EXCELLENT_THRESHOLD: float = 0.85
ACCEPTABLE_THRESHOLD: float = 0.60


def _format_key(key: object) -> str:
    """Extrae la representación en cadena de claves de métrica (Enum, StrEnum o str)."""
    if isinstance(key, Enum):
        return str(key.value)
    return str(key)


@runtime_checkable
class ReportFormatter(Protocol):
    """Protocolo para formateadores de reporte."""

    def format(self, report: BenchmarkSummaryReport) -> str:
        ...


class JsonReportFormatter(ReportFormatter):
    """Formateador serializador a JSON con tipos primitivos strictly tipados."""

    def format(self, report: BenchmarkSummaryReport) -> str:
        data: dict[str, object] = {
            "provider_name": report.provider_name,
            "total_documents": report.total_documents,
            "summary_metrics": {
                _format_key(k): v for k, v in report.summary_metrics.items()
            },
            "documents": [
                {
                    "doc_id": doc.doc_id,
                    "metrics": [
                        {
                            "metric_name": _format_key(m.metric_name),
                            "value": m.value,
                            "details": dict(m.details),
                        }
                        for m in doc.metrics
                    ],
                }
                for doc in report.document_results
            ],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


class MarkdownReportFormatter(ReportFormatter):
    """Formateador a Markdown pragmático con umbrales configurables (ADR 0017)."""

    def format(self, report: BenchmarkSummaryReport) -> str:
        lines: list[str] = [
            f"# Benchmark Topológico: `{report.provider_name}`",
            "",
            f"- **Total de Documentos Evaluados:** {report.total_documents}",
            "",
            "## Resumen Global de Métricas",
            "",
            "| Métrica Topológica | Score Promedio | Status |",
            "| :--- | :---: | :---: |",
        ]

        for metric_name, score in report.summary_metrics.items():
            if score >= EXCELLENT_THRESHOLD:
                status = "🟢 EXCELENTE"
            elif score >= ACCEPTABLE_THRESHOLD:
                status = "🟡 ACEPTABLE"
            else:
                status = "🔴 ALERTA"

            lines.append(f"| `{_format_key(metric_name)}` | **{score:.4f}** | {status} |")

        metric_keys = list(report.summary_metrics.keys())
        header_keys = " | ".join([f"`{_format_key(k)}`" for k in metric_keys])
        align_row = " | ".join([":---:" for _ in metric_keys])

        lines.extend([
            "",
            "## Desglose por Documento",
            "",
            f"| Documento ID | {header_keys} |",
            f"| :--- | {align_row} |",
        ])

        for doc in report.document_results:
            scores_map = {_format_key(m.metric_name): f"{m.value:.4f}" for m in doc.metrics}
            row_scores = [scores_map.get(_format_key(k), "N/A") for k in metric_keys]
            lines.append(f"| `{doc.doc_id}` | " + " | ".join(row_scores) + " |")

        lines.append("")
        return "\n".join(lines)