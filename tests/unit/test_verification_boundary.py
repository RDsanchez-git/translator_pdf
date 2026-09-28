"""
Verification Boundary Tests (NADR-F17BIS-25 §5.1 R1-R4, §5.3 R8-R10).

Verifica estáticamente (vía AST parsing) que el verification entry point
normativo (run_regression.py):

1. Existe en la ubicación canónica esperada.
2. Importa build_extraction_pipeline desde apps.bootstrap.pipeline_factory.
3. No importa providers/parsers directamente como sustituto del pipeline.
4. Usa RegressionEvaluationStrategy como mecanismo de evaluación.
5. No existe un segundo mecanismo de verificación paralelo en core/apps/infra.

Estos tests son de verificación estructural (arquitectura), no de comportamiento.
No ejecutan el código bajo test; analizan la estructura de imports estáticamente.

Nota sobre el marker: estos tests leen archivos fuente y recorren directorios
del proyecto (I/O de filesystem). Según la taxonomía de pyproject.toml, el
marker "unit" se define como "Pure unit tests with no I/O". Por lo tanto se
usa el marker "integration", aunque no requieren recursos externos ni red.

NADR-F17BIS-25:
- R1: El sujeto de verificación MUST ser el production pipeline canónico.
- R2: MUST NOT verificar componentes aislados como sustituto.
- R3: MUST NOT usar fixtures sintéticos como referencia en CI.
- R4: La correspondencia sujeto ↔ verificación MUST ser demostrable.
- R8: MUST reutilizar el mecanismo existente (Integración, No Creación).
"""
from __future__ import annotations

import ast
import pathlib
from typing import List, Tuple

import pytest

# ── Paths relativos al root del proyecto ──────────────────────────────────────
# Este archivo vive en tests/unit/, así que parent.parent.parent = project root.
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
REGRESSION_ENTRY_POINT = PROJECT_ROOT / "tools" / "evaluation" / "run_regression.py"

# ── Módulos prohibidos como sustituto del production pipeline ─────────────────
# NADR-F17BIS-25 §5.1 R2: el entry point MUST NOT importar providers/parsers
# directamente. Debe obtener el PdfParserAdapter vía build_extraction_pipeline().
#
# Fuentes:
# - infra/extraction/providers/ (providers productivos actuales)
# - core/extraction/ocr_providers/ (providers legacy, según import-linter)
# - infra/adapters/pdf_parser.py (PdfParserAdapter, obtenido vía factory)
FORBIDDEN_SUBJECT_MODULES: frozenset[str] = frozenset({
    "infra.extraction.providers.pymupdf_provider",
    "infra.extraction.providers.docling_provider",
    "infra.extraction.providers.tesseract_provider",
    "core.extraction.ocr_providers.pymupdf_provider",
    "core.extraction.ocr_providers.docling_provider",
    "core.extraction.ocr_providers.tesseract_provider",
    "infra.adapters.pdf_parser",
})


# ── Utilidades de AST parsing ─────────────────────────────────────────────────


def _parse_imports(file_path: pathlib.Path) -> List[Tuple[str, str]]:
    """Extrae todos los imports de un archivo Python como (module, name).

    Args:
        file_path: Path al archivo Python a analizar.

    Returns:
        Lista de tuplas (module, name) para cada import encontrado.
        Para ``import X``, retorna (X, X).
        Para ``from M import N``, retorna (M, N).
    """
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))

    imports: List[Tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append((module, alias.name))

    return imports


# ── Tests: Verification Entry Point Boundary ──────────────────────────────────


@pytest.mark.integration
class TestVerificationEntryPointBoundary:
    """NADR-F17BIS-25 §5.1 R1-R4: El verification entry point normativo
    MUST usar exclusivamente el production pipeline canónico."""

    def test_entry_point_file_exists(self) -> None:
        """R1: El verification entry point normativo existe en la ubicación esperada."""
        assert REGRESSION_ENTRY_POINT.exists(), (
            f"Verification entry point not found: {REGRESSION_ENTRY_POINT}. "
            f"NADR-F17BIS-25 §5.1 R1 requires a formal, isolated verification "
            f"entry point."
        )

    def test_imports_build_extraction_pipeline_from_canonical_root(self) -> None:
        """R2: El entry point importa build_extraction_pipeline desde
        apps.bootstrap.pipeline_factory (composition root canónica)."""
        imports = _parse_imports(REGRESSION_ENTRY_POINT)

        # Buscar todas las importaciones de build_extraction_pipeline
        pipeline_imports = [
            (module, name)
            for module, name in imports
            if name == "build_extraction_pipeline"
        ]

        assert len(pipeline_imports) > 0, (
            "run_regression.py does not import build_extraction_pipeline. "
            "NADR-F17BIS-25 §5.1 R2 requires the verification entry point to "
            "invoke the production pipeline canonical composition root."
        )

        # Verificar que la importación es desde la ubicación canónica
        canonical_imports = [
            (module, name)
            for module, name in pipeline_imports
            if module == "apps.bootstrap.pipeline_factory"
        ]

        assert len(canonical_imports) > 0, (
            f"build_extraction_pipeline is imported from "
            f"{[m for m, _ in pipeline_imports]}, "
            f"expected apps.bootstrap.pipeline_factory. "
            f"NADR-F17BIS-25 §5.1 R2 requires importing from the canonical "
            f"composition root."
        )

    def test_does_not_import_forbidden_subject_modules(self) -> None:
        """R2: El entry point MUST NOT importar providers/parsers/adapters
        directamente como sustituto del pipeline."""
        imports = _parse_imports(REGRESSION_ENTRY_POINT)
        imported_modules = {module for module, _ in imports}

        violations = imported_modules & FORBIDDEN_SUBJECT_MODULES
        assert not violations, (
            f"run_regression.py imports forbidden modules directly: "
            f"{sorted(violations)}. "
            f"NADR-F17BIS-25 §5.1 R2 prohibits importing providers/parsers "
            f"directly as substitutes for the production pipeline. "
            f"The PdfParserAdapter must be obtained via "
            f"build_extraction_pipeline()."
        )

    def test_uses_regression_evaluation_strategy(self) -> None:
        """R4: El entry point usa RegressionEvaluationStrategy como mecanismo
        de evaluación canónico."""
        imports = _parse_imports(REGRESSION_ENTRY_POINT)

        strategy_imports = [
            (module, name)
            for module, name in imports
            if name == "RegressionEvaluationStrategy"
        ]

        assert len(strategy_imports) > 0, (
            "run_regression.py does not import RegressionEvaluationStrategy. "
            "NADR-F17BIS-25 §5.1 R4 requires the verification entry point to "
            "use the canonical regression evaluation strategy."
        )

    def test_entry_point_calls_build_extraction_pipeline(self) -> None:
        """R4: El entry point invoca build_extraction_pipeline().

        Verifica que el entry point no solo importa sino que también
        invoca la composition root (correspondencia demostrable).
        """
        source = REGRESSION_ENTRY_POINT.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(REGRESSION_ENTRY_POINT))

        found_call = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == "build_extraction_pipeline":
                        found_call = True
                        break

        assert found_call, (
            "run_regression.py does not call build_extraction_pipeline(). "
            "NADR-F17BIS-25 §5.1 R4 requires demonstrable correspondence "
            "between the verification entry point and the production pipeline."
        )


@pytest.mark.integration
class TestNoParallelVerificationMechanism:
    """NADR-F17BIS-25 §5.3 R8-R10: MUST NOT existir un segundo mecanismo
    de verificación paralelo fuera del entry point normativo.

    Nota: esta verificación detecta imports directos de
    RegressionEvaluationStrategy en core/, apps/, infra/. La verificación
    completa de ausencia de mecanismos paralelos se complementa en
    Task 1.1.3 con un contrato import-linter en pyproject.toml, que
    cubre también imports indirectos y composiciones alternativas.
    """

    def test_no_module_in_core_apps_infra_orchestrates_regression(self) -> None:
        """R8: Ningún módulo en core/, apps/, o infra/ importa
        RegressionEvaluationStrategy para orquestar verificación."""
        search_dirs = [
            PROJECT_ROOT / "core",
            PROJECT_ROOT / "apps",
            PROJECT_ROOT / "infra",
        ]

        orchestrating_modules: List[str] = []

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for py_file in search_dir.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                try:
                    imports = _parse_imports(py_file)
                    imported_names = {name for _, name in imports}
                    if "RegressionEvaluationStrategy" in imported_names:
                        rel_path = py_file.relative_to(PROJECT_ROOT)
                        orchestrating_modules.append(str(rel_path))
                except (SyntaxError, UnicodeDecodeError):
                    continue

        assert not orchestrating_modules, (
            f"Modules outside tools/evaluation/run_regression.py import "
            f"RegressionEvaluationStrategy: {orchestrating_modules}. "
            f"NADR-F17BIS-25 §5.3 R8 prohibits parallel verification "
            f"mechanisms. Only tools/evaluation/run_regression.py may "
            f"orchestrate regression evaluation against the sealed baseline."
        )

@pytest.mark.integration
class TestNoLocalExitCodesInEntryPoint:
    """ENGINEERING_PRINCIPLES §IV: única fuente de verdad para exit codes."""

    def test_run_regression_does_not_define_exit_codes_locally(self) -> None:
        """Las constantes EXIT_* MUST importarse de core.benchmark.verification.outcome.

        Esto previene divergencia silenciosa entre run_regression.py y
        outcome.py (dos fuentes de verdad).
        """
        source = REGRESSION_ENTRY_POINT.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(REGRESSION_ENTRY_POINT))

        local_exit_definitions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.startswith("EXIT_"):
                        local_exit_definitions.append(target.id)

        assert not local_exit_definitions, (
            f"run_regression.py defines EXIT_* constants locally: "
            f"{local_exit_definitions}. These MUST be imported from "
            f"core.benchmark.verification.outcome to maintain a single "
            f"source of truth (ENGINEERING_PRINCIPLES §IV)."
        )