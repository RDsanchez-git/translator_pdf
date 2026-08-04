"""
NADR-03: Hashing semántico determinista del AST.

Este módulo contiene ÚNICAMENTE la función de hashing semántico.
La lógica de chunking fue extraída a core/chunking/semantic_chunking.py (NADR-03 §5.2).
"""

import json
from typing import Sequence

from core.ast.models import ASTNode
from core.shared.crypto import compute_sha256


def compute_ast_hash(ast: Sequence[ASTNode]) -> str:
    """
    NADR-03 §5.1: Generación determinística de firma semántica para el AST.

    El hash EXCLUYE explícitamente:
    - node_id: identidad efímera del nodo
    - sequence_id: orden de procesamiento
    - metadata: linaje físico (bboxes, pages, confidence)

    El hash INCLUYE únicamente:
    - node_type: tipo semántico del nodo
    - payload: contenido del nodo (vía text_content)

    NOTA: AST V2 (Fase 16.2) es plano. No existe children.

    Esto garantiza que dos ASTs semánticamente idénticos produzcan
    el mismo hash independientemente de su identidad física o orden de procesamiento.
    """
    def serialize_node(n: ASTNode) -> dict:
        # ASTNode.node_type está tipado definitivamente como ContentNodeType (Fase 16)
        type_str = n.node_type.value

        # NADR-03 §5.1 R2: Solo incluir node_type y payload
        # AST V2 es plano, no tiene children
        return {
            "type": type_str,
            "content": n.text_content,
        }

    raw = json.dumps(
        [serialize_node(n) for n in ast],
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )
    return compute_sha256(raw.encode("utf-8"))