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
    build_canonical_engine_configuration,
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
from core.benchmark.topology.regression.configuration import ConfigurationFingerprintCalculator
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

from core.benchmark.corpus.models import CorpusManifest

from collections.abc import Iterator

from core.benchmark.corpus.integrity import (
    PdfMissingError,
    verify_manifest_hash,
    verify_pdf_hash,
    BaselineIntegrityError,
)
from core.shared.crypto import compute_sha256_stream


from core.benchmark.corpus.integrity import (
    GTUnreadableError
)
from core.benchmark.ground_truth.completeness import BaselineCompletenessVerifier
from core.benchmark.ground_truth.errors import IncompleteBaselineError

# Exit codes (NADR-19 §5.5 R22)
EXIT_PASS = 0
EXIT_WARNING = 1
EXIT_HARD_FAIL = 2
# NADR-F17BIS-26 §5.6 R25: fallo de integridad de la baseline NO es regresión.
# Exit code separado de los resultados de evaluación (0, 1, 2).
EXIT_BASELINE_INTEGRITY_FAILURE = 3

def _iter_pdf_chunks(pdf_path: Path, chunk_size: int = 8 * 1024 * 1024) -> Iterator[bytes]:
    """Itera sobre chunks de un PDF para cálculo de hash en streaming.

    Evita cargar el PDF completo en memoria. Chunk size 8 MB.
    """
    with open(pdf_path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk


def verify_baseline_physical_integrity(
    manifest: CorpusManifest,
    manifest_hash: str,
    pdf_dir: Path,
) -> None:
    """Orquesta la verificación de integridad física de la baseline.

    NADR-F17BIS-26 §5.2 R6-R10.

    Imperative Shell: lee archivos del filesystem, calcula hashes,
    llama a las funciones puras del core.

    Nota: manifest_hash se pasa como parámetro separado porque
    CorpusManifest (modelo de dominio) no incluye el hash. El hash
    vive en el DTO (RawCorpusManifestDTO.manifest_hash) y se extrae
    antes de la conversión a dominio.

    Orden de verificación (fail-fast):
    1. manifest_hash contra recalculado (R8)
    2. sha256 de cada PDF contra manifest (R9)

    Args:
        manifest: Manifest del corpus cargado (modelo de dominio).
        manifest_hash: manifest_hash declarado en el DTO del manifest.
        pdf_dir: Directorio que contiene los PDFs del corpus.

    Raises:
        ManifestHashMismatchError: Si manifest_hash no coincide (R8).
        PdfMissingError: Si algún PDF listado en el manifest no existe.
        PdfIntegrityError: Si el sha256 de algún PDF no coincide (R9).
    """
    # R8: Verificar manifest_hash contra recalculado
    verify_manifest_hash(
        declared_hash=manifest_hash,
        version=manifest.corpus_version,
        documents=manifest.documents,
    )

    # R6, R9: Verificar existencia e integridad de cada PDF
    for doc in manifest.documents:
        pdf_path = pdf_dir / f"{doc.document_id}.pdf"

        if not pdf_path.exists():
            raise PdfMissingError(
                document_id=doc.document_id,
                pdf_path=str(pdf_path),
            )

        actual_sha256 = compute_sha256_stream(_iter_pdf_chunks(pdf_path))
        verify_pdf_hash(
            document_id=doc.document_id,
            expected_sha256=doc.fingerprint.sha256,
            actual_sha256=actual_sha256,
        )


def verify_ground_truth_preconditions(
    load_gt_uc: LoadGroundTruthUseCase,
    manifest: CorpusManifest,
) -> None:
    """Verifica legibilidad de Ground Truths antes de evaluación.

    NADR-F17BIS-26 §5.3 R13: Un artefacto ilegible o corrupto MUST NOT
    ser tratado como válido.

    NADR-F17BIS-26 §5.3 R14: La verificación de precondiciones MUST
    preceder a la evaluación topológica.

    Imperative Shell: intenta cargar cada GT, captura errores de I/O y
    parseo, los convierte en errores de dominio.

    Excepciones capturadas:
    - OSError: errores de filesystem (FileNotFoundError, PermissionError)
    - ValueError: errores de parseo JSON y validación Pydantic
      (json.JSONDecodeError y pydantic.ValidationError son subclasses)

    NO captura TypeError, AttributeError, KeyError (errores de programación).

    Args:
        load_gt_uc: Caso de uso para cargar Ground Truths.
        manifest: Manifest del corpus cargado.

    Raises:
        GTUnreadableError: Si algún GT es ilegible o corrupto.
    """
    for doc in manifest.documents:
        try:
            load_gt_uc.execute(doc.document_id)
        except GTUnreadableError:
            raise
        except (OSError, ValueError) as e:
            raise GTUnreadableError(
                document_id=doc.document_id,
                reason=str(e),
            ) from e


def verify_baseline_materialized(
    pdf_dir: Path,
    manifest: CorpusManifest,
) -> None:
    """Verifica que la baseline está materializada antes de ejecutar.

    NADR-F17BIS-26 §5.1 R2: La baseline MUST estar físicamente materializada
    en el entorno de ejecución antes de iniciar la evaluación.

    NADR-F17BIS-26 §5.1 R3: La materialización MUST conservar correspondencia
    verificable con los artefactos que constituyen la baseline canónica.

    Args:
        pdf_dir: Directorio que contiene los PDFs del corpus.
        manifest: Manifiesto del corpus cargado.

    Raises:
        FileNotFoundError: Si el directorio de PDFs no existe o si faltan
            PDFs esperados según el manifest.
    """
    # NADR-F17BIS-26 §5.1 R2: Verificar directorio de PDFs
    if not pdf_dir.exists():
        raise FileNotFoundError(
            f"PDF directory not found: {pdf_dir}. "
            f"The baseline must be physically materialized before evaluation "
            f"(NADR-F17BIS-26 §5.1 R2)."
        )

    # NADR-F17BIS-26 §5.1 R3: Verificar correspondencia de PDFs
    missing_pdfs: list[str] = []
    for doc in manifest.documents:
        pdf_path = pdf_dir / f"{doc.document_id}.pdf"
        if not pdf_path.exists():
            missing_pdfs.append(doc.document_id)

    if missing_pdfs:
        raise FileNotFoundError(
            f"Missing PDFs for baseline materialization: "
            f"{', '.join(sorted(missing_pdfs))}. "
            f"The materialization must preserve verifiable correspondence "
            f"with the canonical baseline artifacts "
            f"(NADR-F17BIS-26 §5.1 R3)."
        )


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

    # ── Verificación de precondiciones de la baseline (NADR-26 §5.6 R23-R25) ──
    # Si la baseline no puede demostrar identidad, integridad o completitud,
    # se termina con EXIT_BASELINE_INTEGRITY_FAILURE (3).
    # Este exit code es distinto de los resultados de evaluación (0, 1, 2)
    # porque un fallo de integridad NO es una regresión del production pipeline.
    try:
        # ── Paso 1: Cargar manifiesto ────────────────────────────────────
        corpus_loader = LocalFileSystemCorpusLoader(base_path=corpus_dir)
        raw_dto = corpus_loader.load_raw_manifest()
        declared_manifest_hash = raw_dto.manifest_hash
        load_manifest_uc = LoadCorpusManifestUseCase(reader=corpus_loader)
        manifest = load_manifest_uc.execute()

        # ── Paso 1b: Verificar materialización (Task 1.2.1) ─────────────
        verify_baseline_materialized(pdf_dir, manifest)

        # ── Paso 1c: Verificar integridad física (Task 1.2.2) ───────────
        verify_baseline_physical_integrity(manifest, declared_manifest_hash, pdf_dir)

        # Calcular manifest_doc_ids (necesario para Paso 1d y Paso 2)
        manifest_doc_ids = frozenset(d.document_id for d in manifest.documents)

        # ── Paso 1d: Completitud biyectiva de PDFs (Task 1.2.3) ─────────
        pdf_doc_ids = frozenset(
            p.stem for p in pdf_dir.glob("*.pdf") if p.is_file()
        )
        pdf_completeness_errors = BaselineCompletenessVerifier.verify_pdf_ids(
            manifest_doc_ids=manifest_doc_ids,
            pdf_doc_ids=pdf_doc_ids,
        )
        if pdf_completeness_errors:
            raise IncompleteBaselineError(
                "PDF completeness violations: " + "; ".join(pdf_completeness_errors)
            )

        # ── Paso 2: Completitud biyectiva de GTs (existente) ────────────
        artifact_adapter = LocalFileSystemGroundTruthArtifactAdapter(base_path=corpus_dir)
        artifact_doc_ids = frozenset(artifact_adapter.list_artifact_ids())
        adapter = RegressionAdapter()
        adapter.verify_completeness(manifest_doc_ids, artifact_doc_ids)

        # ── Paso 2b: Legibilidad de Ground Truths (Task 1.2.3) ──────────
        gt_reader = LocalFileSystemGroundTruthReader(base_path=corpus_dir)
        load_gt_uc = LoadGroundTruthUseCase(reader=gt_reader)
        verify_ground_truth_preconditions(load_gt_uc, manifest)

    except (BaselineIntegrityError, IncompleteBaselineError, FileNotFoundError) as e:
        # NADR-F17BIS-26 §5.6 R24-R25: Un fallo de integridad de la baseline
        # se distingue semánticamente de una divergencia del production pipeline.
        # No se interpreta como regresión científica.
        print(f"BASELINE_INTEGRITY_FAILURE: {e}", file=sys.stderr)
        sys.exit(EXIT_BASELINE_INTEGRITY_FAILURE)

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
    
    # NADR-22 §5.6 R19: Configuracion canonica + fingerprint
    config = build_canonical_engine_configuration(
        matching_policy=matching_policy,
        cost_context=cost_context,
    )
    config_fingerprint = ConfigurationFingerprintCalculator.calculate(config)

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
        configuration_fingerprint=config_fingerprint,
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