"""Guardia negativa de cobertura observable para el adaptador PyMuPDF.

B02 (parcial): no permite que objetos descartados por esta ruta lleguen a
presentarse como un AST completo. No certifica la fidelidad del texto ni la
detección de todas las ecuaciones, tablas o pérdidas de fuentes PDF.

La guardia es infraestructura del proveedor; no altera el contrato del AST.
"""

from collections.abc import Mapping, Sequence
from typing import Any


class UnrepresentedPdfContentError(ValueError):
    """Un objeto visible para PyMuPDF no tiene representación en este adapter."""


def validate_pymupdf_page_coverage(
    raw_blocks: Sequence[Mapping[str, Any]],
    *,
    page_number: int,
    has_vector_drawings: bool,
    allow_image_blocks: bool = False,
) -> None:
    """Detiene únicamente pérdidas *observables* en esta frontera.

    - type != 0: los bloques no-textuales se omitían silenciosamente.
    - U+FFFD/U+FFFF: texto extraído con sustitución o no-caracteres visibles.
    - trazos vectoriales: esta ruta no crea nodos/activos para preservarlos.

    No asume que todo trazo es una ecuación ni que su ausencia prueba fidelidad.
    Es una política provisional fail-closed, potencialmente restrictiva.
    """
    for index, block in enumerate(raw_blocks):
        block_type = block.get("type")
        native_index = block.get("number", index)

        if block_type == 1 and allow_image_blocks:
            continue  # Materialization is owned by PyMuPDFProvider, not this guard.
        if block_type != 0:
            category = "IMAGE" if block_type == 1 else "UNSUPPORTED"
            raise UnrepresentedPdfContentError(
                f"B02_UNREPRESENTED_{category}_BLOCK: "
                f"page={page_number} block={native_index} type={block_type!r}; "
                "PyMuPDFProvider no materializa este bloque en Layout/AST"
            )

        for line_index, line in enumerate(block.get("lines", [])):
            for span_index, span in enumerate(line.get("spans", [])):
                span_text = span.get("text", "")
                for codepoint, char in (("U+FFFD", "\ufffd"), ("U+FFFF", "\uffff")):
                    if char in span_text:
                        raise UnrepresentedPdfContentError(
                            "B02_UNMAPPED_GLYPH: "
                            f"page={page_number} block={native_index} "
                            f"line={line_index} span={span_index} codepoint={codepoint}; "
                            "no hay evidencia de recuperación del glifo original"
                        )

    if has_vector_drawings:
        raise UnrepresentedPdfContentError(
            f"B02_UNREPRESENTED_VECTOR_DRAWING: page={page_number}; "
            "la ruta actual no conserva trazos vectoriales en Layout/AST"
        )
