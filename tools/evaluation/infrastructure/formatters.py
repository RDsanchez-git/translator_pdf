import json
from typing import Protocol, runtime_checkable

from tools.evaluation.topology.models import BenchmarkSummaryReport

EXCELLENT_THRESHOLD: float = 0.85
ACCEPTABLE_THRESHOLD: float = 0.60


@runtime_checkable
class ReportFormatter(Protocol):
    """Protocolo simple para formateadores de reporte."""

    def format(self, report: BenchmarkSummaryReport) -> str:
        ...


class JsonReportFormatter(ReportFormatter):
    """Formateador serializador a JSON con tipos primitivos estrictos."""

    def format(self, report: BenchmarkSummaryReport) -> str:
        data: dict[str, object] = {
            "provider_name": report.provider_name,
            "total_documents": report.total_documents,
            "summary_metrics": {
                k.value: v for k, v in report.summary_metrics.items()
            },
            "documents": [
                {
                    "doc_id": doc.doc_id,
                    "metrics": [
                        {
                            "metric_name": m.metric_name.value,
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
    """Formateador a Markdown pragmático con umbrales configurables."""

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

            lines.append(f"| `{metric_name.value}` | **{score:.4f}** | {status} |")

        lines.extend([
            "",
            "## Desglose por Documento",
            "",
            "| Documento ID | " + " | ".join([f"`{k.value}`" for k in report.summary_metrics.keys()]) + " |",
            "| :--- | " + " | ".join([":---:" for _ in report.summary_metrics.keys()]) + " |",
        ])

        for doc in report.document_results:
            scores_map = {m.metric_name: f"{m.value:.4f}" for m in doc.metrics}
            row_scores = [scores_map.get(k, "N/A") for k in report.summary_metrics.keys()]
            lines.append(f"| `{doc.doc_id}` | " + " | ".join(row_scores) + " |")

        lines.append("")
        return "\n".join(lines)