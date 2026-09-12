"""Contratos de frontera de certificacion (NADR-24 SS5.6 R25-R28, Task 4.3.1).

R25: SealedOracle sin mutadores de instancia y congelado (config + conductual).
R26: ningun modulo de certificacion importa puertos de escritura de GT.
R27: los adaptadores de GT apuntan unicamente al directorio ground_truth/.
R28: la autoridad de lifecycle reside solo en el dominio (use cases activos).
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.benchmark.ground_truth.models import SealedOracle
from infra.fs.ground_truth_store import (
    LocalFileSystemGroundTruthArtifactAdapter,
    LocalFileSystemGroundTruthReader,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

CERTIFICATION_MODULES = [
    REPO_ROOT / "core" / "benchmark" / "certification" / "contract.py",
    REPO_ROOT / "core" / "benchmark" / "certification" / "preflight.py",
    REPO_ROOT / "tools" / "evaluation" / "preflight_certification.py",
    REPO_ROOT / "tools" / "evaluation" / "freeze_parameters.py",
]

FORBIDDEN_GT_WRITE_SYMBOLS = (
    "LocalFileSystemGroundTruthDraftWriter",
    "save_draft_ast",
    "LifecycleTransitionAuthority",
    "SealGroundTruthUseCase",
    "write_ast_json_atomic",
)

IMPORT_AUTHORITY_PAT = re.compile(
    r"^\s*(from|import)\s+.*LifecycleTransitionAuthority", re.M
)

# Capas activas: se excluye tools/benchmark_archive (legacy de archivo, O-4.3-1)
ACTIVE_SCAN_ROOTS = ["core", "infra", "apps", "bootstrap", "tools/evaluation"]

ALLOWED_AUTHORITY_IMPORTERS = {
    Path("core/benchmark/ground_truth/use_cases.py"),
    # Entry point de sellado (MIG-06, Gate 2): orquesta el ciclo de vida en
    # memoria INVOCANDO la autoridad (diseno congelado en Wave 2.2). Es tooling
    # de gestion de lifecycle, no de ejecucion certificante. R28 prohibe
    # bypassear la autoridad, no invocarla. Ver O-4.3-3 del Record.
    Path("tools/evaluation/freeze_ground_truth.py"),
}


class TestSealedOracleImmutability:
    def test_no_instance_mutators(self) -> None:
        mutators = [
            name
            for name, _member in inspect.getmembers(SealedOracle)
            if not name.startswith("_")
            and callable(getattr(SealedOracle, name))
            and (name.startswith("set_") or name.startswith("with_") or name.startswith("update_"))
            and not isinstance(
                inspect.getattr_static(SealedOracle, name), (classmethod, staticmethod)
            )
        ]
        assert mutators == []

    def test_pydantic_frozen_config(self) -> None:
        """R25: SealedOracle es frozen a nivel de configuracion Pydantic."""
        assert SealedOracle.model_config.get("frozen") is True

    def test_assignment_raises(self) -> None:
        """R25: asignacion de atributo bloqueada en instancia construida por keywords."""
        oracle = SealedOracle(document_id="doc-1", nodes=())
        with pytest.raises(ValidationError):
            oracle.document_id = "doc-2"  # type: ignore[misc]


class TestCertificationModulesWithoutGtWritePorts:
    @pytest.mark.parametrize("module_path", CERTIFICATION_MODULES, ids=lambda p: p.name)
    def test_no_forbidden_gt_write_symbols(self, module_path: Path) -> None:
        source = module_path.read_text(encoding="utf-8")
        for symbol in FORBIDDEN_GT_WRITE_SYMBOLS:
            assert symbol not in source, f"{module_path.name} referencia {symbol}"


class TestGtAdaptersScopedToGroundTruthDir:
    def test_artifact_adapter_ignores_candidates_and_reports(self, tmp_path: Path) -> None:
        (tmp_path / "ground_truth").mkdir()
        (tmp_path / "candidates").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "ground_truth" / "doc-a.json").write_text("[]", encoding="utf-8")
        (tmp_path / "candidates" / "doc-b.json").write_text("[]", encoding="utf-8")
        (tmp_path / "reports" / "doc-c.json").write_text("[]", encoding="utf-8")
        adapter = LocalFileSystemGroundTruthArtifactAdapter(base_path=tmp_path)
        assert adapter.list_artifact_ids() == ("doc-a",)

    def test_reader_ignores_candidates_dir(self, tmp_path: Path) -> None:
        """R27: el reader no resuelve artefactos fuera de ground_truth/ (conductual)."""
        (tmp_path / "candidates").mkdir()
        (tmp_path / "candidates" / "doc-x.json").write_text("[]", encoding="utf-8")
        reader = LocalFileSystemGroundTruthReader(base_path=tmp_path)
        with pytest.raises(FileNotFoundError):
            reader.load_ground_truth("doc-x")


class TestLifecycleAuthorityOwnership:
    def test_only_domain_use_cases_import_authority(self) -> None:
        """R28: la autoridad solo la importan el dominio y el entry point de sellado."""
        offenders = []
        for root in ACTIVE_SCAN_ROOTS:
            for path in (REPO_ROOT / root).rglob("*.py"):
                source = path.read_text(encoding="utf-8", errors="ignore")
                if IMPORT_AUTHORITY_PAT.search(source):
                    rel = path.relative_to(REPO_ROOT)
                    if rel not in ALLOWED_AUTHORITY_IMPORTERS:
                        offenders.append(str(rel))
        assert offenders == []
