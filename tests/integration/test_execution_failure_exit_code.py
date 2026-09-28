"""Tests de exit code para fallo de ejecución (NADR-F17BIS-27 §5.6 R34-R35).

Verifica que una excepción no controlada en Pasos 3-7 produce exit code 4
(EXECUTION_FAILURE), no exit code 1 (que colisionaría con WARNING).
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest


@pytest.mark.integration
class TestExecutionFailureExitCode:
    """NADR-F17BIS-27 §5.6 R34: excepción no controlada → EXECUTION_FAILURE."""

    def test_exit_code_4_on_execution_failure(
        self, tmp_path: pathlib.Path, monkeypatch
    ) -> None:
        """R34, R35: fallo de ejecución → exit code 4, no exit code 1."""
        from core.benchmark.verification.outcome import EXIT_EXECUTION_FAILURE
        from tools.evaluation.run_regression import main

        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir()
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()

        # Crear manifest.json válido para pasar Pasos 1-2b
        manifest_data = {
            "corpus_version": "test-v1",
            "manifest_hash": "a" * 64,
            "documents": [],
        }
        (corpus_dir / "manifest.json").write_text(
            json.dumps(manifest_data), encoding="utf-8"
        )
        (corpus_dir / "ground_truth").mkdir()

        # CORRECCIÓN: Mockear verify_baseline_physical_integrity para que
        # las precondiciones pasen. Sin este mock, el manifest_hash "a"*64
        # no coincidiría con el hash recalculado y se produciría exit 3,
        # no exit 4.
        monkeypatch.setattr(
            "tools.evaluation.run_regression.verify_baseline_physical_integrity",
            lambda *args, **kwargs: None,
        )

        # Mock _run_evaluation para lanzar una excepción no controlada
        def mock_run_evaluation(*args, **kwargs):
            raise RuntimeError("Simulated pipeline crash")

        monkeypatch.setattr(
            "tools.evaluation.run_regression._run_evaluation",
            mock_run_evaluation,
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

        # R34: exit code MUST ser 4 (EXECUTION_FAILURE), no 1 (WARNING)
        assert exc_info.value.code == EXIT_EXECUTION_FAILURE
        assert exc_info.value.code == 4

    def test_execution_failure_exit_code_does_not_collide_with_warning(self) -> None:
        """R30: exit code 4 es distinto de exit code 1 (WARNING)."""
        from core.benchmark.verification.outcome import (
            EXIT_EXECUTION_FAILURE,
            EXIT_WARNING,
        )
        assert EXIT_EXECUTION_FAILURE != EXIT_WARNING