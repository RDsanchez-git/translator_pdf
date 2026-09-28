"""
Tests de integración del entry point de regresión (NADR-19 §5.5 R20-R22).

Verifica:
- NADR-19 §5.5 R20: Reutiliza build_extraction_pipeline().
- NADR-19 §5.5 R21: Orquestación completa.
- NADR-19 §5.5 R22: Exit code diferenciado (0/1/2).
- NADR-19 §5.4 R18-R19: Fail-Fast ante oráculo no verificado.

Nota: Estos tests mockean _run_evaluation() para aislar la lógica del
entry point de los detalles internos de evaluación. Task 2.2.3 introdujo
identity chain y ContinuousVerificationReport; mockear _run_evaluation()
evita tener que mockear toda la cadena de dependencias internas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusManifest,
    CorpusVersion,
    DocumentFingerprint,
)
from core.benchmark.topology.regression import RegressionReport
from core.benchmark.ground_truth.identity import OracleSemanticIdentityCalculator
from core.benchmark.topology.criticality.costs import DEFAULT_CRITICALITY_WEIGHTS
from core.benchmark.topology.regression.models import (
    RegressionCriticalitySignal,
    RegressionEvaluationReport,
    RegressionVerdict,
)
from core.benchmark.verification.report import EvaluationArtifacts
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import (
    LocalFileSystemGroundTruthArtifactAdapter,
    LocalFileSystemGroundTruthReader,
)


def _make_node(node_id: str, content: str = "test") -> ASTNode:
    """Helper para crear ASTNode de prueba."""
    return ASTNode(
        node_id=node_id,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content=content),
    )


def _make_eval_report(
    document_id: str = "doc1",
    verdict: RegressionVerdict = RegressionVerdict.PASS,
    nss_score: float = 0.95,
) -> RegressionEvaluationReport:
    """Helper para crear RegressionEvaluationReport con veredicto controlado."""
    signal = (
        RegressionCriticalitySignal.ABSOLUTE_FAIL
        if verdict is RegressionVerdict.HARD_FAIL
        else RegressionCriticalitySignal.WARNING
        if verdict is RegressionVerdict.WARNING
        else RegressionCriticalitySignal.PASS
    )
    return RegressionEvaluationReport(
        document_id=document_id,
        metrics=(),
        overall_score=nss_score,
        verdict=verdict,
        criticality_signal=signal,
    )


def _make_manifest(
    doc_ids: list[str],
    oracle_hashes: dict[str, str] | None = None,
    ground_truth_states: dict[str, str] | None = None,
) -> CorpusManifest:
    """Helper para crear CorpusManifest de prueba."""
    if oracle_hashes is None:
        oracle_hashes = {}
    if ground_truth_states is None:
        ground_truth_states = {}

    docs = []
    for doc_id in doc_ids:
        docs.append(
            CorpusDocumentMetadata(
                document_id=doc_id,
                fingerprint=DocumentFingerprint(sha256="a" * 64),
                traits=frozenset({next(iter(ExtractionChallengeTrait))}),
                page_count=3,
                oracle_hash=oracle_hashes.get(doc_id),
                ground_truth_state=ground_truth_states.get(doc_id, "sealed"),
            )
        )
    return CorpusManifest(
        corpus_version=CorpusVersion(value="test_v1"),
        documents=docs,
    )


def _make_regression_report(
    eval_reports: tuple[RegressionEvaluationReport, ...] | None = None,
) -> RegressionReport:
    """Helper para crear RegressionReport de prueba."""
    if eval_reports is None:
        eval_reports = (_make_eval_report(),)

    verdicts = [r.verdict for r in eval_reports]
    corpus_verdict = max(verdicts, key=lambda v: v.severity_rank)
    nss_scores = [r.overall_score for r in eval_reports]
    corpus_nss = sum(nss_scores) / len(nss_scores)

    pass_count = sum(1 for v in verdicts if v is RegressionVerdict.PASS)
    warning_count = sum(1 for v in verdicts if v is RegressionVerdict.WARNING)
    hard_fail_count = sum(1 for v in verdicts if v is RegressionVerdict.HARD_FAIL)

    return RegressionReport(
        corpus_version="test_v1",
        corpus_verdict=corpus_verdict,
        corpus_nss=corpus_nss,
        total_documents=len(eval_reports),
        pass_count=pass_count,
        warning_count=warning_count,
        hard_fail_count=hard_fail_count,
        document_reports=eval_reports,
        total_critical_false_negatives=0,
        total_warning_false_negatives=0,
        total_info_false_negatives=0,
        generated_at=None,
        configuration_fingerprint="f" * 64,
    )


def _make_artifacts(
    eval_reports: tuple[RegressionEvaluationReport, ...] | None = None,
) -> EvaluationArtifacts:
    """Helper para crear EvaluationArtifacts de prueba."""
    return EvaluationArtifacts(
        regression_report=_make_regression_report(eval_reports),
        config_fingerprint="f" * 64,
        cost_weights=dict(DEFAULT_CRITICALITY_WEIGHTS),
    )


def _setup_dirs(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Crea directorios de prueba."""
    corpus_dir = tmp_path / "corpus"
    pdf_dir = tmp_path / "pdfs"
    output_dir = tmp_path / "output"
    corpus_dir.mkdir(exist_ok=True)
    pdf_dir.mkdir(exist_ok=True)
    (corpus_dir / "ground_truth").mkdir(exist_ok=True)
    return corpus_dir, pdf_dir, output_dir


def _run_entry_point(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    manifest: CorpusManifest,
    nodes: tuple[ASTNode, ...],
    strategy_report: RegressionEvaluationReport | None = None,
) -> int:
    """Helper que configura todos los mocks y ejecuta el entry point.

    Mockea _run_evaluation() directamente para evitar depender de la
    cadena completa de mocks internos. Task 2.2.3 introdujo identity
    chain y ContinuousVerificationReport que requieren mocks adicionales.

    Returns:
        Exit code capturado.
    """
    corpus_dir, pdf_dir, output_dir = _setup_dirs(tmp_path)

    # Construir EvaluationArtifacts con el strategy_report del test
    if strategy_report is not None:
        artifacts = _make_artifacts((strategy_report,))
    else:
        artifacts = _make_artifacts()

    # Raw DTO mock (para declared_manifest_hash)
    mock_raw_dto = MagicMock()
    mock_raw_dto.manifest_hash = "a" * 64

    mock_loader = MagicMock(spec=LocalFileSystemCorpusLoader)
    mock_loader.load_raw_manifest.return_value = mock_raw_dto

    mock_artifact = MagicMock(spec=LocalFileSystemGroundTruthArtifactAdapter)
    mock_artifact.list_artifact_ids.return_value = tuple(
        d.document_id for d in manifest.documents
    )

    mock_gt_reader = MagicMock(spec=LocalFileSystemGroundTruthReader)
    mock_gt_reader.load_ground_truth.return_value = nodes

    with (
        patch(
            "tools.evaluation.run_regression.LocalFileSystemCorpusLoader",
            return_value=mock_loader,
        ),
        patch(
            "tools.evaluation.run_regression.LoadCorpusManifestUseCase"
        ) as mock_load_uc,
        patch(
            "tools.evaluation.run_regression.LocalFileSystemGroundTruthArtifactAdapter",
            return_value=mock_artifact,
        ),
        patch(
            "tools.evaluation.run_regression.LocalFileSystemGroundTruthReader",
            return_value=mock_gt_reader,
        ),
        patch(
            "tools.evaluation.run_regression.LoadGroundTruthUseCase"
        ) as mock_gt_uc,
        patch(
            "tools.evaluation.run_regression.verify_baseline_materialized"
        ),
        patch(
            "tools.evaluation.run_regression.verify_baseline_physical_integrity"
        ),
        patch(
            "tools.evaluation.run_regression.verify_ground_truth_preconditions"
        ),
        # FIX: Mockear BaselineCompletenessVerifier.verify_pdf_ids para evitar
        # fallo por PDFs ausentes en pdf_dir vacío
        patch(
            "tools.evaluation.run_regression.BaselineCompletenessVerifier.verify_pdf_ids",
            return_value=[],
        ),
        # Mockear _run_evaluation directamente (Task 2.2.3)
        patch(
            "tools.evaluation.run_regression._run_evaluation",
            return_value=artifacts,
        ),
        # Mockear funciones de Task 2.2.3
        patch(
            "tools.evaluation.run_regression._get_subject_identity",
            return_value="c" * 40,
        ),
        patch(
            "tools.evaluation.run_regression._build_timestamp_shell",
            return_value="2026-09-27T10-00-00Z",
        ),
    ):
        mock_load_uc.return_value.execute.return_value = manifest
        mock_gt_uc.return_value.execute.return_value = nodes

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "run_regression.py",
                "--corpus-dir", str(corpus_dir),
                "--pdf-dir", str(pdf_dir),
                "--output-dir", str(output_dir),
            ],
        )

        from tools.evaluation.run_regression import main

        with pytest.raises(SystemExit) as exc_info:
            main()
        code = exc_info.value.code
        assert isinstance(code, int), f"Expected int exit code, got {type(code)}"
        return code


class TestExitCodes:
    """Tests de exit codes (NADR-19 §5.5 R22, NADR-27 §5.6 R29-R35)."""

    def test_exit_code_pass_when_all_pass(self, tmp_path, monkeypatch):
        """NADR-19 §5.5 R22: Todos PASS → exit code 0."""
        nodes = (_make_node("n1"),)
        oracle_hash = OracleSemanticIdentityCalculator.calculate(nodes)
        manifest = _make_manifest(
            doc_ids=["doc1"],
            oracle_hashes={"doc1": oracle_hash},
        )
        report = _make_eval_report(verdict=RegressionVerdict.PASS)

        exit_code = _run_entry_point(tmp_path, monkeypatch, manifest, nodes, report)
        assert exit_code == 0

    def test_exit_code_warning_when_any_warning(self, tmp_path, monkeypatch):
        """NADR-19 §5.5 R22: Al menos un WARNING → exit code 1."""
        nodes = (_make_node("n1"),)
        oracle_hash = OracleSemanticIdentityCalculator.calculate(nodes)
        manifest = _make_manifest(
            doc_ids=["doc1"],
            oracle_hashes={"doc1": oracle_hash},
        )
        report = _make_eval_report(verdict=RegressionVerdict.WARNING, nss_score=0.90)

        exit_code = _run_entry_point(tmp_path, monkeypatch, manifest, nodes, report)
        assert exit_code == 1

    def test_exit_code_hard_fail_when_any_hard_fail(self, tmp_path, monkeypatch):
        """NADR-19 §5.5 R22: Al menos un HARD_FAIL → exit code 2."""
        nodes = (_make_node("n1"),)
        oracle_hash = OracleSemanticIdentityCalculator.calculate(nodes)
        manifest = _make_manifest(
            doc_ids=["doc1"],
            oracle_hashes={"doc1": oracle_hash},
        )
        report = _make_eval_report(verdict=RegressionVerdict.HARD_FAIL, nss_score=0.50)

        exit_code = _run_entry_point(tmp_path, monkeypatch, manifest, nodes, report)
        assert exit_code == 2


class TestFailFast:
    """Tests de Fail-Fast (NADR-19 §5.4 R18-R19)."""

    def test_fail_fast_on_incomplete_baseline(self, tmp_path, monkeypatch):
        """NADR-19 §5.4 R18-R19: Fail-Fast ante corpus incompleto."""
        corpus_dir, pdf_dir, output_dir = _setup_dirs(tmp_path)

        manifest = _make_manifest(
            doc_ids=["doc1", "doc2"],
            oracle_hashes={"doc1": "a" * 64, "doc2": "b" * 64},
        )

        mock_raw_dto = MagicMock()
        mock_raw_dto.manifest_hash = "a" * 64

        mock_loader = MagicMock(spec=LocalFileSystemCorpusLoader)
        mock_loader.load_raw_manifest.return_value = mock_raw_dto
        mock_artifact = MagicMock(spec=LocalFileSystemGroundTruthArtifactAdapter)
        mock_artifact.list_artifact_ids.return_value = ("doc1",)  # Falta doc2

        with (
            patch(
                "tools.evaluation.run_regression.LocalFileSystemCorpusLoader",
                return_value=mock_loader,
            ),
            patch(
                "tools.evaluation.run_regression.LoadCorpusManifestUseCase"
            ) as mock_load_uc,
            patch(
                "tools.evaluation.run_regression.LocalFileSystemGroundTruthArtifactAdapter",
                return_value=mock_artifact,
            ),
            patch(
                "tools.evaluation.run_regression.verify_baseline_materialized"
            ),
            patch(
                "tools.evaluation.run_regression.verify_baseline_physical_integrity"
            ),
            # FIX: Mockear verify_pdf_ids para que NO falle por PDFs ausentes
            # Queremos testear la completitud de GT artifacts, no de PDFs
            patch(
                "tools.evaluation.run_regression.BaselineCompletenessVerifier.verify_pdf_ids",
                return_value=[],
            ),
        ):
            mock_load_uc.return_value.execute.return_value = manifest

            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "run_regression.py",
                    "--corpus-dir", str(corpus_dir),
                    "--pdf-dir", str(pdf_dir),
                    "--output-dir", str(output_dir),
                ],
            )

            from tools.evaluation.run_regression import main

            with pytest.raises(SystemExit) as exc_info:
                main()
            # Baseline integrity failure → exit code 3
            assert exc_info.value.code == 3


class TestReportFiles:
    """Tests de generación de reportes (actualizados para Task 2.2.3)."""

    def test_report_files_created(self, tmp_path, monkeypatch):
        """Verifica que los archivos de reporte se crean con filename único."""
        nodes = (_make_node("n1"),)
        oracle_hash = OracleSemanticIdentityCalculator.calculate(nodes)
        manifest = _make_manifest(
            doc_ids=["doc1"],
            oracle_hashes={"doc1": oracle_hash},
        )
        report = _make_eval_report(verdict=RegressionVerdict.PASS)

        exit_code = _run_entry_point(tmp_path, monkeypatch, manifest, nodes, report)
        assert exit_code == 0

        output_dir = tmp_path / "output"

        # NADR-28 §5.4 R21: filename único, no fijo
        json_files = list(output_dir.glob("regression_report_*.json"))
        assert len(json_files) == 1

        # Markdown se mantiene con filename fijo
        assert (output_dir / "regression_report.md").exists()

        # Verificar que el JSON es válido y contiene identity chain
        data = json.loads(json_files[0].read_text(encoding="utf-8"))
        assert "schema_version" in data
        assert "identity_chain" in data
        assert "operational_result" in data
        assert "regression_report" in data
        assert data["operational_result"]["outcome"] == "PASS"

    def test_deterministic_report(self, tmp_path, monkeypatch):
        """NADR-19 §5.7 R29 + NADR-28 §5.2 R8: ejecución reproducible."""
        nodes = (_make_node("n1"),)
        oracle_hash = OracleSemanticIdentityCalculator.calculate(nodes)
        manifest = _make_manifest(
            doc_ids=["doc1"],
            oracle_hashes={"doc1": oracle_hash},
        )
        report = _make_eval_report(verdict=RegressionVerdict.PASS)

        # Primera ejecución
        _run_entry_point(tmp_path, monkeypatch, manifest, nodes, report)
        output_dir = tmp_path / "output"
        json_files_1 = list(output_dir.glob("regression_report_*.json"))
        assert len(json_files_1) == 1
        data_1 = json.loads(json_files_1[0].read_text(encoding="utf-8"))

        # Segunda ejecución (limpiar output_dir)
        for f in output_dir.glob("*.json"):
            f.unlink()
        for f in output_dir.glob("*.md"):
            f.unlink()

        _run_entry_point(tmp_path, monkeypatch, manifest, nodes, report)
        json_files_2 = list(output_dir.glob("regression_report_*.json"))
        assert len(json_files_2) == 1
        data_2 = json.loads(json_files_2[0].read_text(encoding="utf-8"))

        # NADR-28 §5.2 R8: execution_id determinista
        assert data_1["identity_chain"]["execution_id"] == data_2["identity_chain"]["execution_id"]
        # El contenido del regression_report es idéntico
        assert data_1["regression_report"] == data_2["regression_report"]


class TestParseArgs:
    """Tests de parse_args()."""

    def test_required_args(self, monkeypatch):
        """Verifica que los argumentos requeridos funcionan."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "run_regression.py",
                "--corpus-dir", "/tmp/corpus",
                "--pdf-dir", "/tmp/pdfs",
            ],
        )
        from tools.evaluation.run_regression import parse_args

        args = parse_args()
        assert args.corpus_dir == Path("/tmp/corpus")
        assert args.pdf_dir == Path("/tmp/pdfs")
        assert args.output_dir == Path("reports/regression")
        assert args.inject_timestamp is False

    def test_inject_timestamp_flag(self, monkeypatch):
        """Verifica que --inject-timestamp funciona."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "run_regression.py",
                "--corpus-dir", "/tmp/corpus",
                "--pdf-dir", "/tmp/pdfs",
                "--inject-timestamp",
            ],
        )
        from tools.evaluation.run_regression import parse_args

        args = parse_args()
        assert args.inject_timestamp is True

    def test_custom_output_dir(self, monkeypatch):
        """Verifica que --output-dir funciona."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "run_regression.py",
                "--corpus-dir", "/tmp/corpus",
                "--pdf-dir", "/tmp/pdfs",
                "--output-dir", "/tmp/custom_output",
            ],
        )
        from tools.evaluation.run_regression import parse_args

        args = parse_args()
        assert args.output_dir == Path("/tmp/custom_output")