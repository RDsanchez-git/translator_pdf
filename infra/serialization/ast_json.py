import os
import pathlib
import tempfile
from typing import List
from pydantic import TypeAdapter
from core.ast.models import ASTNode

# Constante de módulo inmutable para evitar recreaciones redundantes en memoria
_AST_LIST_ADAPTER: TypeAdapter[List[ASTNode]] = TypeAdapter(List[ASTNode])


def serialize_ast_json(nodes: List[ASTNode], indent: int | None = 2) -> str:
    """Convierte una colección de nodos AST a su representación JSON respetando el orden provisto."""
    return _AST_LIST_ADAPTER.dump_json(nodes, indent=indent).decode("utf-8")


def deserialize_ast_json(json_content: str) -> List[ASTNode]:
    """Rehidrata una cadena JSON cruda en instancias inmutables de ASTNode."""
    return _AST_LIST_ADAPTER.validate_json(json_content)


def write_ast_json_atomic(nodes: List[ASTNode], target_path: pathlib.Path, indent: int | None = 2) -> None:
    """Escribe la colección AST en disco de forma estrictamente atómica para prevenir corrupciones."""
    content = serialize_ast_json(nodes, indent=indent)
    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    # Garantía SRE: Escritura intermedia segura en el mismo sistema de archivos
    with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
        temp_path = pathlib.Path(tf.name)
        tf.write(content)
        tf.flush()
        
        # Forzar el vaciado del búfer del sistema operativo al medio físico
        try:
            os.fsync(tf.fileno())
        except (AttributeError, OSError):
            pass

    # Operación atómica a nivel de kernel (reemplazo seguro de punteros en disco)
    temp_path.rename(target_path)


def read_ast_json(source_path: pathlib.Path) -> List[ASTNode]:
    """Lee y rehidrata un artefacto físico desde el almacenamiento a memoria."""
    return deserialize_ast_json(source_path.read_text(encoding="utf-8"))