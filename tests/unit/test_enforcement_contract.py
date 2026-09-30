"""Tests de contrato del ENFORCEMENT_CONTRACT.md (Task 4.1.2).

NADR-F17BIS-30 §5.1 R1-R3, §5.2 R4-R6, §5.4 R11-R13: el enforcement
contract debe declarar explícitamente qué checks bloquean integración.

Verifica las cuatro declaraciones duras del contrato:
1. `static-analysis` es el ÚNICO check REQUIRED.
2. `regression-gates` y `cv-full-profile` son informativos.
3. Cláusula 6.1 declara el comportamiento de WARNING al promocionar
   y prohíbe el wrapper por NADR-F17BIS-27 §5.6 R32.
4. Tabla de alternativas rechazadas presente (A, C, D, Ruleset).

Consistente con test_cv_workflow_contract.py: marker unit, lectura de
artefacto del repositorio sin ejecución de pipeline.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    REPO_ROOT
    / "docs"
    / "architecture"
    / "adr"
    / "phase-17-bis"
    / "plans"
    / "FASE_6_ENFORCEMENT_CONTRACT.md"
)


def _read_contract() -> str:
    assert CONTRACT_PATH.exists(), (
        f"ENFORCEMENT_CONTRACT.md no existe en {CONTRACT_PATH}. "
        f"Task 4.1.1 pendiente o ubicación incorrecta (debe vivir en plans/ "
        f"según Guía de Documentación de Arquitectura §4)."
    )
    return CONTRACT_PATH.read_text(encoding="utf-8")


def _parse_checks_table(text: str) -> dict[str, str]:
    """Parsea la tabla de §3 y mapea check -> estado declarado."""
    lines = text.splitlines()
    start = next(
        i for i, line in enumerate(lines) if line.strip().startswith("| Check |")
    )
    checks: dict[str, str] = {}
    for line in lines[start + 2 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        name = cells[0].strip("`")
        state = cells[3].replace("*", "")
        checks[name] = state
    return checks


@pytest.mark.unit
class TestContractExistsAndLocation:
    def test_contract_exists_in_plans(self) -> None:
        """El contrato vive en plans/ (Guía §4), no en reviews/ ni reports/."""
        assert CONTRACT_PATH.exists()
        assert CONTRACT_PATH.parent.name == "plans"

    def test_contract_references_nadr30_and_execution_plan(self) -> None:
        """Trazabilidad: deriva de NADR-30 y del Execution Plan v1.0.10."""
        text = _read_contract()
        assert "NADR-F17BIS-30" in text
        assert "PHASE_17BIS_FASE6_EXECUTION_PLAN.md v1.0.10" in text


@pytest.mark.unit
class TestRequiredChecksDeclaration:
    def test_static_analysis_is_required(self) -> None:
        checks = _parse_checks_table(_read_contract())
        assert checks.get("static-analysis") == "REQUIRED"

    def test_static_analysis_is_the_only_required_check(self) -> None:
        """Declaración dura 1: único REQUIRED."""
        checks = _parse_checks_table(_read_contract())
        required = [name for name, state in checks.items() if state == "REQUIRED"]
        assert required == ["static-analysis"], (
            f"Esperado exactamente 1 check REQUIRED (static-analysis), "
            f"obtenido: {required}"
        )

    def test_cv_checks_are_informational(self) -> None:
        """Declaración dura 2: ambos checks CV informativos."""
        checks = _parse_checks_table(_read_contract())
        assert checks.get("regression-gates") == "informativo"
        assert checks.get("cv-full-profile") == "informativo"

    def test_enforcement_scope_is_documented(self) -> None:
        """El contrato declara qué bloquea entrada y qué queda diferido."""
        text = _read_contract()
        # Con required checks activos, commits sin checks pasados son rechazados
        assert "push directo de un" in text
        assert "commit sin checks pasados es rechazado" in text
        # Lo que queda diferido es enforcement de CV (checks CV informativos)
        assert "regression-gates" in text
        assert "cv-full-profile" in text
        assert "aún no son" in text or "aun no son" in text.lower()


@pytest.mark.unit
class TestActivationClause:
    def test_activation_requires_basal_pass_or_governed_recalibration(self) -> None:
        text = _read_contract()
        assert "estado basal del corpus canónico sea PASS (exit 0)" in text
        assert "recalibración gobernada de thresholds" in text

    def test_warning_blocks_after_promotion_is_declared(self) -> None:
        """Declaración dura 3: WARNING (exit 1) bloqueará al promocionar."""
        text = _read_contract()
        assert "WARNING (exit 1) también bloqueará" in text

    def test_exit_code_wrapper_is_prohibited(self) -> None:
        """El wrapper WARNING→0 está prohibido por NADR-27 §5.6 R32."""
        text = _read_contract()
        assert "prohibido" in text
        assert "NADR-F17BIS-27 §5.6 R32" in text


@pytest.mark.unit
class TestRejectedAlternatives:
    def test_rejected_alternatives_table_present(self) -> None:
        """Declaración dura 4: alternativas A, C, D y Ruleset documentadas."""
        text = _read_contract()
        assert "## 7. Alternativas rechazadas" in text
        for marker in ("**A:**", "**C:**", "**D:**", "**Ruleset**"):
            assert marker in text, f"Alternativa rechazada faltante: {marker}"

    def test_relative_gate_rejected_for_normative_hierarchy(self) -> None:
        """El gate relativo se rechaza por jerarquía normativa, no por gusto."""
        text = _read_contract()
        assert "gate relativo" in text
        assert "jerarquía normativa" in text


@pytest.mark.unit
class TestEvidencePath:
    def test_evidence_path_is_reports_not_reviews(self) -> None:
        """Anti-regresión: evidencia binaria en reports/evidence/, no reviews/."""
        text = _read_contract()
        assert "reports/evidence/" in text
        assert "reviews/evidence/" not in text