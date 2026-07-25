"""
tools/evaluation/run_benchmark.py

Fachada CLI unificada para la ejecución del Benchmark Topológico de Extracción.
Conecta la infraestructura de persistencia (BenchmarkPersistenceGateway) y emite
reportes formateados en Markdown y JSON (ADR 0017).
"""

import argparse
import sys
from pathlib import Path

from core.benchmark.persistence import BenchmarkPersistenceGateway
from tools.evaluation.application.benchmark_service import TopologyBenchmarkService
from tools.evaluation.infrastructure.corpus_repository import (
    LocalFileSystemCorpusRepository,
)
from tools.evaluation.infrastructure.formatters import (
    JsonReportFormatter,
    MarkdownReportFormatter,
)
from tools.evaluation.topology.metrics import (
    MetricRegistry,
    UnknownMetricProfileError,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI para la ejecución del Benchmark Topológico de Extracción."
    )
    parser.add_argument(
        "--provider",
        type=str,
        required=True,
        help="Nombre del proveedor a evaluar (ej. pymupdf, docling).",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default="calibration_v1",
        help="Nombre del corpus de evaluación (default: calibration_v1).",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="default",
        help="Perfil de métricas a resolver desde MetricRegistry (default: default).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/benchmark"),
        help="Directorio de destino para los reportes.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    repo = LocalFileSystemCorpusRepository()
    persistence = BenchmarkPersistenceGateway(output_dir=str(args.output_dir))

    try:
        metrics = MetricRegistry.resolve(args.profile)
    except UnknownMetricProfileError as err:
        print(f"❌ Error de Configuración: {err}", file=sys.stderr)
        sys.exit(1)

    service = TopologyBenchmarkService(metrics=metrics)

    try:
        corpus_docs = repo.load_corpus_documents(
            provider_name=args.provider,
            corpus_name=args.corpus,
        )
    except FileNotFoundError as err:
        print(f"❌ Error de Infraestructura: {err}", file=sys.stderr)
        sys.exit(1)

    if not corpus_docs:
        print("❌ Error: No se encontraron pares válidos para evaluar.", file=sys.stderr)
        sys.exit(1)

    print(
        f"🚀 Ejecutando Benchmark Topológico para `{args.provider}` sobre `{args.corpus}` "
        f"({len(corpus_docs)} docs, perfil: '{args.profile}')..."
    )

    report = service.evaluate_corpus(
        provider_name=args.provider,
        documents=corpus_docs,
    )

    md_formatter = MarkdownReportFormatter()
    json_formatter = JsonReportFormatter()

    md_output = md_formatter.format(report)
    json_output = json_formatter.format(report)

    print("\n" + md_output)

    md_file = persistence.save_artifact(
        f"{args.provider}_{args.corpus}_report.md", md_output
    )
    json_file = persistence.save_artifact(
        f"{args.provider}_{args.corpus}_report.json", json_output
    )

    print(f"✅ Reporte Markdown guardado en: {md_file}")
    print(f"✅ Reporte JSON guardado en:     {json_file}")


if __name__ == "__main__":
    main()