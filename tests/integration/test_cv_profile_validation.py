"""Validación end-to-end de perfiles de Continuous Verification (Wave 3.3).

NADR-F17BIS-29 §5.3 R14-R17: Perfil completo evalúa todo el corpus.
NADR-F17BIS-29 §5.4 R18-R23: Perfil reducido con cobertura explícita.
NADR-F17BIS-29 §5.6 R28-R31: Perfiles distinguibles en evidencia.
NADR-F17BIS-28 §5.2 R8: Determinismo de identidad.

DISTINCIÓN CRÍTICA (Verification vs Validation):
- Wave 3.2 hizo VERIFICATION (estructura de workflows, contratos).
- Wave 3.3 hace VALIDATION (comportamiento end-to-end real).

Estos tests ejecutan el pipeline REAL contra el corpus canónico.
Son lentos (~4 min FULL, ~1 min SMOKE) y se ejecutan bajo demanda:

    python -m pytest tests/integration/test_cv_profile_validation.py -m e2e -v

Resultado esperado: El corpus actual produce divergencias topológicas reales
(NSS ~0.72 < threshold 0.80), así que el veredicto científico esperado es
HARD_FAIL. Sin embargo, los tests NO asumen HARD_FAIL específicamente:
verifican que el veredicto es CIENTÍFICO (PASS/WARNING/HARD_FAIL), no
operacional (BASELINE_INTEGRITY_FAILURE/EXECUTION_FAILURE). Esto es robusto
ante futura mejora de la baseline (Fase 18).
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

from core.benchmark.verification.outcome import (
    EXIT_BASELINE_INTEGRITY_FAILURE,
    EXIT_EXECUTION_FAILURE,
    EXIT_HARD_FAIL,
    EXIT_PASS,
    EXIT_WARNING,
)
from tools.evaluation.run_regression import main

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS_DIR = REPO_ROOT / "tests" / "corpus" / "canonical"
PDF_DIR = CORPUS_DIR / "pdf"

EXIT_CODES_SCIENTIFIC = {EXIT_PASS, EXIT_WARNING, EXIT_HARD_FAIL}
EXIT_CODES_OPERATIONAL = {EXIT_BASELINE_INTEGRITY_FAILURE, EXIT_EXECUTION_FAILURE}

EXPECTED_FULL_COVERAGE_SIZE = 21  # 22 PDFs - doc_06_johnstone (sin GT sellado)
EXPECTED_SMOKE_COVERAGE_SIZE = 5
EXPECTED_SMOKE_DOCUMENT_IDS = frozenset({
    "doc_01_single",
    "doc_04_table",
    "doc_12_multi_col",
    "doc_18_table_math_doble_col",
    "doc_22_table_fig_math",
})


def _run_profile(
    profile: str,
    output_dir: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[int, dict]:
    """Ejecuta run_regression.py con un perfil dado y retorna (exit_code, json_data).

    Helper que orquesta la ejecución real del pipeline contra el corpus
    canónico. No mockea el pipeline: validación end-to-end real.

    Args:
        profile: "FULL" o "SMOKE".
        output_dir: Directorio temporal para reportes.
        monkeypatch: Fixture de pytest para mockear sys.argv.

    Returns:
        Tupla (exit_code, json_data del reporte persistido).
    """
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_regression.py",
            "--corpus-dir", str(CORPUS_DIR),
            "--pdf-dir", str(PDF_DIR),
            "--output-dir", str(output_dir),
            "--profile", profile,
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()
    exit_code = exc_info.value.code
    assert isinstance(exit_code, int), f"Exit code no es int: {type(exit_code)}"

    # Leer el JSON persistido (filename único)
    json_files = list(output_dir.glob("regression_report_*.json"))
    assert len(json_files) == 1, (
        f"Esperado exactamente 1 JSON, encontrados {len(json_files)}: "
        f"{[f.name for f in json_files]}"
    )
    data = json.loads(json_files[0].read_text(encoding="utf-8"))

    return exit_code, data


def _assert_scientific_verdict(exit_code: int, profile: str) -> None:
    """Asserta que el exit code es un veredicto científico, no operacional.

    Si el pipeline produce BASELINE_INTEGRITY_FAILURE o EXECUTION_FAILURE,
    esto indica un problema en el pipeline (ej. PyMuPDF no instalado, PDF
    corrupto, baseline alterada), NO en la validación de perfiles. El test
    debe fallar con un mensaje claro que distinga ambas situaciones.
    """
    assert exit_code not in EXIT_CODES_OPERATIONAL, (
        f"Pipeline produjo fallo operacional (exit {exit_code}) con perfil "
        f"{profile}, no veredicto científico. Esto indica un problema en el "
        f"pipeline o la baseline, no en la validación de perfiles. "
        f"Verificar: PyMuPDF instalado, corpus canónico intacto, baseline sellada."
    )
    assert exit_code in EXIT_CODES_SCIENTIFIC, (
        f"Exit code inesperado {exit_code} con perfil {profile}. "
        f"Esperado uno de {sorted(EXIT_CODES_SCIENTIFIC)}."
    )


@pytest.mark.e2e
class TestFullProfileValidation:
    """Task 3.3.1: Validar Full Profile end-to-end contra corpus canónico."""

    def test_full_profile_produces_scientific_verdict(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-29 §5.3 R14-R17: FULL evalúa todo el corpus y produce
        veredicto científico válido."""
        exit_code, data = _run_profile("FULL", tmp_path, monkeypatch)

        _assert_scientific_verdict(exit_code, "FULL")

        # Veredicto científico presente en operational_result
        assert "operational_result" in data
        assert data["operational_result"]["scientific_verdict"] is not None

    def test_full_profile_coverage_is_21_documents(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-29 §5.3 R14: FULL evalúa los 21 documentos del manifest
        (excluye doc_06_johnstone que no tiene GT sellado)."""
        exit_code, data = _run_profile("FULL", tmp_path, monkeypatch)

        _assert_scientific_verdict(exit_code, "FULL")

        assert "coverage" in data
        coverage = data["coverage"]
        assert len(coverage) == EXPECTED_FULL_COVERAGE_SIZE, (
            f"FULL coverage esperado {EXPECTED_FULL_COVERAGE_SIZE}, "
            f"obtenido {len(coverage)}"
        )

    def test_full_profile_identity_chain_complete(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-28 §5.3 R15: identity chain completa en la evidencia."""
        exit_code, data = _run_profile("FULL", tmp_path, monkeypatch)

        _assert_scientific_verdict(exit_code, "FULL")

        chain = data["identity_chain"]
        assert "execution_id" in chain
        assert "baseline_identity" in chain
        assert "subject_identity" in chain
        assert "configuration_identity" in chain
        assert "parameter_identity" in chain
        assert "profile_identity" in chain
        assert "result_identity" in chain

        # baseline_identity debe ser el manifest_hash real (no UNAVAILABLE)
        assert chain["baseline_identity"] != "UNAVAILABLE", (
            "baseline_identity es UNAVAILABLE: manifest no pudo cargarse"
        )

    def test_full_profile_regression_report_present(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-28 §5.3 R16: regression_report presente cuando hay
        evaluación científica."""
        exit_code, data = _run_profile("FULL", tmp_path, monkeypatch)

        _assert_scientific_verdict(exit_code, "FULL")

        assert "regression_report" in data
        assert data["regression_report"] is not None
        assert data["regression_report"]["corpus_nss"] is not None


@pytest.mark.e2e
class TestSmokeProfileValidation:
    """Task 3.3.2: Validar Smoke Profile y cobertura distinguible."""

    def test_smoke_profile_produces_scientific_verdict(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-29 §5.4 R18-R23: SMOKE produce veredicto científico válido."""
        exit_code, data = _run_profile("SMOKE", tmp_path, monkeypatch)

        _assert_scientific_verdict(exit_code, "SMOKE")

        assert "operational_result" in data
        assert data["operational_result"]["scientific_verdict"] is not None

    def test_smoke_profile_coverage_is_5_documents(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-29 §5.4 R19: SMOKE evalúa exactamente 5 documentos
        representativos."""
        exit_code, data = _run_profile("SMOKE", tmp_path, monkeypatch)

        _assert_scientific_verdict(exit_code, "SMOKE")

        assert "coverage" in data
        coverage = set(data["coverage"])
        assert len(coverage) == EXPECTED_SMOKE_COVERAGE_SIZE, (
            f"SMOKE coverage esperado {EXPECTED_SMOKE_COVERAGE_SIZE}, "
            f"obtenido {len(coverage)}"
        )
        assert coverage == EXPECTED_SMOKE_DOCUMENT_IDS, (
            f"SMOKE coverage inesperado: {sorted(coverage)}"
        )

    def test_smoke_coverage_is_subset_of_full(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-29 §5.2 R10-R11: SMOKE es subconjunto estricto de FULL."""
        # Ejecutar FULL
        full_output = tmp_path / "full"
        full_output.mkdir()
        _, full_data = _run_profile("FULL", full_output, monkeypatch)

        # Ejecutar SMOKE
        smoke_output = tmp_path / "smoke"
        smoke_output.mkdir()
        _, smoke_data = _run_profile("SMOKE", smoke_output, monkeypatch)

        full_coverage = set(full_data["coverage"])
        smoke_coverage = set(smoke_data["coverage"])

        assert smoke_coverage < full_coverage, (
            "SMOKE no es subconjunto estricto de FULL. "
            f"SMOKE: {sorted(smoke_coverage)}, FULL: {sorted(full_coverage)}"
        )

    def test_smoke_pass_does_not_imply_full_verification(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-29 §5.4 R22: PASS de SMOKE no implica verificación completa.

        Este test verifica que la evidencia de SMOKE declara explícitamente
        su cobertura limitada, de modo que un consumidor de la evidencia
        puede distinguir SMOKE de FULL independientemente del veredicto.
        """
        exit_code, data = _run_profile("SMOKE", tmp_path, monkeypatch)

        _assert_scientific_verdict(exit_code, "SMOKE")

        # La cobertura en la evidencia debe distinguir SMOKE de FULL:
        # un consumidor puede verificar que SMOKE evaluó menos documentos
        # que el corpus completo, independientemente del veredicto científico.
        smoke_coverage = set(data["coverage"])
        assert len(smoke_coverage) < EXPECTED_FULL_COVERAGE_SIZE, (
            f"SMOKE evaluó {len(smoke_coverage)} documentos, igual o más que "
            f"el corpus completo ({EXPECTED_FULL_COVERAGE_SIZE}). Un consumidor "
            f"de la evidencia no podría determinar que SMOKE no verificó "
            f"todo el corpus."
        )

        # La identidad del perfil también distingue SMOKE de FULL
        # (ya verificado en test_profile_identity_differs_between_profiles)
        assert data["identity_chain"]["profile_identity"] is not None


@pytest.mark.e2e
class TestProfileIdentityValidation:
    """Task 3.3.3: Validar identidad por perfil y determinismo."""

    def test_execution_id_differs_between_profiles(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-29 §5.6 R31: Ejecuciones bajo perfiles diferentes producen
        execution_ids distinguibles."""
        full_output = tmp_path / "full"
        full_output.mkdir()
        _, full_data = _run_profile("FULL", full_output, monkeypatch)

        smoke_output = tmp_path / "smoke"
        smoke_output.mkdir()
        _, smoke_data = _run_profile("SMOKE", smoke_output, monkeypatch)

        full_exec_id = full_data["identity_chain"]["execution_id"]
        smoke_exec_id = smoke_data["identity_chain"]["execution_id"]

        assert full_exec_id != smoke_exec_id, (
            "FULL y SMOKE produjeron el mismo execution_id, violando "
            "NADR-29 §5.6 R31"
        )

    def test_profile_identity_differs_between_profiles(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-29 §5.6 R28-R29: profile_identity distingue perfiles."""
        full_output = tmp_path / "full"
        full_output.mkdir()
        _, full_data = _run_profile("FULL", full_output, monkeypatch)

        smoke_output = tmp_path / "smoke"
        smoke_output.mkdir()
        _, smoke_data = _run_profile("SMOKE", smoke_output, monkeypatch)

        full_profile_id = full_data["identity_chain"]["profile_identity"]
        smoke_profile_id = smoke_data["identity_chain"]["profile_identity"]

        assert full_profile_id != smoke_profile_id, (
            "FULL y SMOKE produjeron el mismo profile_identity, violando "
            "NADR-29 §5.6 R28"
        )

    def test_execution_id_is_deterministic(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-28 §5.2 R8: Ejecuciones equivalentes producen execution_id
        idéntico. Ejecutar SMOKE dos veces y verificar mismo execution_id.

        Nota: Se usa SMOKE en lugar de FULL para reducir tiempo de ejecución.
        El determinismo es una propiedad del mecanismo, no del perfil específico.
        """
        run1_output = tmp_path / "run1"
        run1_output.mkdir()
        _, run1_data = _run_profile("SMOKE", run1_output, monkeypatch)

        run2_output = tmp_path / "run2"
        run2_output.mkdir()
        _, run2_data = _run_profile("SMOKE", run2_output, monkeypatch)

        run1_exec_id = run1_data["identity_chain"]["execution_id"]
        run2_exec_id = run2_data["identity_chain"]["execution_id"]

        assert run1_exec_id == run2_exec_id, (
            "SMOKE produjo execution_ids diferentes en dos ejecuciones "
            "equivalentes, violando NADR-28 §5.2 R8. "
            f"run1: {run1_exec_id}, run2: {run2_exec_id}"
        )

    def test_profile_identity_is_deterministic(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-28 §5.2 R8: profile_identity determinista entre ejecuciones."""
        run1_output = tmp_path / "run1"
        run1_output.mkdir()
        _, run1_data = _run_profile("SMOKE", run1_output, monkeypatch)

        run2_output = tmp_path / "run2"
        run2_output.mkdir()
        _, run2_data = _run_profile("SMOKE", run2_output, monkeypatch)

        run1_profile_id = run1_data["identity_chain"]["profile_identity"]
        run2_profile_id = run2_data["identity_chain"]["profile_identity"]

        assert run1_profile_id == run2_profile_id, (
            "profile_identity difiere entre ejecuciones equivalentes"
        )

    def test_exit_code_matches_scientific_verdict(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """NADR-27 §5.6 R29-R35: exit code propaga según veredicto científico."""
        exit_code, data = _run_profile("SMOKE", tmp_path, monkeypatch)

        _assert_scientific_verdict(exit_code, "SMOKE")

        scientific_verdict = data["operational_result"]["scientific_verdict"]
        reported_exit_code = data["operational_result"]["exit_code"]

        # El exit code reportado en la evidencia debe coincidir con el exit code real
        assert reported_exit_code == exit_code, (
            f"exit_code en evidencia ({reported_exit_code}) difiere del exit "
            f"code real ({exit_code})"
        )

        # El exit code debe ser consistente con el veredicto científico
        verdict_to_exit = {"PASS": 0, "WARNING": 1, "HARD_FAIL": 2}
        if scientific_verdict in verdict_to_exit:
            assert exit_code == verdict_to_exit[scientific_verdict], (
                f"exit_code {exit_code} inconsistente con veredicto "
                f"{scientific_verdict}"
            )