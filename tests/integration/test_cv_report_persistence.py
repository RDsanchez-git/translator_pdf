"""Tests de persistencia de ContinuousVerificationReport (NADR-F17BIS-28 §5.4, §5.5).

Verifica filename único, reproducibilidad de execution_id, que el
reporte JSON contiene la identity chain completa, y los campos de
perfil (coverage, profile_identity) de Task 3.1.3.

NADR-F17BIS-29 §5.1 R3, §5.6 R28-R31: Perfil de ejecución en evidencia.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

from core.benchmark.topology.criticality.costs import DEFAULT_CRITICALITY_WEIGHTS
from core.benchmark.topology.regression.models import RegressionVerdict
from core.benchmark.topology.regression.report import RegressionReport
from core.benchmark.verification.report import EvaluationArtifacts
from tools.evaluation.run_regression import (
    _build_report_filename,
    _build_timestamp_shell,
    main,
)


@pytest.mark.unit
class TestBuildReportFilename:
    """NADR-F17BIS-28 §5.4 R21: filename único."""

    def test_filename_contains_execution_id_prefix(self) -> None:
        filename = _build_report_filename("a" * 64, "2026-09-27T10-30-00Z")
        assert filename.startswith("regression_report_")
        assert "a" * 16 in filename
        assert filename.endswith(".json")

    def test_filename_contains_timestamp(self) -> None:
        filename = _build_report_filename("a" * 64, "2026-09-27T10-30-00Z")
        assert "2026-09-27T10-30-00Z" in filename

    def test_timestamp_shell_has_no_colons(self) -> None:
        """Cross-platform: Windows no permite ':' en filenames."""
        ts = _build_timestamp_shell()
        assert ":" not in ts

    def test_different_timestamps_produce_different_filenames(self) -> None:
        """R22: ejecuciones sucesivas son distinguibles."""
        f1 = _build_report_filename("a" * 64, "2026-09-27T10-30-00Z")
        f2 = _build_report_filename("a" * 64, "2026-09-27T10-31-00Z")
        assert f1 != f2


def _make_mock_artifacts() -> EvaluationArtifacts:
    """Helper: EvaluationArtifacts de prueba con RegressionReport mínimo."""
    report = RegressionReport(
        corpus_version="test-v1",
        corpus_verdict=RegressionVerdict.PASS,
        corpus_nss=0.98,
        total_documents=0,
        pass_count=0,
        warning_count=0,
        hard_fail_count=0,
        document_reports=(),
        total_critical_false_negatives=0,
        total_warning_false_negatives=0,
        total_info_false_negatives=0,
        generated_at=None,
        configuration_fingerprint="f" * 64,
    )
    return EvaluationArtifacts(
        regression_report=report,
        config_fingerprint="f" * 64,
        cost_weights=dict(DEFAULT_CRITICALITY_WEIGHTS),
    )


def _setup_corpus(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    """Helper: crea corpus mínimo y retorna (corpus_dir, pdf_dir, output_dir)."""
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    output_dir = tmp_path / "output"

    manifest_data = {
        "corpus_version": "test-v1",
        "manifest_hash": "a" * 64,
        "documents": [],
    }
    (corpus_dir / "manifest.json").write_text(
        json.dumps(manifest_data), encoding="utf-8"
    )
    (corpus_dir / "ground_truth").mkdir()
    return corpus_dir, pdf_dir, output_dir


def _setup_corpus_with_documents(
    tmp_path: pathlib.Path,
    doc_ids: list[str],
) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    """Helper: crea corpus con documentos (sin PDFs ni GTs reales).

    Requiere mockear verificaciones de materialización e integridad
    porque los archivos físicos no existen.
    """
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    output_dir = tmp_path / "output"

    documents = [
        {
            "document_id": doc_id,
            "sha256": "a" * 64,
            "traits": ["native_pdf"],
            "page_count": 3,
            "ground_truth_state": "sealed",
            "oracle_hash": "b" * 64,
        }
        for doc_id in doc_ids
    ]

    manifest_data = {
        "corpus_version": "test-v1",
        "manifest_hash": "a" * 64,
        "documents": documents,
    }
    (corpus_dir / "manifest.json").write_text(
        json.dumps(manifest_data), encoding="utf-8"
    )
    (corpus_dir / "ground_truth").mkdir()
    return corpus_dir, pdf_dir, output_dir


def _apply_common_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Helper: aplica mocks comunes para tests de persistencia."""
    monkeypatch.setattr(
        "tools.evaluation.run_regression.verify_baseline_materialized",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "tools.evaluation.run_regression.verify_baseline_physical_integrity",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "tools.evaluation.run_regression._run_evaluation",
        lambda *a, **k: _make_mock_artifacts(),
    )
    monkeypatch.setattr(
        "tools.evaluation.run_regression._get_subject_identity",
        lambda: "c" * 40,
    )


@pytest.mark.integration
class TestCvReportPersistence:
    """NADR-F17BIS-28 §5.4 R21, §5.5 R25: persistencia con filename único."""

    def test_report_written_with_unique_filename(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """R21: reporte se escribe con filename único, no fijo."""
        corpus_dir, pdf_dir, output_dir = _setup_corpus(tmp_path)

        _apply_common_mocks(monkeypatch)
        monkeypatch.setattr(
            sys, "argv",
            ["run_regression.py", "--corpus-dir", str(corpus_dir),
             "--pdf-dir", str(pdf_dir), "--output-dir", str(output_dir)],
        )

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

        json_files = list(output_dir.glob("regression_report_*.json"))
        assert len(json_files) == 1
        # R21: NO se escribe regression_report.json fijo
        assert not (output_dir / "regression_report.json").exists()

    def test_report_contains_identity_chain(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """R15: reporte JSON contiene identity chain completa (incluye profile_identity)."""
        corpus_dir, pdf_dir, output_dir = _setup_corpus(tmp_path)

        _apply_common_mocks(monkeypatch)
        monkeypatch.setattr(
            sys, "argv",
            ["run_regression.py", "--corpus-dir", str(corpus_dir),
             "--pdf-dir", str(pdf_dir), "--output-dir", str(output_dir)],
        )

        with pytest.raises(SystemExit):
            main()

        json_files = list(output_dir.glob("regression_report_*.json"))
        data = json.loads(json_files[0].read_text(encoding="utf-8"))

        assert "schema_version" in data
        assert "identity_chain" in data
        assert "operational_result" in data
        assert "regression_report" in data

        chain = data["identity_chain"]
        assert "execution_id" in chain
        assert "baseline_identity" in chain
        assert "subject_identity" in chain
        assert chain["subject_identity"] == "c" * 40
        assert "configuration_identity" in chain
        assert "parameter_identity" in chain
        assert "profile_identity" in chain  # NADR-29 §5.6 R28
        assert "result_identity" in chain

    def test_execution_id_is_reproducible(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """R25: dos ejecuciones con mismas entradas → mismo execution_id."""
        execution_ids = []
        for i in range(2):
            run_dir = tmp_path / f"run_{i}"
            run_dir.mkdir()
            corpus_dir, pdf_dir, output_dir = _setup_corpus(run_dir)

            _apply_common_mocks(monkeypatch)
            monkeypatch.setattr(
                sys, "argv",
                ["run_regression.py", "--corpus-dir", str(corpus_dir),
                 "--pdf-dir", str(pdf_dir), "--output-dir", str(output_dir)],
            )

            with pytest.raises(SystemExit):
                main()

            json_files = list(output_dir.glob("regression_report_*.json"))
            data = json.loads(json_files[0].read_text(encoding="utf-8"))
            execution_ids.append(data["identity_chain"]["execution_id"])

        # R25: mismo execution_id (aunque filenames difieran por timestamp)
        assert execution_ids[0] == execution_ids[1]


@pytest.mark.integration
class TestProfileInReport:
    """NADR-F17BIS-29 §5.1 R3, §5.2 R8-R13, §5.6 R28-R31."""

    def test_report_contains_profile_identity(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """R28: profile_identity está en la identity chain."""
        corpus_dir, pdf_dir, output_dir = _setup_corpus(tmp_path)

        _apply_common_mocks(monkeypatch)
        monkeypatch.setattr(
            sys, "argv",
            ["run_regression.py", "--corpus-dir", str(corpus_dir),
             "--pdf-dir", str(pdf_dir), "--output-dir", str(output_dir),
             "--profile", "FULL"],
        )

        with pytest.raises(SystemExit):
            main()

        json_files = list(output_dir.glob("regression_report_*.json"))
        data = json.loads(json_files[0].read_text(encoding="utf-8"))
        chain = data["identity_chain"]

        assert "profile_identity" in chain
        assert isinstance(chain["profile_identity"], str)
        assert len(chain["profile_identity"]) == 64

    def test_report_contains_coverage(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """R8-R13: coverage está en el JSON como lista."""
        corpus_dir, pdf_dir, output_dir = _setup_corpus(tmp_path)

        _apply_common_mocks(monkeypatch)
        monkeypatch.setattr(
            sys, "argv",
            ["run_regression.py", "--corpus-dir", str(corpus_dir),
             "--pdf-dir", str(pdf_dir), "--output-dir", str(output_dir)],
        )

        with pytest.raises(SystemExit):
            main()

        json_files = list(output_dir.glob("regression_report_*.json"))
        data = json.loads(json_files[0].read_text(encoding="utf-8"))

        assert "coverage" in data
        assert isinstance(data["coverage"], list)

    def test_different_profiles_produce_different_execution_id(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """NADR-29 §5.6 R31: perfiles diferentes → execution_ids diferentes."""
        execution_ids = {}

        for profile_name in ["FULL", "SMOKE"]:
            run_dir = tmp_path / f"profile_{profile_name}"
            run_dir.mkdir()
            corpus_dir, pdf_dir, output_dir = _setup_corpus(run_dir)

            _apply_common_mocks(monkeypatch)
            monkeypatch.setattr(
                sys, "argv",
                ["run_regression.py", "--corpus-dir", str(corpus_dir),
                 "--pdf-dir", str(pdf_dir), "--output-dir", str(output_dir),
                 "--profile", profile_name],
            )

            with pytest.raises(SystemExit):
                main()

            json_files = list(output_dir.glob("regression_report_*.json"))
            data = json.loads(json_files[0].read_text(encoding="utf-8"))
            execution_ids[profile_name] = data["identity_chain"]["execution_id"]

        # R31: perfiles diferentes producen execution_ids diferentes
        assert execution_ids["FULL"] != execution_ids["SMOKE"]

    def test_smoke_profile_with_documents_produces_correct_coverage(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """SMOKE con documentos produce coverage correcta (intersección)."""
        # Documentos que están en SMOKE_DOCUMENT_IDS
        doc_ids = ["doc_01_single", "doc_04_table", "doc_12_multi_col"]
        corpus_dir, pdf_dir, output_dir = _setup_corpus_with_documents(
            tmp_path, doc_ids
        )

        _apply_common_mocks(monkeypatch)
        # Mockear verificaciones de completitud que fallarían sin archivos reales
        monkeypatch.setattr(
            "core.benchmark.ground_truth.completeness.BaselineCompletenessVerifier.verify_pdf_ids",
            classmethod(lambda cls, **kwargs: []),
        )
        monkeypatch.setattr(
            "tools.evaluation.run_regression.verify_ground_truth_preconditions",
            lambda *a, **k: None,
        )
        monkeypatch.setattr(
            "infra.fs.ground_truth_store.LocalFileSystemGroundTruthArtifactAdapter.list_artifact_ids",
            lambda self: tuple(doc_ids),
        )
        monkeypatch.setattr(
            "tools.evaluation.run_regression.RegressionAdapter.verify_completeness",
            lambda self, *a, **k: None,
        )

        monkeypatch.setattr(
            sys, "argv",
            ["run_regression.py", "--corpus-dir", str(corpus_dir),
             "--pdf-dir", str(pdf_dir), "--output-dir", str(output_dir),
             "--profile", "SMOKE"],
        )

        with pytest.raises(SystemExit):
            main()

        json_files = list(output_dir.glob("regression_report_*.json"))
        data = json.loads(json_files[0].read_text(encoding="utf-8"))

        # SMOKE coverage debe contener los documentos que están en SMOKE_DOCUMENT_IDS
        coverage_set = set(data["coverage"])
        assert coverage_set == {"doc_01_single", "doc_04_table", "doc_12_multi_col"}

    def test_full_profile_with_documents_produces_full_coverage(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """FULL con documentos produce coverage completa."""
        doc_ids = ["doc_01_single", "doc_04_table", "doc_12_multi_col"]
        corpus_dir, pdf_dir, output_dir = _setup_corpus_with_documents(
            tmp_path, doc_ids
        )

        _apply_common_mocks(monkeypatch)
        monkeypatch.setattr(
            "core.benchmark.ground_truth.completeness.BaselineCompletenessVerifier.verify_pdf_ids",
            classmethod(lambda cls, **kwargs: []),
        )
        monkeypatch.setattr(
            "tools.evaluation.run_regression.verify_ground_truth_preconditions",
            lambda *a, **k: None,
        )
        monkeypatch.setattr(
            "infra.fs.ground_truth_store.LocalFileSystemGroundTruthArtifactAdapter.list_artifact_ids",
            lambda self: tuple(doc_ids),
        )
        monkeypatch.setattr(
            "tools.evaluation.run_regression.RegressionAdapter.verify_completeness",
            lambda self, *a, **k: None,
        )

        monkeypatch.setattr(
            sys, "argv",
            ["run_regression.py", "--corpus-dir", str(corpus_dir),
             "--pdf-dir", str(pdf_dir), "--output-dir", str(output_dir),
             "--profile", "FULL"],
        )

        with pytest.raises(SystemExit):
            main()

        json_files = list(output_dir.glob("regression_report_*.json"))
        data = json.loads(json_files[0].read_text(encoding="utf-8"))

        # FULL coverage debe contener todos los documentos del manifest
        coverage_set = set(data["coverage"])
        assert coverage_set == set(doc_ids)