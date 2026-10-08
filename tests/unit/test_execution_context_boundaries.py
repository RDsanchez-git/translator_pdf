"""
Test de arquitectura para verificar los boundaries de contextos del execution plane.

Verifica:
1. Que los 6 contextos existen y son importables.
2. Que no hay god-object (ningún módulo importa todos los contextos).
3. Que cada contexto tiene un boundary único documentado.

NADR-F18-02 §5.6 R20-R22. DC-05.
"""
from __future__ import annotations

import ast
from pathlib import Path

from core.execution.context_boundaries import (
    ALL_BOUNDARIES,
    ASSEMBLY_CONTEXT_BOUNDARY,
    CONTEXT_RESOLVER_BOUNDARY,
    CONTROL_PLANE_BOUNDARY,
    EVENT_PLANE_BOUNDARY,
    FSM_STATE_BOUNDARY,
    MATERIALIZED_PLANE_BOUNDARY,
)


class TestContextBoundariesExist:
    """NADR-F18-02 §5.6 R20: context boundaries explícitos."""

    def test_six_boundaries_defined(self):
        assert len(ALL_BOUNDARIES) == 6

    def test_control_plane_boundary(self):
        assert CONTROL_PLANE_BOUNDARY.context_name == "ControlPlanePort"
        assert "ControlPlanePort" in CONTROL_PLANE_BOUNDARY.module_path

    def test_event_plane_boundary(self):
        assert EVENT_PLANE_BOUNDARY.context_name == "EventPlanePort"

    def test_materialized_plane_boundary(self):
        assert MATERIALIZED_PLANE_BOUNDARY.context_name == "MaterializedPlanePort"

    def test_fsm_state_boundary(self):
        assert FSM_STATE_BOUNDARY.context_name == "FSM State"

    def test_context_resolver_boundary(self):
        assert CONTEXT_RESOLVER_BOUNDARY.context_name == "ContextResolver"

    def test_assembly_context_boundary(self):
        assert ASSEMBLY_CONTEXT_BOUNDARY.context_name == "AssemblyContext"

    def test_all_boundaries_have_responsibility(self):
        for boundary in ALL_BOUNDARIES:
            assert len(boundary.responsibility) > 0, (
                f"{boundary.context_name} sin responsabilidad documentada"
            )

    def test_all_boundaries_have_thread_safety(self):
        for boundary in ALL_BOUNDARIES:
            assert len(boundary.thread_safety) > 0, (
                f"{boundary.context_name} sin contrato de thread-safety"
            )


class TestContextModulesImportable:
    """Verifica que los módulos de cada contexto existen y son importables."""

    def test_control_plane_port_importable(self):
        from core.execution.ports import ControlPlanePort
        assert ControlPlanePort is not None

    def test_event_plane_port_importable(self):
        from core.execution.ports import EventPlanePort
        assert EventPlanePort is not None

    def test_materialized_plane_port_importable(self):
        from core.execution.ports import MaterializedPlanePort
        assert MaterializedPlanePort is not None

    def test_fsm_state_importable(self):
        from core.execution.state import DocumentState, FSMValidator
        assert DocumentState is not None
        assert FSMValidator is not None

    def test_context_resolver_importable(self):
        from core.context.context_resolver import (
            ContextResolverProtocol,
            InMemoryContextResolver,
        )
        assert ContextResolverProtocol is not None
        assert InMemoryContextResolver is not None

    def test_assembly_context_importable(self):
        from core.compiler.assembly_context import AssemblyExecutionContext
        assert AssemblyExecutionContext is not None


class TestNoGodObject:
    """
    NADR-F18-02 §5.6 R21: no god-object.

    Verifica que no existe un módulo que importe TODAS las clases de contexto
    simultáneamente (lo cual indicaría un god-object).
    """

    def test_no_module_imports_all_six_context_classes(self):
        """
        Ningún módulo debe importar las 6 clases de contexto simultáneamente.
        Verifica por CLASES importadas (no por módulos) para detectar
        god-objects reales con mayor granularidad.

        Umbral: < 6 clases. Si un archivo importa las 6, es god-object.
        """
        project_root = Path(__file__).parent.parent.parent

        # Las 6 clases de contexto que no deben coexistir en un solo archivo
        context_classes = {
            "ControlPlanePort",
            "EventPlanePort",
            "MaterializedPlanePort",
            "DocumentState",
            "ContextResolverProtocol",
            "AssemblyExecutionContext",
        }

        excluded_files = {
            "context_boundaries.py",
            "test_execution_context_boundaries.py",
            "__init__.py",
        }

        # Excluir directorios de dependencias y cache (no son código propio)
        excluded_dirs = {
            "venv", ".venv", "env", ".env",
            "node_modules",
            ".git",
            ".pytest_cache",
            "__pycache__",
            ".tox",
            ".mypy_cache",
            ".ruff_cache",
            "dist", "build",
        }

        def is_in_excluded_dir(path: Path) -> bool:
            """Verifica si el path está dentro de un directorio excluido."""
            for part in path.parts:
                if part in excluded_dirs:
                    return True
            return False

        for py_file in project_root.rglob("*.py"):
            if py_file.name in excluded_files:
                continue

            if is_in_excluded_dir(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                    tree = ast.parse(f.read())
            except (SyntaxError, UnicodeDecodeError):
                continue

            # Extraer nombres de clases importadas (ImportFrom)
            imported_classes: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imported_classes.add(alias.name)

            # Verificar que no importe las 6 clases de contexto
            context_imports = imported_classes & context_classes

            assert len(context_imports) < 6, (
                f"God-object detectado en {py_file.relative_to(project_root)}: "
                f"importa {len(context_imports)} clases de contexto "
                f"({', '.join(sorted(context_imports))}). "
                f"DC-05 exige contextos especializados separados."
            )

    def test_context_boundaries_module_is_not_god_object(self):
        """
        context_boundaries.py NO es un god-object: solo documenta boundaries,
        no importa los contextos ni agrega comportamiento.
        """
        import core.execution.context_boundaries as cb_module

        source = Path(cb_module.__file__).read_text(encoding="utf-8")

        assert "from core.execution.ports import" not in source
        assert "from core.execution.state import" not in source
        assert "from core.context.context_resolver import" not in source
        assert "from core.compiler.assembly_context import" not in source