"""Tests de persistencia de ContinuousVerificationReport (NADR-F17BIS-28 §5.4, §5.5).

Verifica filename único, reproducibilidad de execution_id, y que el
reporte JSON contiene la identity chain completa.
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


@pytest.mark.integration
class TestCvReportPersistence:
    """NADR-F17BIS-28 §5.4 R21, §5.5 R25: persistencia con filename único."""

    def test_report_written_with_unique_filename(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """R21: reporte se escribe con filename único, no fijo."""
        corpus_dir, pdf_dir, output_dir = _setup_corpus(tmp_path)

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
        """R15: reporte JSON contiene identity chain completa."""
        corpus_dir, pdf_dir, output_dir = _setup_corpus(tmp_path)

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