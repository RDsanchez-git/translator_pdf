"""
tools/evaluation/run_regression.py

Entry point CLI para la evaluación de regresión topológica graduada.

NADR-F17BIS-19 §5.5:
- R20: Reutiliza build_extraction_pipeline() para generar runtime AST.
- R21: Orquesta carga de manifiesto, verificación de integridad, evaluación
       y emisión de veredicto.
- R22: Exit code diferenciado: 0 = PASS, 1 = WARNING, 2 = HARD_FAIL.

Diseño:
- Functional Core: la lógica de orquestación es pura (sin estado).
- Imperative Shell: el I/O se empuja a los bordes (file system, sys.exit).
- Reutiliza LoadCorpusManifestUseCase, LoadGroundTruthUseCase,
  RegressionAdapter, RegressionEvaluationStrategy, build_regression_report.
- Patrón CLI consistente con run_benchmark.py (argparse + main()).

Optimización de verificación:
- verify_completeness() se ejecuta UNA sola vez antes del loop
  (verificación a nivel corpus).
- Dentro del loop se ejecutan las verificaciones por documento
  (identidad, estado sellado, integridad) sin redundancia.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from bootstrap.topology import (
    DefaultNodeMatchingPolicy,
    create_topology_evaluator,
)
from core.ast.enums import ContentNodeType
from core.benchmark.corpus.use_cases import LoadCorpusManifestUseCase
from core.benchmark.ground_truth.models import (
    GroundTruthLifecycleState,
    SealedOracle,
    hydrate_ground_truth,
)
from core.benchmark.ground_truth.use_cases import LoadGroundTruthUseCase
from core.benchmark.topology.criticality.costs import CriticalityAwareCostContext
from core.benchmark.topology.evaluators.recall import EntityRecallEvaluator
from core.benchmark.topology.regression import (
    JsonRegressionReportFormatter,
    MarkdownRegressionReportFormatter,
    RegressionAdapter,
    RegressionEvaluationStrategy,
    RegressionVerdict,
    build_regression_report,
)
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import (
    LocalFileSystemGroundTruthArtifactAdapter,
    LocalFileSystemGroundTruthReader,
)

# Exit codes (NADR-19 §5.5 R22)
EXIT_PASS = 0
EXIT_WARNING = 1
EXIT_HARD_FAIL = 2


def parse_args() -> argparse.Namespace:
    """Parsea argumentos del CLI."""
    parser = argparse.ArgumentParser(
        description="CLI para la evaluación de regresión topológica graduada."
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
        default=Path("reports/regression"),
        help="Directorio de destino para los reportes (default: reports/regression).",
    )
    parser.add_argument(
        "--inject-timestamp",
        action="store_true",
        default=False,
        help="Inyectar timestamp UTC en el reporte (rompe determinismo estricto).",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point principal."""
    args = parse_args()

    corpus_dir: Path = args.corpus_dir
    pdf_dir: Path = args.pdf_dir
    output_dir: Path = args.output_dir
    inject_timestamp: bool = args.inject_timestamp

    # ── Paso 1: Cargar manifiesto ──────────────────────────────────
    corpus_loader = LocalFileSystemCorpusLoader(base_path=corpus_dir)
    load_manifest_uc = LoadCorpusManifestUseCase(reader=corpus_loader)
    manifest = load_manifest_uc.execute()

    # ── Paso 2: Verificar completitud biyectiva (UNA sola vez) ────
    manifest_doc_ids = frozenset(d.document_id for d in manifest.documents)
    artifact_adapter = LocalFileSystemGroundTruthArtifactAdapter(base_path=corpus_dir)
    artifact_doc_ids = frozenset(artifact_adapter.list_artifact_ids())

    adapter = RegressionAdapter()
    adapter.verify_completeness(manifest_doc_ids, artifact_doc_ids)

    # ── Paso 3: Construir pipeline de evaluación ──────────────────
    cost_context = CriticalityAwareCostContext()
    ted_evaluator = create_topology_evaluator(cost_context=cost_context)

    matching_policy = DefaultNodeMatchingPolicy()
    recall_evaluators: dict[ContentNodeType, EntityRecallEvaluator] = {
        node_type: EntityRecallEvaluator(node_type, matching_policy)
        for node_type in ContentNodeType
    }

    strategy = RegressionEvaluationStrategy(
        ted_evaluator=ted_evaluator,
        recall_evaluators=recall_evaluators,
    )

    extraction_pipeline = build_extraction_pipeline()

    gt_reader = LocalFileSystemGroundTruthReader(base_path=corpus_dir)
    load_gt_uc = LoadGroundTruthUseCase(reader=gt_reader)

    # ── Paso 4: Evaluar cada documento ────────────────────────────
    document_reports = []
    for doc_metadata in manifest.documents:
        doc_id = doc_metadata.document_id

        # 4a. Cargar oráculo
        nodes = load_gt_uc.execute(doc_id)
        oracle = hydrate_ground_truth(
            document_id=doc_id,
            nodes=nodes,
            state=GroundTruthLifecycleState.SEALED,
        )
        assert isinstance(oracle, SealedOracle)  # Garantizado por state=SEALED

        # 4b. Verificaciones por documento
        adapter.verify_document_identity(oracle, doc_metadata)
        adapter.verify_sealed_state(doc_metadata)
        adapter.verify_oracle_integrity(oracle, doc_metadata)

        # 4c. Generar runtime AST
        pdf_path = pdf_dir / f"{doc_id}.pdf"
        runtime_ast = extraction_pipeline.parse(str(pdf_path))

        # 4d. Evaluar
        eval_report = strategy.evaluate_regression(
            document_id=doc_id,
            candidate_ast=runtime_ast,
            ground_truth_ast=oracle.nodes,
        )
        document_reports.append(eval_report)

    # ── Paso 5: Construir reporte de corpus ────────────────────────
    generated_at = (
        datetime.now(timezone.utc).isoformat() if inject_timestamp else None
    )
    regression_report = build_regression_report(
        corpus_version=manifest.corpus_version.value,
        evaluation_reports=document_reports,
        generated_at=generated_at,
    )

    # ── Paso 6: Escribir reportes ─────────────────────────────────
    output_dir.mkdir(parents=True, exist_ok=True)

    json_formatter = JsonRegressionReportFormatter()
    md_formatter = MarkdownRegressionReportFormatter()

    json_path = output_dir / "regression_report.json"
    md_path = output_dir / "regression_report.md"

    json_path.write_text(json_formatter.format(regression_report), encoding="utf-8")
    md_path.write_text(md_formatter.format(regression_report), encoding="utf-8")

    # ── Paso 7: Exit code (NADR-19 §5.5 R22) ──────────────────────
    verdict = regression_report.corpus_verdict
    if verdict is RegressionVerdict.HARD_FAIL:
        sys.exit(EXIT_HARD_FAIL)
    elif verdict is RegressionVerdict.WARNING:
        sys.exit(EXIT_WARNING)
    else:
        sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()