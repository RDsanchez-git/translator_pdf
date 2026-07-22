from pathlib import Path
from typing import Sequence
from core.ast.models import ASTNode
from infra.serialization.ast_json import read_ast_json


def load_ast_sequence_from_json(filepath: Path) -> Sequence[ASTNode]:
    """Carga y deserializa una secuencia ordenada de ASTNodes reutilizando

    la infraestructura de serialización nativa del proyecto.
    """
    nodes = read_ast_json(filepath)
    return tuple(nodes)