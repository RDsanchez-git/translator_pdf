"""
tools/evaluation/run_df04_benchmark.py

Benchmark comparativo DF-04: ZhangShasha vs APTED.

NADR-22 §5.1 R3: APTED queda como experimental/benchmark no normativo.
FASE_4_HANDOFF §5.2 DF-04: Criterio de decisión:
  - Divergencia < 1% TED normalizado → APTED experimental sin acción adicional
  - Divergencia ≥ 1% TED normalizado → investigar causa raíz y documentar

Diseño:
- Functional Core: la lógica de comparación es pura (sin estado).
- Imperative Shell: el I/O se empuja a los bordes (file system, sys.exit).
- Reutiliza build_extraction_pipeline(), create_topology_evaluator(),
  StructuralTopologyMetric, LoadCorpusManifestUseCase, LoadGroundTruthUseCase.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path

from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from bootstrap.topology import create_topology_evaluator
from core.benchmark.corpus.use_cases import LoadCorpusManifestUseCase
from core.benchmark.ground_truth.models import (
    GroundTruthLifecycleState,
    hydrate_ground_truth,
)
from core.benchmark.ground_truth.use_cases import LoadGroundTruthUseCase
from core.benchmark.topology.costs.unit import UnitCostContext
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import LocalFileSystemGroundTruthReader
from tools.evaluation.topology.metrics.structural import StructuralTopologyMetric


@dataclass(frozen=True)
class DocumentComparison:
    """Comparación de un documento entre ZhangShasha y APTED."""
    document_id: str
    zhang_shasha_score: float
    apted_score: float
    divergence: float
    divergence_pct: float


@dataclass(frozen=True)
class DF04BenchmarkResult:
    """Resultado agregado del benchmark DF-04."""
    corpus_version: str
    total_documents: int
    avg_divergence: float
    avg_divergence_pct: float
    max_divergence_pct: float
    criterion_threshold_pct: float
    criterion_met: bool
    criterion_decision: str
    documents: tuple[DocumentComparison, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark comparativo DF-04: ZhangShasha vs APTED."
    )
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        required=True,
        help="Directorio del corpus canónico (contiene manifest.json y ground_truth/).",
    )
    parser.add_argument(
        "--pdf-dir",
        type=Path,
        required=True,
        help="Directorio que contiene los PDFs del corpus.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/df04"),
        help="Directorio de destino para el reporte (default: reports/df04).",
    )
    parser.add_argument(
        "--threshold-pct",
        type=float,
        default=1.0,
        help="Umbral de divergencia en porcentaje (default: 1.0).",
    )
    return parser.parse_args()


def run_benchmark(
    corpus_dir: Path,
    pdf_dir: Path,
    threshold_pct: float,
) -> DF04BenchmarkResult:
    """Ejecuta el benchmark comparativo DF-04.

    Functional Core: lógica pura de comparación.
    """
    # Cargar manifest
    corpus_loader = LocalFileSystemCorpusLoader(base_path=corpus_dir)
    load_manifest_uc = LoadCorpusManifestUseCase(reader=corpus_loader)
    manifest = load_manifest_uc.execute()

    # Cargar Ground Truths
    gt_reader = LocalFileSystemGroundTruthReader(base_path=corpus_dir)
    load_gt_uc = LoadGroundTruthUseCase(reader=gt_reader)

    # Construir evaluadores
    # ZhangShasha con UnitCostContext (cost model uniforme, comparable a APTED)
    cost_context = UnitCostContext()
    zhang_shasha_evaluator = create_topology_evaluator(cost_context=cost_context)

    # APTED con CostMatrix.default_v1() (cost model nativo)
    apted_metric = StructuralTopologyMetric()

    # Pipeline de extracción para generar runtime AST
    extraction_pipeline = build_extraction_pipeline()

    # Comparar cada documento
    comparisons: list[DocumentComparison] = []

    for doc_metadata in manifest.documents:
        doc_id = doc_metadata.document_id

        # Cargar oráculo sellado
        nodes = load_gt_uc.execute(doc_id)
        oracle = hydrate_ground_truth(
            document_id=doc_id,
            nodes=nodes,
            state=GroundTruthLifecycleState.SEALED,
        )

        # Generar runtime AST
        pdf_path = pdf_dir / f"{doc_id}.pdf"
        runtime_ast = extraction_pipeline.parse(str(pdf_path))

        # Evaluar con ZhangShasha
        zs_result = zhang_shasha_evaluator.evaluate(runtime_ast, oracle.nodes)
        zs_score = zs_result.primary_score

        # Evaluar con APTED
        apted_result = apted_metric.evaluate(runtime_ast, oracle.nodes)
        apted_score = apted_result.value

        # Calcular divergencia
        divergence = abs(zs_score - apted_score)
        divergence_pct = divergence * 100.0

        comparisons.append(
            DocumentComparison(
                document_id=doc_id,
                zhang_shasha_score=zs_score,
                apted_score=apted_score,
                divergence=divergence,
                divergence_pct=divergence_pct,
            )
        )

    # Agregar resultados
    total_docs = len(comparisons)
    avg_divergence = sum(c.divergence for c in comparisons) / total_docs if total_docs > 0 else 0.0
    avg_divergence_pct = avg_divergence * 100.0
    max_divergence_pct = max((c.divergence_pct for c in comparisons), default=0.0)

    criterion_met = avg_divergence_pct < threshold_pct
    criterion_decision = (
        "APTED queda como experimental sin acción adicional"
        if criterion_met
        else "Investigar causa raíz y documentar"
    )

    return DF04BenchmarkResult(
        corpus_version=manifest.corpus_version.value,
        total_documents=total_docs,
        avg_divergence=avg_divergence,
        avg_divergence_pct=avg_divergence_pct,
        max_divergence_pct=max_divergence_pct,
        criterion_threshold_pct=threshold_pct,
        criterion_met=criterion_met,
        criterion_decision=criterion_decision,
        documents=tuple(comparisons),
    )


def format_json_report(result: DF04BenchmarkResult) -> str:
    """Formatea el resultado como JSON."""
    return json.dumps(asdict(result), indent=2, ensure_ascii=False)


def format_markdown_report(result: DF04BenchmarkResult) -> str:
    """Formatea el resultado como Markdown."""
    lines = [
        "# DF-04 Benchmark: ZhangShasha vs APTED",
        "",
        f"**Corpus version:** {result.corpus_version}",
        f"**Total documents:** {result.total_documents}",
        f"**Criterion threshold:** {result.criterion_threshold_pct:.2f}%",
        "",
        "## Results",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Average divergence | {result.avg_divergence_pct:.4f}% |",
        f"| Max divergence | {result.max_divergence_pct:.4f}% |",
        f"| Criterion met | {'✅ Yes' if result.criterion_met else '❌ No'} |",
        f"| Decision | {result.criterion_decision} |",
        "",
        "## Per-document comparison",
        "",
        "| Document | ZhangShasha | APTED | Divergence |",
        "|----------|:-----------:|:-----:|:----------:|",
    ]

    for doc in result.documents:
        lines.append(
            f"| {doc.document_id} | {doc.zhang_shasha_score:.4f} | "
            f"{doc.apted_score:.4f} | {doc.divergence_pct:.4f}% |"
        )

    lines.append("")
    lines.append("## Known differences")
    lines.append("")
    lines.append("| Aspect | ZhangShasha | APTED |")
    lines.append("|--------|-------------|-------|")
    lines.append("| Cost model | UnitCostContext (uniform) | CostMatrix.default_v1 (diff substitution) |")
    lines.append("| Normalization | MaxBound: 1-TED/max(gt,cand) | 1-TED/(del*gt+ins*cand) |")
    lines.append("| Fingerprint | No .strip() | .strip() applied (H-5.2-6) |")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    print(
        f"🚀 Ejecutando DF-04 Benchmark: ZhangShasha vs APTED "
        f"sobre {args.corpus_dir} (umbral: {args.threshold_pct}%)"
    )

    result = run_benchmark(
        corpus_dir=args.corpus_dir,
        pdf_dir=args.pdf_dir,
        threshold_pct=args.threshold_pct,
    )

    # Crear directorio de salida
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Escribir reportes
    json_path = args.output_dir / "df04_benchmark.json"
    md_path = args.output_dir / "df04_benchmark.md"

    json_path.write_text(format_json_report(result), encoding="utf-8")
    md_path.write_text(format_markdown_report(result), encoding="utf-8")

    print(f"\n📊 Reporte JSON: {json_path}")
    print(f"📊 Reporte Markdown: {md_path}")
    print(f"\n{'='*60}")
    print(f"Average divergence: {result.avg_divergence_pct:.4f}%")
    print(f"Max divergence:     {result.max_divergence_pct:.4f}%")
    print(f"Threshold:          {result.criterion_threshold_pct:.2f}%")
    print(f"Criterion met:      {'✅ YES' if result.criterion_met else '❌ NO'}")
    print(f"Decision:           {result.criterion_decision}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
