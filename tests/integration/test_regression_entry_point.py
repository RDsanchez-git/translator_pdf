"""
Tests de integración del entry point de regresión (NADR-19 §5.5 R20-R22).

Verifica:
- NADR-19 §5.5 R20: Reutiliza build_extraction_pipeline().
- NADR-19 §5.5 R21: Orquestación completa.
- NADR-19 §5.5 R22: Exit code diferenciado (0/1/2).
- NADR-19 §5.4 R18-R19: Fail-Fast ante oráculo no verificado.

Nota: Estos tests usan fixtures en memoria y mocks con spec= para evitar
dependencia del corpus canónico real (que se materializa en Fase 5).
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
from core.benchmark.ground_truth.errors import IncompleteBaselineError
from core.benchmark.ground_truth.identity import OracleSemanticIdentityCalculator
from core.benchmark.topology.regression.models import (
    RegressionCriticalitySignal,
    RegressionEvaluationReport,
    RegressionVerdict,
)
from infra.adapters.pdf_parser import PdfParserAdapter
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from infra.fs.ground_truth_store import (
    LocalFileSystemGroundTruthArtifactAdapter,
    LocalFileSystemGroundTruthReader,
)
from core.benchmark.topology.regression.strategy import RegressionEvaluationStrategy


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


def _setup_dirs(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Crea directorios de prueba."""
    corpus_dir = tmp_path / "corpus"
    pdf_dir = tmp_path / "pdfs"
    output_dir = tmp_path / "output"
    corpus_dir.mkdir()
    pdf_dir.mkdir()
    (corpus_dir / "ground_truth").mkdir()
    return corpus_dir, pdf_dir, output_dir


def _run_entry_point(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    manifest: CorpusManifest,
    nodes: tuple[ASTNode, ...],
    strategy_report: RegressionEvaluationReport | None = None,
) -> int:
    """Helper que configura todos los mocks y ejecuta el entry point.

    Returns:
        Exit code capturado.
    """
    corpus_dir, pdf_dir, output_dir = _setup_dirs(tmp_path)

    mock_loader = MagicMock(spec=LocalFileSystemCorpusLoader)
    mock_artifact = MagicMock(spec=LocalFileSystemGroundTruthArtifactAdapter)
    mock_artifact.list_artifact_ids.return_value = tuple(
        d.document_id for d in manifest.documents
    )
    mock_gt_reader = MagicMock(spec=LocalFileSystemGroundTruthReader)
    mock_gt_reader.load_ground_truth.return_value = nodes
    mock_pipeline = MagicMock(spec=PdfParserAdapter)
    mock_pipeline.parse.return_value = list(nodes)

    patches = [
        patch(
            "tools.evaluation.run_regression.LocalFileSystemCorpusLoader",
            return_value=mock_loader,
        ),
        patch(
            "tools.evaluation.run_regression.LoadCorpusManifestUseCase"
        ),
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
        ),
        patch(
            "tools.evaluation.run_regression.build_extraction_pipeline",
            return_value=mock_pipeline,
        ),
    ]

    with patches[0], patches[1] as mock_load_uc, patches[2], patches[3], \
         patches[4] as mock_gt_uc, patches[5]:
        mock_load_uc.return_value.execute.return_value = manifest
        mock_gt_uc.return_value.execute.return_value = nodes

        if strategy_report is not None:
            strategy_patch = patch(
                "tools.evaluation.run_regression.RegressionEvaluationStrategy"
            )
            with strategy_patch as mock_strategy_cls:
                mock_strategy = MagicMock(spec=RegressionEvaluationStrategy)
                mock_strategy.evaluate_regression.return_value = strategy_report
                mock_strategy_cls.return_value = mock_strategy

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
        else:
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
    """Tests de exit codes (NADR-19 §5.5 R22)."""

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

        mock_loader = MagicMock(spec=LocalFileSystemCorpusLoader)
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

            with pytest.raises(IncompleteBaselineError):
                main()


class TestReportFiles:
    """Tests de generación de reportes."""

    def test_report_files_created(self, tmp_path, monkeypatch):
        """Verifica que los archivos de reporte se crean."""
        corpus_dir, pdf_dir, output_dir = _setup_dirs(tmp_path)

        nodes = (_make_node("n1"),)
        oracle_hash = OracleSemanticIdentityCalculator.calculate(nodes)
        manifest = _make_manifest(
            doc_ids=["doc1"],
            oracle_hashes={"doc1": oracle_hash},
        )
        report = _make_eval_report(verdict=RegressionVerdict.PASS)

        mock_loader = MagicMock(spec=LocalFileSystemCorpusLoader)
        mock_artifact = MagicMock(spec=LocalFileSystemGroundTruthArtifactAdapter)
        mock_artifact.list_artifact_ids.return_value = ("doc1",)
        mock_gt_reader = MagicMock(spec=LocalFileSystemGroundTruthReader)
        mock_gt_reader.load_ground_truth.return_value = nodes
        mock_pipeline = MagicMock(spec=PdfParserAdapter)
        mock_pipeline.parse.return_value = list(nodes)

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
                "tools.evaluation.run_regression.build_extraction_pipeline",
                return_value=mock_pipeline,
            ),
            patch(
                "tools.evaluation.run_regression.RegressionEvaluationStrategy"
            ) as mock_strategy_cls,
        ):
            mock_load_uc.return_value.execute.return_value = manifest
            mock_gt_uc.return_value.execute.return_value = nodes
            mock_strategy = MagicMock(spec=RegressionEvaluationStrategy)
            mock_strategy.evaluate_regression.return_value = report
            mock_strategy_cls.return_value = mock_strategy

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

            with pytest.raises(SystemExit):
                main()

            # Verificar que los archivos se crearon
            assert (output_dir / "regression_report.json").exists()
            assert (output_dir / "regression_report.md").exists()

            # Verificar que el JSON es válido
            json_content = (output_dir / "regression_report.json").read_text()
            data = json.loads(json_content)
            assert "corpus_verdict" in data
            assert "documents" in data
            assert data["corpus_verdict"] == "PASS"

    def test_deterministic_report(self, tmp_path, monkeypatch):
        """NADR-19 §5.7 R29: Dos ejecuciones producen el mismo JSON."""
        corpus_dir, pdf_dir, output_dir = _setup_dirs(tmp_path)

        nodes = (_make_node("n1"),)
        oracle_hash = OracleSemanticIdentityCalculator.calculate(nodes)
        manifest = _make_manifest(
            doc_ids=["doc1"],
            oracle_hashes={"doc1": oracle_hash},
        )
        report = _make_eval_report(verdict=RegressionVerdict.PASS)

        mock_loader = MagicMock(spec=LocalFileSystemCorpusLoader)
        mock_artifact = MagicMock(spec=LocalFileSystemGroundTruthArtifactAdapter)
        mock_artifact.list_artifact_ids.return_value = ("doc1",)
        mock_gt_reader = MagicMock(spec=LocalFileSystemGroundTruthReader)
        mock_gt_reader.load_ground_truth.return_value = nodes
        mock_pipeline = MagicMock(spec=PdfParserAdapter)
        mock_pipeline.parse.return_value = list(nodes)

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
                "tools.evaluation.run_regression.build_extraction_pipeline",
                return_value=mock_pipeline,
            ),
            patch(
                "tools.evaluation.run_regression.RegressionEvaluationStrategy"
            ) as mock_strategy_cls,
        ):
            mock_load_uc.return_value.execute.return_value = manifest
            mock_gt_uc.return_value.execute.return_value = nodes
            mock_strategy = MagicMock(spec=RegressionEvaluationStrategy)
            mock_strategy.evaluate_regression.return_value = report
            mock_strategy_cls.return_value = mock_strategy

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

            with pytest.raises(SystemExit):
                main()

            json_1 = (output_dir / "regression_report.json").read_text()

            # Ejecutar de nuevo
            with pytest.raises(SystemExit):
                main()

            json_2 = (output_dir / "regression_report.json").read_text()

            assert json_1 == json_2


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