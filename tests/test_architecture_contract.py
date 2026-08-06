import sqlite3
import pytest
from infra.db.control_repo import ControlPlaneRepository
from infra.db.event_repo import EventPlaneRepository
from infra.db.materialized_repo import MaterializedPlaneRepository
from core.execution.ports import ControlPlanePort, EventPlanePort, MaterializedPlanePort


def test_ports_compliance():
    """SOTA: Validación dinámica de Protocolos estructurales."""
    # SOTA: Conexiones en memoria simuladas para pasar el Type Hint checker
    dummy_conn = sqlite3.connect(":memory:")

    control = ControlPlaneRepository(dummy_conn)
    event = EventPlaneRepository(dummy_conn)
    mat = MaterializedPlaneRepository(dummy_conn)

    assert isinstance(control, ControlPlanePort), "Fallo de contrato en Control Plane"
    assert isinstance(event, EventPlanePort), "Fallo de contrato en Event Plane"
    assert isinstance(mat, MaterializedPlanePort), "Fallo de contrato en Materialized Plane"


def _is_ast_node_call(node) -> bool:
    """
    Detecta si una llamada AST es una invocación al constructor de ASTNode.

    Cubre tres formas de referencia para evitar bypasses:
    - ASTNode(**kwargs)          -> ast.Name con id == "ASTNode"
    - models.ASTNode(**kwargs)   -> ast.Attribute con attr == "ASTNode"
    - ast_models.ASTNode(**kwargs) -> ast.Attribute con attr == "ASTNode"
    """
    import ast as ast_module
    if isinstance(node.func, ast_module.Name):
        return node.func.id == "ASTNode"
    if isinstance(node.func, ast_module.Attribute):
        return node.func.attr == "ASTNode"
    return False


def test_ast_node_instantiation_contract():
    """
    NADR-01 §5.1 R3, R4: Detectar instanciación no tipada de ASTNode desde dicts.
    """
    import ast as ast_module
    from pathlib import Path

    project_root = Path(__file__).parent.parent

    scan_dirs = [
        project_root / "core",
        project_root / "infra",
        project_root / "apps",
        project_root / "runtime",
        project_root / "tools",
    ]

    # Archivos excluidos del escaneo (deuda técnica programada para eliminación)
    excluded_files = {
        # DF-09: core/ast/parser.py es el parser legacy regex programado para
        # eliminación en Gate 2, Wave 2.2 (Task 2.2.3). Se excluye temporalmente
        # del contract test para no bloquear la Wave 2.1.
        #"core/ast/parser.py", fue eliminado en Wave 2.2.3
    }

    violations = []

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue

        for py_file in scan_dir.rglob("*.py"):
            rel_path = str(py_file.relative_to(project_root)).replace("\\", "/")
            if rel_path in excluded_files:
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    source = f.read()

                tree = ast_module.parse(source, filename=str(py_file))

                for node in ast_module.walk(tree):
                    if isinstance(node, ast_module.Call):
                        if _is_ast_node_call(node):
                            for keyword in node.keywords:
                                if keyword.arg is None:
                                    violations.append(
                                        f"{py_file.relative_to(project_root)}: Línea {node.lineno} - "
                                        f"ASTNode(**kwargs) detectado. Usar PayloadRegistry.create() o deserialize_ast_json()."
                                    )

            except (SyntaxError, UnicodeDecodeError):
                continue

    if violations:
        pytest.fail(
            "NADR-01 §5.1 R3, R4: Se detectaron instanciaciones no tipadas de ASTNode:\n"
            + "\n".join(violations)
        )