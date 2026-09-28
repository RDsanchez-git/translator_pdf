"""Tests de exit code para fallo de integridad de la baseline.

NADR-F17BIS-26 §5.6 R25: Fallo de integridad → exit code 3,
distinto de los resultados de evaluación (0, 1, 2).

Tests de integración que verifican el exit code del entry point
cuando la baseline tiene un fallo de integridad.
"""
from __future__ import annotations

import pathlib
import sys
import json
import pytest

from core.benchmark.corpus.integrity import ManifestHashMismatchError



@pytest.mark.integration
class TestBaselineIntegrityExitCode:
    """NADR-F17BIS-26 §5.6 R25: Exit code 3 para fallo de integridad."""

    def test_exit_code_3_on_baseline_integrity_failure(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """R25: ManifestHashMismatchError → exit code 3.

        Crea un manifest.json válido para que load_raw_manifest() no falle
        y el código llegue a verify_baseline_physical_integrity (mocked).
        Sin manifest.json, el test pasaría por FileNotFoundError, no por
        ManifestHashMismatchError.
        """
        from core.benchmark.verification.outcome import EXIT_BASELINE_INTEGRITY_FAILURE
        from tools.evaluation.run_regression import main

        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir()
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()

        # manifest.json válido para que load_raw_manifest() no falle.
        # documents=[] → verify_baseline_materialized pasa (loop vacío).
        manifest_data = {
            "corpus_version": "test-v1",
            "manifest_hash": "a" * 64,
            "documents": [],
        }
        (corpus_dir / "manifest.json").write_text(
            json.dumps(manifest_data), encoding="utf-8"
        )

        def mock_verify(*args, **kwargs):
            raise ManifestHashMismatchError(expected="a" * 64, actual="b" * 64)

        monkeypatch.setattr(
            "tools.evaluation.run_regression.verify_baseline_physical_integrity",
            mock_verify,
        )

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "run_regression.py",
                "--corpus-dir", str(corpus_dir),
                "--pdf-dir", str(pdf_dir),
            ],
        )

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == EXIT_BASELINE_INTEGRITY_FAILURE
        assert exc_info.value.code == 3