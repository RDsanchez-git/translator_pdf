"""Task 4.2.2 — REGRESSION path end-to-end (NADR-30 §5.3 R7-R10).

Cadena verificada: RESULT (REGRESSION) → EVIDENCE (CV report persistido)
→ CI STATUS (exit code ≠ 0 ⇒ check rojo ⇒ integración bloqueada cuando
el check sea required, cláusula 6.1 del ENFORCEMENT_CONTRACT).

Marker e2e: ejecuta extracción real contra el corpus canónico. El estado
basal del extractor produce HARD_FAIL (NSS 0.7208 < 0.80), que es
exactamente el escenario REGRESSION que este test valida. No se fabrica
un PASS (NADR-26 §5.5 R20-R22).

Fixture module-scoped: una sola ejecución real compartida por todos los
tests del módulo para no multiplicar el costo (~5-8 s por run SMOKE).
"""
from __future__ import annotations

import pathlib

import pytest

import subprocess 

from tests.helpers.cv_execution import CORPUS_DIR, PDF_DIR, load_cv_report, run_cv

EXPECTED_SMOKE_COVERAGE = {
    "doc_01_single",
    "doc_04_table",
    "doc_12_multi_col",
    "doc_18_table_math_doble_col",
    "doc_22_table_fig_math",
}


@pytest.fixture(scope="module")
def smoke_run(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[subprocess.CompletedProcess[str], pathlib.Path]:
    """Ejecuta SMOKE una vez contra el corpus canónico real."""
    output_dir = tmp_path_factory.mktemp("cv-regression-path")
    proc = run_cv("SMOKE", CORPUS_DIR, PDF_DIR, output_dir)
    return proc, output_dir


@pytest.mark.e2e
class TestRegressionPathResult:
    def test_exit_code_is_hard_fail(self, smoke_run) -> None:
        """NADR-27 §5.6 R29-R33: exit 2 propaga sin reinterpretar."""
        proc, _ = smoke_run
        assert proc.returncode == 2, (
            f"Esperado exit 2 (HARD_FAIL basal), obtenido {proc.returncode}. "
            f"stderr: {proc.stderr[-500:]}"
        )

    def test_exit_code_nonzero_so_ci_check_is_red(self, smoke_run) -> None:
        """NADR-30 §5.3 R7-R10: exit ≠ 0 ⇒ check rojo ⇒ bloquea al ser required."""
        proc, _ = smoke_run
        assert proc.returncode != 0

    def test_stderr_is_explicit(self, smoke_run) -> None:
        """ENGINEERING_PRINCIPLES §IV: cero fallos silenciosos."""
        proc, _ = smoke_run
        assert "REGRESSION" in proc.stderr


@pytest.mark.e2e
class TestRegressionPathEvidence:
    def test_evidence_persisted_with_regression_outcome(self, smoke_run) -> None:
        """NADR-28 §5.3 R14-R17: evidencia completa del resultado bloqueante."""
        _, output_dir = smoke_run
        data = load_cv_report(output_dir)
        operational = data["operational_result"]
        assert operational["outcome"] == "REGRESSION"
        assert operational["scientific_verdict"] == "HARD_FAIL"
        assert operational["exit_code"] == 2

    def test_evidence_contains_coverage_and_identity(self, smoke_run) -> None:
        """NADR-29 §5.6 R28-R31: identidad y cobertura trazables en evidencia."""
        _, output_dir = smoke_run
        data = load_cv_report(output_dir)
        assert set(data["coverage"]) == EXPECTED_SMOKE_COVERAGE
        chain = data["identity_chain"]
        assert chain["profile_identity"]
        assert chain["execution_id"]
        assert chain["result_identity"]

    def test_regression_report_present_in_evidence(self, smoke_run) -> None:
        """REGRESSION lleva resultado científico (NADR-27 §5.2 R8-R9)."""
        _, output_dir = smoke_run
        data = load_cv_report(output_dir)
        assert data["regression_report"] is not None
        assert data["regression_report"]["corpus_verdict"] == "HARD_FAIL"