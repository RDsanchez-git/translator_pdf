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

    Este contract test escanea todos los archivos Python del proyecto (excluyendo
    tests) y falla si encuentra patrones del tipo:
    - ASTNode(**some_dict)
    - ASTNode(**data)
    - ASTNode(**kwargs)
    - models.ASTNode(**kwargs)
    - ast_models.ASTNode(**kwargs)

    La instanciación de ASTNode DEBE realizarse mediante:
    - PayloadRegistry.create() + ASTNode(node_id=..., payload=...)
    - infra.serialization.ast_json.deserialize_ast_json()

    NOTA: tools/ está INCLUIDO en el escaneo (no se excluye).
    """
    import ast as ast_module
    from pathlib import Path

    project_root = Path(__file__).parent.parent

    # Directorios a escanear (excluir SOLO tests)
    # tools/ se INCLUYE porque también debe cumplir el contrato
    scan_dirs = [
        project_root / "core",
        project_root / "infra",
        project_root / "apps",
        project_root / "runtime",
        project_root / "tools",
    ]

    violations = []

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue

        for py_file in scan_dir.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    source = f.read()

                tree = ast_module.parse(source, filename=str(py_file))

                # Buscar llamadas a ASTNode con **kwargs
                for node in ast_module.walk(tree):
                    if isinstance(node, ast_module.Call):
                        # Verificar si es una llamada a ASTNode (Name o Attribute)
                        if _is_ast_node_call(node):
                            # Buscar argumentos con **kwargs (keyword con arg=None)
                            for keyword in node.keywords:
                                if keyword.arg is None:  # Esto indica **kwargs
                                    violations.append(
                                        f"{py_file.relative_to(project_root)}: Línea {node.lineno} - "
                                        f"ASTNode(**kwargs) detectado. Usar PayloadRegistry.create() o deserialize_ast_json()."
                                    )

            except (SyntaxError, UnicodeDecodeError):
                # Ignorar archivos con errores de sintaxis o encoding
                continue

    if violations:
        pytest.fail(
            "NADR-01 §5.1 R3, R4: Se detectaron instanciaciones no tipadas de ASTNode:\n"
            + "\n".join(violations)
        )