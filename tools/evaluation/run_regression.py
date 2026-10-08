"""
tools/evaluation/run_regression.py

Entry point CLI para la evaluación de regresión topológica graduada.

NADR-F17BIS-19 §5.5:
- R20: Reutiliza build_extraction_pipeline() para generar runtime AST.
- R21: Orquesta carga de manifiesto, verificación de integridad, evaluación
       y emisión de veredicto.
- R22: Exit code diferenciado: 0 = PASS, 1 = WARNING, 2 = HARD_FAIL.

NADR-F17BIS-29 §5.1:
- R1-R3: Perfil de ejecución explícito con cobertura declarada.
- R24-R27: Mismo verification entry point para todos los perfiles.

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
import subprocess
import sys
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from bootstrap.topology import (
    DefaultNodeMatchingPolicy,
    build_canonical_engine_configuration,
    create_topology_evaluator,
)
from core.ast.enums import ContentNodeType
from core.benchmark.corpus.integrity import (
    BaselineIntegrityError,
    GTUnreadableError,
    PdfMissingError,
    verify_manifest_hash,
    verify_pdf_hash,
)
from core.benchmark.corpus.models import CorpusManifest
from core.benchmark.corpus.use_cases import LoadCorpusManifestUseCase
from core.benchmark.ground_truth.completeness import BaselineCompletenessVerifier
from core.benchmark.ground_truth.errors import IncompleteBaselineError
from core.benchmark.ground_truth.models import (
    GroundTruthLifecycleState,
    SealedOracle,
    hydrate_ground_truth,
)
from core.benchmark.ground_truth.use_cases import LoadGroundTruthUseCase
from core.benchmark.topology.criticality.costs import (
    CriticalityAwareCostContext,
    DEFAULT_CRITICALITY_WEIGHTS,
)
from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.evaluators.recall import EntityRecallEvaluator
from core.benchmark.topology.regression import (
    JsonRegressionReportFormatter,
    MarkdownRegressionReportFormatter,
    RegressionAdapter,
    RegressionEvaluationStrategy,
    RegressionReport,
    RegressionVerdict,
    build_regression_report,
)
from core.benchmark.topology.regression.configuration import (
    ConfigurationFingerprintCalculator,
)
from core.benchmark.verification.identity_chain import (
    SCHEMA_VERSION,
    build_identity_chain,
    build_profile_identity,
    build_result_identity,
)
from core.benchmark.verification.outcome import (
    VerificationOutcome,
    resolve_operational_outcome,
)
from core.benchmark.verification.profiles import (
    VerificationProfile,
    get_profile_document_ids,
)
from core.benchmark.verification.report import (
    ContinuousVerificationReport,
    EvaluationArtifacts,
    JsonContinuousVerificationReportFormatter,
)
from core.shared.crypto import compute_sha256_stream
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import (
    LocalFileSystemGroundTruthArtifactAdapter,
    LocalFileSystemGroundTruthReader,
)

import uuid
from core.benchmark.verification.execution_metadata import ExecutionMetadata




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
        help="Directorio del corpus canónico.",
    )
    parser.add_argument(
        "--pdf-dir",
        type=Path,
        required=True,
        help="Directorio de PDFs del corpus.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/regression"),
        help="Directorio de salida para reportes.",
    )
    parser.add_argument(
        "--inject-timestamp",
        action="store_true",
        help="Inyectar timestamp en el reporte (NADR-19 §5.7 R29).",
    )
    parser.add_argument(
        "--profile",
        choices=["FULL", "SMOKE"],
        default="FULL",
        help="Perfil de ejecución (NADR-29 §5.1 R1). FULL evalúa todo el corpus, SMOKE evalúa subset representativo.",
    )
    return parser.parse_args()


def _get_subject_identity() -> str | None:
    """Obtiene el commit SHA del production pipeline (NADR-28 §5.1 R3).

    Imperative Shell: I/O de subprocess. Fallback a None si git no está
    accesible (limitación observable, NADR-28 §5.5 R29).

    Returns:
        Commit SHA o None si git no está accesible.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _build_report_filename(execution_id: str, timestamp_shell: str) -> str:
    """Construye el filename único del reporte (NADR-28 §5.4 R21).

    execution_id[:16] es un prefix corto para legibilidad; el hash
    completo está en el contenido del reporte (identity_chain.execution_id).

    Args:
        execution_id: Hash de la identidad de ejecución.
        timestamp_shell: Timestamp UTC generado por el Imperative Shell.

    Returns:
        Filename único.
    """
    return f"regression_report_{execution_id[:16]}_{timestamp_shell}.json"


def _build_timestamp_shell() -> str:
    """Genera timestamp UTC para filename (Imperative Shell).

    Formato ISO 8601 con guiones (HH-MM-SS) para cross-platform
    (Windows no permite ':' en filenames).

    Este timestamp NO va en el contenido del reporte (respeta
    NADR-19 §5.7 R29); solo se usa para unicidad del filename
    (NADR-28 §5.4 R21).
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _run_evaluation(
    corpus_dir: Path,
    pdf_dir: Path,
    output_dir: Path,
    inject_timestamp: bool,
    manifest: CorpusManifest,
    declared_manifest_hash: str,
    profile: VerificationProfile,
) -> EvaluationArtifacts:
    """Ejecuta Pasos 3-5: pipeline, evaluación, construcción de reporte.

    NO escribe archivos (eso lo hace main() como Imperative Shell).
    Retorna EvaluationArtifacts con el RegressionReport, config_fingerprint
    y cost_weights para que main() construya el ContinuousVerificationReport
    y escriba JSON + Markdown.

    NADR-29 §5.1 R3: Filtra documentos por perfil de ejecución antes
    de evaluar. Todos los perfiles usan el mismo mecanismo de evaluación
    (NADR-29 §5.5 R24-R27).

    Imperative Shell: orquesta I/O de lectura (PDFs, GTs). Cualquier
    excepción no controlada se propaga al caller para ser traducida a
    EXECUTION_FAILURE.

    Returns:
        EvaluationArtifacts con regression_report, config_fingerprint,
        y cost_weights.
    """
    # ── Paso 3: Construir pipeline de evaluación ─────────────────────
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

    config = build_canonical_engine_configuration(
        matching_policy=matching_policy,
        cost_context=cost_context,
    )
    config_fingerprint = ConfigurationFingerprintCalculator.calculate(config)

    extraction_pipeline = build_extraction_pipeline()

    gt_reader = LocalFileSystemGroundTruthReader(base_path=corpus_dir)
    load_gt_uc = LoadGroundTruthUseCase(reader=gt_reader)

    adapter = RegressionAdapter()

    # ── Paso 3b: Filtrar documentos por perfil (NADR-29 §5.1 R3) ────
    profile_document_ids = get_profile_document_ids(profile, manifest)
    filtered_documents = [
        doc for doc in manifest.documents
        if doc.document_id in profile_document_ids
    ]

    # ── Paso 4: Evaluar cada documento del perfil ────────────────────
    document_reports = []
    for doc_metadata in filtered_documents:
        doc_id = doc_metadata.document_id

        nodes = load_gt_uc.execute(doc_id)
        oracle = hydrate_ground_truth(
            document_id=doc_id,
            nodes=nodes,
            state=GroundTruthLifecycleState.SEALED,
        )
        assert isinstance(oracle, SealedOracle)

        adapter.verify_document_identity(oracle, doc_metadata)
        adapter.verify_sealed_state(doc_metadata)
        adapter.verify_oracle_integrity(oracle, doc_metadata)

        pdf_path = pdf_dir / f"{doc_id}.pdf"
        runtime_ast = extraction_pipeline.parse(str(pdf_path))

        eval_report = strategy.evaluate_regression(
            document_id=doc_id,
            candidate_ast=runtime_ast,
            ground_truth_ast=oracle.nodes,
        )
        document_reports.append(eval_report)

    # ── Paso 5: Construir reporte de corpus ──────────────────────────
    generated_at = (
        datetime.now(timezone.utc).isoformat() if inject_timestamp else None
    )
    regression_report = build_regression_report(
        corpus_version=manifest.corpus_version.value,
        evaluation_reports=document_reports,
        generated_at=generated_at,
        configuration_fingerprint=config_fingerprint,
    )

    # ── Paso 7: Retornar artefactos (la escritura JSON la hace main) ─
    return EvaluationArtifacts(
        regression_report=regression_report,
        config_fingerprint=config_fingerprint,
        cost_weights=cost_context.weights,
    )


def main() -> None:
    """Entry point principal."""
    args = parse_args()

    corpus_dir: Path = args.corpus_dir
    pdf_dir: Path = args.pdf_dir
    output_dir: Path = args.output_dir
    inject_timestamp: bool = args.inject_timestamp
    profile = VerificationProfile(args.profile)

    # ── Estado operacional (NADR-27 §5.1 R1) ─────────────────────────
    baseline_failed = False
    execution_failed = False
    scientific_verdict: RegressionVerdict | None = None
    reason = ""

    # ── Estado para identity chain ───────────────────────────────────
    regression_report: RegressionReport | None = None
    config_fingerprint: str | None = None
    cost_weights: dict[NodeCriticality, float] | None = None
    declared_manifest_hash = ""
    manifest: CorpusManifest | None = None

    # ── Pasos 1-2b: Precondiciones de baseline (Gate 1) ──────────────
    try:
        corpus_loader = LocalFileSystemCorpusLoader(base_path=corpus_dir)
        raw_dto = corpus_loader.load_raw_manifest()
        declared_manifest_hash = raw_dto.manifest_hash
        load_manifest_uc = LoadCorpusManifestUseCase(reader=corpus_loader)
        manifest = load_manifest_uc.execute()

        verify_baseline_materialized(pdf_dir, manifest)
        verify_baseline_physical_integrity(manifest, declared_manifest_hash, pdf_dir)

        manifest_doc_ids = frozenset(d.document_id for d in manifest.documents)

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

        artifact_adapter = LocalFileSystemGroundTruthArtifactAdapter(base_path=corpus_dir)
        artifact_doc_ids = frozenset(artifact_adapter.list_artifact_ids())
        adapter = RegressionAdapter()
        adapter.verify_completeness(manifest_doc_ids, artifact_doc_ids)

        gt_reader = LocalFileSystemGroundTruthReader(base_path=corpus_dir)
        load_gt_uc = LoadGroundTruthUseCase(reader=gt_reader)
        verify_ground_truth_preconditions(load_gt_uc, manifest)

    except (BaselineIntegrityError, IncompleteBaselineError, OSError, ValueError) as e:
        # OSError cubre FileNotFoundError (materialización) y errores de I/O.
        # ValueError cubre json.JSONDecodeError y pydantic.ValidationError
        # (manifest corrupto o con schema inválido): una referencia ilegible
        # es fallo de integridad de la baseline, no un crash silencioso
        # (DF-11; NADR-27 §5.6 R34; NADR-28 §5.3 R14). Mismo patrón ya
        # validado en verify_ground_truth_preconditions (Gate 1, Task 1.2.3).
        # El catch-all de EXECUTION_FAILURE (exit 4) permanece para lo
        # realmente inesperado fuera de las precondiciones de baseline.
        baseline_failed = True
        reason = str(e)

    # ── Pasos 3-7: Evaluación (Task 2.1.3 catch-all) ─────────────────
    if not baseline_failed and manifest is not None:
        try:
            artifacts = _run_evaluation(
                corpus_dir=corpus_dir,
                pdf_dir=pdf_dir,
                output_dir=output_dir,
                inject_timestamp=inject_timestamp,
                manifest=manifest,
                declared_manifest_hash=declared_manifest_hash,
                profile=profile,
            )
            regression_report = artifacts.regression_report
            config_fingerprint = artifacts.config_fingerprint
            cost_weights = artifacts.cost_weights
            scientific_verdict = regression_report.corpus_verdict
        except Exception as e:
            execution_failed = True
            reason = str(e)

    # ── Resolución operacional (NADR-27 §5.3 R11-R15) ────────────────
    result = resolve_operational_outcome(
        baseline_integrity_failed=baseline_failed,
        execution_failed=execution_failed,
        scientific_verdict=scientific_verdict,
        reason=reason,
    )

    # ── Construir result_identity (NADR-28 §5.2 R13) ─────────────────
    if regression_report is not None:
        regression_json = JsonRegressionReportFormatter().format(regression_report)
    else:
        regression_json = None

    result_identity = build_result_identity(
        outcome_value=result.outcome.value,
        scientific_verdict_value=(
            result.scientific_verdict.value
            if result.scientific_verdict is not None
            else None
        ),
        regression_report_json=regression_json,
    )

    # ── Construir profile_identity (NADR-29 §5.6 R28-R31) ────────────
    if manifest is not None:
        profile_document_ids = get_profile_document_ids(profile, manifest)
    else:
        profile_document_ids = frozenset()

    profile_identity = build_profile_identity(
        profile_name=profile.value,
        document_ids=profile_document_ids,
    )

    # ── Construir identity chain (NADR-28 §5.1 R6, NADR-29 §5.6 R28) ─
    subject_identity = _get_subject_identity()

    configuration_identity = (
        config_fingerprint if config_fingerprint is not None else "NONE"
    )
    chain_cost_weights = (
        cost_weights if cost_weights is not None else dict(DEFAULT_CRITICALITY_WEIGHTS)
    )
    baseline_identity = declared_manifest_hash if declared_manifest_hash else "UNAVAILABLE"

    identity_chain = build_identity_chain(
        baseline_identity=baseline_identity,
        subject_identity=subject_identity,
        configuration_identity=configuration_identity,
        cost_weights=chain_cost_weights,
        profile_identity=profile_identity,
        result_identity=result_identity,
    )
    
    # ── Construir ContinuousVerificationReport (NADR-28 §5.3 R14) ────
    # Generar telemetry_execution_id inline (Task 3.4.2)
    telemetry_execution_id = uuid.uuid4().hex[:16]
    cv_report = ContinuousVerificationReport(
        schema_version=SCHEMA_VERSION,
        identity_chain=identity_chain,
        operational_result=result,
        coverage=tuple(sorted(profile_document_ids)),
        regression_report=regression_report,
        # NUEVO (DF-13): metadata operacional con model_de_execution
        execution_metadata=ExecutionMetadata(
            model_de_execution="sequential_regression",
            execution_timestamp_iso8601=datetime.now(timezone.utc).isoformat(),
            telemetry_execution_id=telemetry_execution_id,
        ),
    )

    # ── Persistir con filename único (NADR-28 §5.4 R21) ──────────────
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp_shell = _build_timestamp_shell()
    filename = _build_report_filename(identity_chain.execution_id, timestamp_shell)
    json_path = output_dir / filename

    cv_formatter = JsonContinuousVerificationReportFormatter()
    json_path.write_text(cv_formatter.format(cv_report), encoding="utf-8")

    # ── Escribir Markdown (para humanos, filename fijo) ────────────────
    # Solo si hay regression_report (PASS/REGRESSION).
    # Para BASELINE_INTEGRITY_FAILURE/EXECUTION_FAILURE no hay contenido
    # científico que reportar en Markdown.
    if regression_report is not None:
        md_path = output_dir / "regression_report.md"
        md_path.write_text(
            MarkdownRegressionReportFormatter().format(regression_report),
            encoding="utf-8",
        )

    # ── Salida operacional (NADR-27 §5.6 R31) ────────────────────────
    if result.outcome is not VerificationOutcome.PASS:
        print(f"{result.outcome.value}: {result.reason}", file=sys.stderr)

    sys.exit(result.exit_code)


if __name__ == "__main__":
    main()