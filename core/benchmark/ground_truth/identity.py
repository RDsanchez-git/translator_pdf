"""Identidad semántica del oráculo (NADR-15 §5.1, NADR-F17BIS-16 §5.2).

CONTRATO CANÓNICO PARA LINAJE DE BASELINE:
Este módulo implementa el contrato canónico de identidad semántica del oráculo
para el linaje de la baseline científica (NADR-F17BIS-16 §5.2 R8).

DIFERENCIACIÓN DE CONTRATOS (DC-01 resuelto):
- OracleSemanticIdentityCalculator (ESTE): Contrato canónico para linaje de baseline.
  Incluye node_id porque la identidad del oráculo requiere distinguir nodos,
  incluso si el contenido semántico es idéntico. Esto garantiza que dos oráculos
  con la misma estructura pero diferentes identidades de nodo produzcan hashes
  distintos, protegiendo la integridad del proceso de certificación.

- compute_ast_hash (core/ast/hashing.py): Contrato alternativo para comparación
  de parsers y evaluación topológica. Excluye node_id porque busca comparar
  contenido semántico puro, independiente de la identidad de los nodos.

Ambos contratos coexisten legítimamente con propósitos arquitectónicos distintos
(NADR-F17BIS-16 §5.2 R4-R8).

Materializa la identidad semántica del oráculo ($H_{semantic}$), un hash
determinista que captura el contenido semántico del oráculo sin acoplarse
a metadata física incidental.

Propiedades garantizadas:
- Determinismo: mismo contenido → mismo hash
- Sensibilidad al contenido: cambiar texto → hash diferente
- Sensibilidad al orden: cambiar orden de nodos → hash diferente
- Sensibilidad al node_id, node_type y strategy
- Insensibilidad a metadata física: sequence_id, depth, parent_id, etc.
  NO afectan el hash

Reutilización (Reuse Before Invent, ADR Maestro §5):
- compute_sha256 de core/shared/crypto.py
- model_dump_json() de Pydantic para serialización determinista de payloads

Observación X1 cerrada: ninguno de los 7 payloads (HeadingPayload,
ParagraphPayload, MathPayload, CodePayload, TablePayload, ImagePayload,
ListPayload) tiene campos Dict[str, Any]. Por lo tanto, model_dump_json()
es determinista para todos los payloads sin necesidad de sort_keys.

Nota sobre payload: ASTNode.payload es un campo requerido (tipo ASTPayload,
no Optional). Pydantic garantiza en construcción que payload nunca es None.
No se requiere verificación defensiva (YAGNI, Explicit over Implicit).
"""

from __future__ import annotations

from typing import Tuple

from core.ast.models import ASTNode
from core.shared.crypto import compute_sha256


class OracleSemanticIdentityCalculator:
    """Calcula la identidad semántica de un oráculo (NADR-15 §5.1).

    La identidad semántica es un hash determinista que captura:
    - El identificador de cada nodo (node_id)
    - El tipo de cada nodo (node_type)
    - La estrategia de traducción (strategy)
    - El contenido del payload (serializado determinísticamente)
    - El orden de los nodos (la tupla es ordenada)

    NO captura metadata física incidental:
    - sequence_id (índice en el documento original)
    - depth, parent_node_id (topología física)
    - metadata (bboxes, pages, confidence)
    - control_plane (Dict[str, Any] de control)
    - segment_index, segment_count (segmentación)

    Esto garantiza que la identidad semántica capture "qué dice el oráculo"
    y no "dónde está en el PDF".
    """

    @staticmethod
    def calculate(nodes: Tuple[ASTNode, ...]) -> str:
        """Calcula la identidad semántica de un oráculo.

        Args:
            nodes: Tupla ordenada de nodos AST del oráculo.

        Returns:
            Hash SHA-256 determinista de la identidad semántica.

        Observación X2: La atomicidad entre el hash físico (disco) y el
        hash semántico (memoria) se garantiza por la ausencia de escrituras
        concurrentes durante la curaduría. No requiere código adicional.
        """
        parts = []
        for node in nodes:
            # Serialización determinista del payload.
            # Observación X1 cerrada: todos los payloads tienen campos
            # tipados sin Dict[str, Any], por lo que model_dump_json()
            # es determinista sin necesidad de sort_keys.
            # payload es campo requerido de ASTNode (nunca None).
            payload_json = node.payload.model_dump_json()
            payload_hash = compute_sha256(payload_json.encode("utf-8"))

            # Identidad del nodo: node_id:type:strategy:payload_hash
            # NO incluye sequence_id, depth, parent_node_id, metadata,
            # control_plane, segment_index, segment_count.
            node_identity = (
                f"{node.node_id}:"
                f"{node.node_type.value}:"
                f"{node.strategy.value}:"
                f"{payload_hash}"
            )
            parts.append(node_identity.encode("utf-8"))

        return compute_sha256(b"".join(parts))