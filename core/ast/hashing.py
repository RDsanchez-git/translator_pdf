"""Identidad semántica AST para la ruta productiva PPPR (G2/W2.2).

Contrato AST_SEMANTIC_PRODUCT_V2: tipo, contenido Unicode canónico conservador,
posición de secuencia y jerarquía explícita. Excluye IDs de nodos, metadata
física, control_plane, geometría y estado operacional.

No es la identidad canónica del oráculo F17-BIS ni una identidad de generación
EN→ES: cada consumidor debe verificar también sus otras dimensiones relevantes.
El cambio de contrato invalida la comparación/reutilización basada en el hash
legacy: nunca aceptar un hash V1 como prueba de identidad V2.
"""

from __future__ import annotations

import json
from typing import Sequence
import unicodedata

from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, HeadingPayload
from core.shared.crypto import compute_sha256

_CONTRACT = "AST_SEMANTIC_PRODUCT_V2"


def _canonical_stem_text(text: str) -> str:
    """NFC solo donde no colapsa un símbolo precompuesto por sí solo.

    NFC por defecto colapsa K->K y Ω->Ω. No se presume la equivalencia de
    símbolos STEM ni se aplica NFKC. La composición diacrítica de letras
    (e + COMBINING ACUTE -> é) se permite solo si todos los codepoints de
    entrada son individualmente estables ante NFC. Conserva bytes para
    casos ambiguos; nunca cambia silenciosamente símbolos químicos/matemáticos.
    """
    if any(unicodedata.normalize("NFC", char) != char for char in text):
        return text
    return unicodedata.normalize("NFC", text)


def compute_ast_hash(ast: Sequence[ASTNode]) -> str:
    """Firma semántica versionada por contenido/orden/jerarquía.

    Ni node_id ni sequence_id ni source_document forman parte del preimage;
    un reintento o variación física no cambia esta identidad semántica.
    """
    elements: list[dict[str, str | int]] = []
    for node in ast:
        if node.depth < 0:
            raise ValueError("PPPR_G2_INVALID_AST_SEMANTIC_DEPTH")
        element: dict[str, str | int] = {
            "node_type": node.node_type.value,
            "content": _canonical_stem_text(node.text_content or ""),
            "depth": node.depth,
        }
        if node.node_type == ContentNodeType.HEADING:
            if not isinstance(node.payload, HeadingPayload):
                raise ValueError("PPPR_G2_INVALID_HEADING_PAYLOAD")
            # UNKNOWN es una identidad distinta, NO se convierte a H1.
            element["heading_level"] = node.payload.heading_level.value
        elements.append(element)
    encoded = json.dumps(
        {"contract": _CONTRACT, "nodes": elements},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    return compute_sha256(encoded)
