import argparse
import sys
from pathlib import Path

from tools.evaluation.application.benchmark_service import TopologyBenchmarkService
from tools.evaluation.infrastructure.corpus_repository import (
    LocalFileSystemCorpusRepository,
)
from tools.evaluation.infrastructure.formatters import (
    JsonReportFormatter,
    MarkdownReportFormatter,
)
from tools.evaluation.topology.metrics import default_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI para la ejecución del Benchmark Topológico de Extracción."
    )
    parser.add_argument(
        "--provider",
        type=str,
        required=True,
        help="Nombre del proveedor a evaluar (ej. pymupdf).",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default="calibration_v1",
        help="Nombre del corpus de evaluación (default: calibration_v1).",
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
    # FIX: Inyección explícita del contrato de métricas activas
    service = TopologyBenchmarkService(metrics=default_metrics())

    try:
        corpus_docs = repo.load_corpus_documents(
            provider_name=args.provider,
            corpus_name=args.corpus,
        )
    except FileNotFoundError as err:
        print(f"❌ Error de Infraestructura: {err}")
        sys.exit(1)

    if not corpus_docs:
        print("❌ Error: No se encontraron pares válidos para evaluar.")
        sys.exit(1)

    print(
        f"🚀 Ejecutando Benchmark Topológico para `{args.provider}` sobre `{args.corpus}` ({len(corpus_docs)} docs)..."
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

    args.output_dir.mkdir(parents=True, exist_ok=True)
    md_file = args.output_dir / f"{args.provider}_{args.corpus}_report.md"
    json_file = args.output_dir / f"{args.provider}_{args.corpus}_report.json"

    md_file.write_text(md_output, encoding="utf-8")
    json_file.write_text(json_output, encoding="utf-8")

    print(f"✅ Reporte Markdown guardado en: {md_file}")
    print(f"✅ Reporte JSON guardado en:     {json_file}")


if __name__ == "__main__":
    main()