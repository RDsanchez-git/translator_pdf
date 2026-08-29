"""
NADR-03 §5.1, NADR-F17BIS-16 §5.2: Hashing semántico determinista del AST.

CONTRATO ALTERNATIVO (NO CANÓNICO PARA LINAJE):
Este módulo implementa un contrato alternativo de hashing semántico del AST,
diseñado para comparación de parsers y evaluación topológica. NO es el
contrato canónico para el linaje de la baseline científica.

DIFERENCIACIÓN DE CONTRATOS (DC-01 resuelto):
- compute_ast_hash (ESTE): Contrato alternativo para comparación de parsers.
  Excluye node_id porque busca comparar contenido semántico puro, independiente
  de la identidad de los nodos. Dos ASTs con la misma estructura semántica
  producirán el mismo hash, incluso si los node_id son diferentes.

- OracleSemanticIdentityCalculator (core/benchmark/ground_truth/identity.py):
  Contrato canónico para linaje de baseline. Incluye node_id porque la identidad
  del oráculo requiere distinguir nodos, incluso si el contenido es idéntico.

Ambos contratos coexisten legítimamente con propósitos arquitectónicos distintos
(NADR-F17BIS-16 §5.2 R4-R8).

Este módulo contiene ÚNICAMENTE la función de hashing semántico.
La lógica de chunking fue extraída a core/chunking/semantic_chunking.py (NADR-03 §5.2).
"""

import json
from typing import Sequence

from core.ast.models import ASTNode
from core.shared.crypto import compute_sha256


def compute_ast_hash(ast: Sequence[ASTNode]) -> str:
    """
    NADR-03 §5.1, NADR-F17BIS-16 §5.2: Generación determinística de firma
    semántica para el AST (contrato alternativo, no canónico para linaje).

    SENSIBILIDAD AL ORDEN (DC-06 resuelto):
    Esta función ES SENSIBLE al orden de los nodos en la secuencia. El docstring
    anterior mencionaba "independientemente de su orden de procesamiento", lo cual
    era ambiguo. La clarificación es:
    - El orden de los nodos en la secuencia SÍ afecta el hash (es parte de la
      identidad estructural del AST).
    - El orden interno de procesamiento (cómo se visitan los nodos durante la
      serialización) NO afecta el hash (gracias a sort_keys=True en json.dumps).

    El hash EXCLUYE explícitamente:
    - node_id: identidad efímera del nodo
    - sequence_id: índice en el documento original
    - metadata: linaje físico (bboxes, pages, confidence)

    El hash INCLUYE únicamente:
    - node_type: tipo semántico del nodo
    - payload: contenido del nodo (vía text_content)
    - El orden de los nodos en la secuencia

    NOTA: AST V2 (Fase 16.2) es plano. No existe children.

    PROPÓSITO: Comparación de parsers y evaluación topológica. Para linaje de
    baseline, usar OracleSemanticIdentityCalculator (NADR-F17BIS-16 §5.2 R8).
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