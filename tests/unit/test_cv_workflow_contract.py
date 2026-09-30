"""Tests de contrato del workflow de Continuous Verification.

NADR-F17BIS-25 §5.2 R5-R7: Verifica que CI invoca el verification
entry point normativo.

NADR-F17BIS-29 §5.5 R24-R27: Verifica que los perfiles reutilizan
el mismo entry point.

NADR-F17BIS-29 §5.7 R32-R35: Verifica que la frecuencia está
gobernada por los triggers del workflow.

GAP-6.3-01 (P0): Resuelto. El job regression-gates invoca
run_regression.py, no pytest -m "regression".
"""
from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip(
    "yaml", reason="pyyaml requerido para tests de contrato de workflow"
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
CV_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "continuous-verification.yml"


def _load_yaml(path: Path) -> dict:
    """Carga un archivo YAML y retorna el dict parseado."""
    content = path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    assert isinstance(data, dict), f"{path} no es un YAML válido con mapping raíz"
    return data


def _get_on_config(data: dict) -> dict:
    """Extrae la configuración de triggers.

    PyYAML parsea 'on' como True (boolean) en YAML 1.1.
    Maneja ambos casos.
    """
    return data.get("on") or data.get(True) or {}


def _get_run_commands(job: dict) -> str:
    """Concatena todos los comandos 'run' de un job."""
    steps = job.get("steps", [])
    return "\n".join(step.get("run", "") for step in steps if "run" in step)


@pytest.mark.unit
class TestWorkflowFilesExist:
    """NADR-25 §5.2 R5: Los workflows existen en la ubicación canónica."""

    def test_ci_workflow_exists(self) -> None:
        assert CI_WORKFLOW.exists(), f"No existe {CI_WORKFLOW}"

    def test_cv_workflow_exists(self) -> None:
        assert CV_WORKFLOW.exists(), f"No existe {CV_WORKFLOW}"

    def test_ci_workflow_is_valid_yaml(self) -> None:
        data = _load_yaml(CI_WORKFLOW)
        assert "jobs" in data

    def test_cv_workflow_is_valid_yaml(self) -> None:
        data = _load_yaml(CV_WORKFLOW)
        assert "jobs" in data


@pytest.mark.unit
class TestRegressionGatesJobContract:
    """GAP-6.3-01 (P0): El job regression-gates invoca el entry point real."""

    def test_regression_gates_job_exists(self) -> None:
        data = _load_yaml(CI_WORKFLOW)
        assert "regression-gates" in data["jobs"]

    def test_regression_gates_invokes_run_regression(self) -> None:
        """El job invoca run_regression.py (no pytest -m regression)."""
        data = _load_yaml(CI_WORKFLOW)
        commands = _get_run_commands(data["jobs"]["regression-gates"])
        assert "run_regression" in commands

    def test_regression_gates_uses_smoke_profile(self) -> None:
        """El job usa --profile SMOKE para feedback rápido en PRs."""
        data = _load_yaml(CI_WORKFLOW)
        commands = _get_run_commands(data["jobs"]["regression-gates"])
        assert "--profile SMOKE" in commands

    def test_regression_gates_does_not_use_pytest_regression_marker(self) -> None:
        """GAP-6.3-01: El job NO ejecuta pytest -m 'regression' (0 tests)."""
        data = _load_yaml(CI_WORKFLOW)
        commands = _get_run_commands(data["jobs"]["regression-gates"])
        assert 'pytest -m "regression"' not in commands
        assert "pytest -m regression" not in commands

    def test_regression_gates_uses_persist_credentials_false(self) -> None:
        """NADR-26 §5.4 R16: El corpus es read-only durante la evaluación."""
        data = _load_yaml(CI_WORKFLOW)
        steps = data["jobs"]["regression-gates"]["steps"]
        checkout_steps = [
            s for s in steps if s.get("uses", "").startswith("actions/checkout")
        ]
        assert len(checkout_steps) > 0
        for step in checkout_steps:
            assert step.get("with", {}).get("persist-credentials") is False

    def test_regression_gates_verifies_corpus_mutation(self) -> None:
        """NADR-26 §5.4 R16-R19: Verificación de mutación del corpus."""
        data = _load_yaml(CI_WORKFLOW)
        commands = _get_run_commands(data["jobs"]["regression-gates"])
        assert "tests/corpus/canonical/" in commands

    def test_regression_gates_verifies_oracle_mutation(self) -> None:
        """NADR-10 §5.1 R2: Verificación de mutación de oráculos (existente)."""
        data = _load_yaml(CI_WORKFLOW)
        commands = _get_run_commands(data["jobs"]["regression-gates"])
        assert "tests/fixtures/" in commands

    def test_regression_gates_uploads_artifacts_with_always(self) -> None:
        """NADR-28 §5.3 R14: Evidencia persistente con if: always()."""
        data = _load_yaml(CI_WORKFLOW)
        steps = data["jobs"]["regression-gates"]["steps"]
        upload_steps = [
            s for s in steps if s.get("uses", "").startswith("actions/upload-artifact")
        ]
        assert len(upload_steps) > 0
        for step in upload_steps:
            assert step.get("if") == "always()"


@pytest.mark.unit
class TestCvFullProfileWorkflowContract:
    """NADR-29 §5.1 R1-R7, §5.7 R32-R35: Workflow de FULL profile."""

    def test_cv_workflow_has_full_profile_job(self) -> None:
        data = _load_yaml(CV_WORKFLOW)
        assert "cv-full-profile" in data["jobs"]

    def test_cv_workflow_invokes_run_regression_full(self) -> None:
        data = _load_yaml(CV_WORKFLOW)
        commands = _get_run_commands(data["jobs"]["cv-full-profile"])
        assert "run_regression" in commands
        assert "--profile FULL" in commands

    def test_cv_workflow_triggers_on_main_push(self) -> None:
        """NADR-29 §5.7 R32-R35: FULL en push a main."""
        data = _load_yaml(CV_WORKFLOW)
        on_config = _get_on_config(data)
        assert "push" in on_config
        assert "main" in on_config["push"]["branches"]

    def test_cv_workflow_has_workflow_dispatch(self) -> None:
        """NADR-29 §5.7 R33: Ejecución manual gobernada."""
        data = _load_yaml(CV_WORKFLOW)
        on_config = _get_on_config(data)
        assert "workflow_dispatch" in on_config

    def test_cv_workflow_not_triggered_on_pull_request(self) -> None:
        """SMOKE cubre PRs; FULL solo en main (evita ~4 min por PR)."""
        data = _load_yaml(CV_WORKFLOW)
        on_config = _get_on_config(data)
        assert "pull_request" not in on_config

    def test_cv_workflow_uses_persist_credentials_false(self) -> None:
        data = _load_yaml(CV_WORKFLOW)
        steps = data["jobs"]["cv-full-profile"]["steps"]
        checkout_steps = [
            s for s in steps if s.get("uses", "").startswith("actions/checkout")
        ]
        assert len(checkout_steps) > 0
        for step in checkout_steps:
            assert step.get("with", {}).get("persist-credentials") is False

    def test_cv_workflow_verifies_corpus_mutation(self) -> None:
        data = _load_yaml(CV_WORKFLOW)
        commands = _get_run_commands(data["jobs"]["cv-full-profile"])
        assert "tests/corpus/canonical/" in commands

    def test_cv_workflow_uploads_artifacts_with_always(self) -> None:
        data = _load_yaml(CV_WORKFLOW)
        steps = data["jobs"]["cv-full-profile"]["steps"]
        upload_steps = [
            s for s in steps if s.get("uses", "").startswith("actions/upload-artifact")
        ]
        assert len(upload_steps) > 0
        for step in upload_steps:
            assert step.get("if") == "always()"

    def test_cv_workflow_has_concurrency_control(self) -> None:
        """Evita ejecuciones redundantes en el mismo ref."""
        data = _load_yaml(CV_WORKFLOW)
        assert "concurrency" in data


@pytest.mark.unit
class TestProfileSeparation:
    """NADR-29 §5.2 R8-R13: Coberturas distinguibles entre perfiles."""

    def test_full_and_smoke_have_different_output_dirs(self) -> None:
        """R11: Diferencia de cobertura observable en evidencia."""
        ci_data = _load_yaml(CI_WORKFLOW)
        cv_data = _load_yaml(CV_WORKFLOW)

        smoke_commands = _get_run_commands(ci_data["jobs"]["regression-gates"])
        full_commands = _get_run_commands(cv_data["jobs"]["cv-full-profile"])

        assert "reports/continuous-verification-smoke" in smoke_commands
        assert "reports/continuous-verification" in full_commands
        assert "reports/continuous-verification-smoke" not in full_commands