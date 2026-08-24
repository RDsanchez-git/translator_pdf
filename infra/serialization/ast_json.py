import os
import pathlib
import tempfile
from typing import List
from pydantic import TypeAdapter
from core.ast.models import ASTNode

_AST_LIST_ADAPTER: TypeAdapter[List[ASTNode]] = TypeAdapter(List[ASTNode])


def serialize_ast_json(nodes: List[ASTNode], indent: int | None = 2) -> str:
    """Convierte una colección de nodos AST a su representación JSON respetando el orden provisto."""
    return _AST_LIST_ADAPTER.dump_json(nodes, indent=indent).decode("utf-8")


def deserialize_ast_json(json_content: str) -> List[ASTNode]:
    """Rehidrata una cadena JSON cruda en instancias inmutables de ASTNode."""
    return _AST_LIST_ADAPTER.validate_json(json_content)


def write_ast_json_atomic(nodes: List[ASTNode], target_path: pathlib.Path, indent: int | None = 2) -> None:
    """Escribe la colección AST en disco de forma estrictamente atómica para prevenir corrupciones.

    NADR-F17BIS-01 §5.6: escritura intermedia + fsync + reemplazo atómico.
    Corrección Task 1.3.2: os.replace() en lugar de Path.rename() para
    garantizar reemplazo atómico multiplataforma (Windows lanza FileExistsError
    con rename() si el destino existe).
    """
    content = serialize_ast_json(nodes, indent=indent)
    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
        temp_path = pathlib.Path(tf.name)
        tf.write(content)
        tf.flush()

        try:
            os.fsync(tf.fileno())
        except (AttributeError, OSError):
            pass

    # os.replace() es atómico y multiplataforma: sobrescribe el destino si existe.
    # Path.rename() (os.rename) lanza FileExistsError en Windows si el destino existe.
    os.replace(temp_path, target_path)


def read_ast_json(source_path: pathlib.Path) -> List[ASTNode]:
    """Lee y rehidrata un artefacto físico desde el almacenamiento a memoria."""
    return deserialize_ast_json(source_path.read_text(encoding="utf-8"))