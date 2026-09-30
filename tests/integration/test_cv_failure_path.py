"""Task 4.2.3 — Operational/integrity FAILURE path end-to-end (NADR-30 §5.3 R7-R10).

Cadena verificada: FAILURE (BASELINE_INTEGRITY_FAILURE) → EVIDENCE (CV report
con regression_report=None) → CI STATUS (exit 3 ⇒ check rojo).

Marker integration (NO e2e): el failure path aborta en la verificación de
materialización (NADR-26 §5.1 R2) ANTES de cualquier extracción, entonces es
rápido (~1-2 s) y debe quedar cubierto por la suite estándar sin costo de tiempo.

Relación con test_baseline_integrity_exit_code.py (Gate 1): aquel test verifica
exit 3 in-process mockeando _run_evaluation; este test verifica el proceso real
completo vía subprocess (lo que observa CI). No duplica lógica de construcción
de baseline corrupta: aquí el corpus mínimo es válido y lo que falta es el
directorio de PDFs, que es el escenario de materialización más simple y directo.
"""
from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from tests.helpers.cv_execution import load_cv_report, run_cv


def _setup_minimal_corpus(tmp_path: pathlib.Path) -> pathlib.Path:
    """Crea corpus mínimo válido (manifest con 0 documentos)."""
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "ground_truth").mkdir()
    manifest = {
        "corpus_version": "test-v1",
        "manifest_hash": "a" * 64,
        "documents": [],
    }
    (corpus_dir / "manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    return corpus_dir


@pytest.mark.integration
class TestFailurePathResult:
    def test_missing_pdf_dir_produces_exit_3(
        self, tmp_path: pathlib.Path
    ) -> None:
        """NADR-26 §5.6 R25: fallo de integridad/materialización ⇒ exit 3."""
        corpus_dir = _setup_minimal_corpus(tmp_path)
        pdf_dir = tmp_path / "pdfs_inexistentes"  # NO se crea a propósito
        output_dir = tmp_path / "out"

        proc = run_cv("FULL", corpus_dir, pdf_dir, output_dir)

        assert proc.returncode == 3, (
            f"Esperado exit 3 (BASELINE_INTEGRITY_FAILURE), obtenido "
            f"{proc.returncode}. stderr: {proc.stderr[-500:]}"
        )

    def test_failure_is_explicit_in_stderr(
        self, tmp_path: pathlib.Path
    ) -> None:
        """ENGINEERING_PRINCIPLES §IV: mensaje explícito, no fallo silencioso."""
        corpus_dir = _setup_minimal_corpus(tmp_path)
        pdf_dir = tmp_path / "pdfs_inexistentes"
        output_dir = tmp_path / "out"

        proc = run_cv("FULL", corpus_dir, pdf_dir, output_dir)

        assert "BASELINE_INTEGRITY_FAILURE" in proc.stderr
        assert "PDF directory not found" in proc.stderr


@pytest.mark.integration
class TestFailurePathEvidence:
    def test_evidence_persisted_without_regression_report(
        self, tmp_path: pathlib.Path
    ) -> None:
        """NADR-27 §5.2 R8 + NADR-28 §5.3 R14: fallo operacional persiste
        evidencia sin resultado científico (clave ausente, no null,
        coherente con test_json_excludes_regression_report_when_none)."""
        corpus_dir = _setup_minimal_corpus(tmp_path)
        pdf_dir = tmp_path / "pdfs_inexistentes"
        output_dir = tmp_path / "out"

        proc = run_cv("FULL", corpus_dir, pdf_dir, output_dir)
        assert proc.returncode == 3

        data = load_cv_report(output_dir)
        assert data["operational_result"]["outcome"] == "BASELINE_INTEGRITY_FAILURE"
        assert data["operational_result"]["scientific_verdict"] is None
        assert data["operational_result"]["exit_code"] == 3
        assert "regression_report" not in data

    def test_failure_aborts_before_any_extraction(
        self, tmp_path: pathlib.Path
    ) -> None:
        """NADR-26 §5.3 R14: precondiciones preceden a la evaluación.
        Sin regression_report ni Markdown científico: no hubo extracción."""
        corpus_dir = _setup_minimal_corpus(tmp_path)
        pdf_dir = tmp_path / "pdfs_inexistentes"
        output_dir = tmp_path / "out"

        proc = run_cv("FULL", corpus_dir, pdf_dir, output_dir)
        assert proc.returncode == 3

        assert not list(output_dir.glob("regression_report.md")), (
            "No debe existir Markdown científico en un fallo de baseline"
        )

@pytest.mark.integration
class TestCorruptManifestPath:
    """DF-11: manifest corrupto o con schema inválido ⇒ exit 3 con evidencia.

    NADR-27 §5.6 R34: ninguna excepción no controlada debe producir exit 1
    sin evidencia. json.JSONDecodeError y pydantic.ValidationError son
    subclasses de ValueError; el except de Pasos 1-2b las traduce a
    BASELINE_INTEGRITY_FAILURE (exit 3) con CV report persistido.
    """

    def _overwrite_manifest(self, corpus_dir: pathlib.Path, content: str) -> None:
        (corpus_dir / "manifest.json").write_text(content, encoding="utf-8")

    def _run_with_corrupt_manifest(
        self, tmp_path: pathlib.Path, content: str
    ) -> tuple[subprocess.CompletedProcess[str], pathlib.Path]:
        """Ejecuta CV con un manifest corrupto y retorna (proceso, output_dir)."""
        corpus_dir = _setup_minimal_corpus(tmp_path)
        self._overwrite_manifest(corpus_dir, content)
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()
        output_dir = tmp_path / "out"
        proc = run_cv("FULL", corpus_dir, pdf_dir, output_dir)
        return proc, output_dir

    def test_invalid_json_manifest_produces_exit_3_with_evidence(
        self, tmp_path: pathlib.Path
    ) -> None:
        """json.JSONDecodeError ⊂ ValueError ⇒ exit 3, no traceback."""
        proc, output_dir = self._run_with_corrupt_manifest(
            tmp_path, "{ esto no es json valido"
        )

        assert proc.returncode == 3, (
            f"Esperado exit 3 con manifest JSON inválido, obtenido "
            f"{proc.returncode}. stderr: {proc.stderr[-500:]}"
        )
        data = load_cv_report(output_dir)
        assert data["operational_result"]["outcome"] == "BASELINE_INTEGRITY_FAILURE"
        assert data["operational_result"]["scientific_verdict"] is None
        assert "regression_report" not in data

    def test_schema_invalid_manifest_produces_exit_3_with_evidence(
        self, tmp_path: pathlib.Path
    ) -> None:
        """pydantic.ValidationError ⊂ ValueError ⇒ exit 3, no traceback."""
        proc, output_dir = self._run_with_corrupt_manifest(
            tmp_path,
            json.dumps(
                {"corpus_version": "test-v1", "manifest_hash": "a" * 64}
            ),  # falta "documents" ⇒ ValidationError
        )

        assert proc.returncode == 3, (
            f"Esperado exit 3 con manifest schema inválido, obtenido "
            f"{proc.returncode}. stderr: {proc.stderr[-500:]}"
        )
        data = load_cv_report(output_dir)
        assert data["operational_result"]["outcome"] == "BASELINE_INTEGRITY_FAILURE"