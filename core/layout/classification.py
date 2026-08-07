# core/layout/classification.py
"""
Clasificación de bloques de layout basada en señales físicas.

Responsabilidad: Determinar el LayoutBlockType de un bloque a partir de
señales tipográficas, posicionales y textuales.

NADR-02: Este módulo pertenece al dominio. No conoce proveedores concretos.
El provider inyecta señales; el clasificador devuelve un tipo de dominio.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from core.domain.document import LayoutBlockType, BoundingBox


@dataclass(frozen=True)
class PageClassificationContext:
    """Contexto estadístico de la página para clasificación relativa."""
    median_font_size: float
    dominant_font_size: float
    page_number: int
    total_pages: int
    block_count: int
    page_height: float
    page_width: float


@dataclass(frozen=True)
class BlockClassificationSignals:
    """Señales físicas de un bloque individual, extraídas por el provider."""
    text: str
    font_name: str | None
    font_size: float | None
    is_bold: bool
    is_italic: bool
    bbox: BoundingBox | None
    reading_order: int


class LayoutClassifier(Protocol):
    """
    Puerto de dominio para clasificación de bloques de layout.

    El provider extrae señales físicas; el clasificador determina el tipo lógico.
    Esta separación garantiza que el provider no conozca reglas de negocio
    y que el clasificador no conozca implementaciones de extracción.
    """
    def classify(
        self,
        signals: BlockClassificationSignals,
        context: PageClassificationContext,
    ) -> LayoutBlockType: ...


# ─────────────────────────────────────────────────────────────────────────────
# HeuristicLayoutClassifier
# ─────────────────────────────────────────────────────────────────────────────

_HEADER_PATTERNS = re.compile(
    r"(contents\s+lists|journal\s+homepage|available\s+online|sciencedirect|elsevier|springer|wiley)",
    re.IGNORECASE,
)

_REFERENCE_PATTERN = re.compile(
    r"^\s*(\[?\d{1,4}\]?|bib\d+)\s*[\.:\)]",
)

_LIST_BULLET_PATTERN = re.compile(r"^\s*[-•▪◦■♦○]\s+")
_LIST_NUMBER_PATTERN = re.compile(r"^\s*\d{1,3}[\.:\)]\s+")

_AUTHOR_AFFILIATION_PATTERN = re.compile(r"[a-z]\s*,\s*[A-Z]|⁎|✉|†|‡|§|¶|\buniversity\b|\binstitute\b|\bdepartment\b", re.IGNORECASE)


class HeuristicLayoutClassifier:
    """
    Clasificador heurístico basado en señales tipográficas y posicionales.

    Limitaciones conocidas (DF-15):
    - PyMuPDF no detecta tablas (se degradan a PARAGRAPH)
    - PyMuPDF no detecta ecuaciones (se degradan a PARAGRAPH)
    - Las imágenes se filtran en la extracción física (type != 0)

    Para detección avanzada de tablas/ecuaciones, evaluar Docling o Nougat
    en Fase 17 (benchmark de proveedores).
    """

    def classify(
        self,
        signals: BlockClassificationSignals,
        context: PageClassificationContext,
    ) -> LayoutBlockType:
        text = signals.text.strip()
        if not text:
            return LayoutBlockType.UNKNOWN

        # 1. Page header/footer (posicional + léxico canónico)
        if self._is_page_header_or_footer(text, signals, context):
            return LayoutBlockType.HEADER

        # 2. Page number (texto muy corto, numérico, en bordes)
        if self._is_page_number(text, signals, context):
            return LayoutBlockType.PAGE_NUMBER

        # 3. Title (primera página, font-size muy grande, centrado)
        if context.page_number == 1 and self._is_title(text, signals, context):
            return LayoutBlockType.TITLE

        # 4. Abstract (léxico explícito)
        if self._is_abstract(text):
            return LayoutBlockType.ABSTRACT

        # 5. Heading/Section (font-size significativamente mayor que el promedio)
        if self._is_heading(signals, context):
            return LayoutBlockType.SECTION

        # 6. Author block (primera página, patrón de nombres + afiliaciones)
        if context.page_number <= 2 and self._is_author_block(text, signals, context):
            return LayoutBlockType.AUTHOR

        # 7. List (bullets o numeración)
        if self._is_list(text):
            return LayoutBlockType.LIST_ITEM

        # 8. Reference entry (patrón [N] o número + autor)
        if self._is_reference_entry(text):
            return LayoutBlockType.REFERENCE_ENTRY

        # 9. Footnote (texto pequeño en la parte inferior)
        if self._is_footnote(signals, context):
            return LayoutBlockType.FOOTNOTE

        # Default
        return LayoutBlockType.PARAGRAPH

    # ─────────────────────────────────────────────────────────────────────────
    # Heurísticas privadas
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _relative_y(bbox: BoundingBox | None, page_height: float) -> float | None:
        if bbox is None or page_height <= 0:
            return None
        center_y = (bbox.y0 + bbox.y1) / 2.0
        return center_y / page_height

    @staticmethod
    def _relative_x(bbox: BoundingBox | None, page_width: float) -> float | None:
        if bbox is None or page_width <= 0:
            return None
        return bbox.center_x / page_width

    @classmethod
    def _is_page_header_or_footer(
        cls, text: str, signals: BlockClassificationSignals, context: PageClassificationContext
    ) -> bool:
        rel_y = cls._relative_y(signals.bbox, context.page_height)
        if rel_y is None:
            return False

        # Zona superior (15%) o inferior (15%)
        in_margin = rel_y < 0.12 or rel_y > 0.88

        # Léxico canónico de headers/footers editoriales
        has_header_lexicon = bool(_HEADER_PATTERNS.search(text))

        # Texto corto en márgenes
        is_short = len(text) < 120

        return in_margin and (has_header_lexicon or (is_short and rel_y < 0.08))

    @classmethod
    def _is_page_number(
        cls, text: str, signals: BlockClassificationSignals, context: PageClassificationContext
    ) -> bool:
        rel_y = cls._relative_y(signals.bbox, context.page_height)
        if rel_y is None:
            return False

        stripped = text.strip()
        is_numeric = stripped.isdigit() and len(stripped) <= 4
        in_footer = rel_y > 0.90

        return is_numeric and in_footer

    @classmethod
    def _is_title(
        cls, text: str, signals: BlockClassificationSignals, context: PageClassificationContext
    ) -> bool:
        if signals.font_size is None:
            return False

        # Font-size al menos 40% mayor que el promedio de la página
        size_ratio = signals.font_size / context.median_font_size if context.median_font_size > 0 else 1.0
        if size_ratio < 1.4:
            return False

        # Texto relativamente corto (títulos no suelen ser párrafos largos)
        if len(text) > 300:
            return False

        # Centrado horizontal (±20% del centro)
        rel_x = cls._relative_x(signals.bbox, context.page_width)
        if rel_x is not None and not (0.3 <= rel_x <= 0.7):
            return False

        # En la mitad superior de la primera página
        rel_y = cls._relative_y(signals.bbox, context.page_height)
        if rel_y is not None and rel_y > 0.5:
            return False

        return True

    @staticmethod
    def _is_abstract(text: str) -> bool:
        stripped = text.strip().lower()
        return stripped.startswith("abstract") and len(text) > 50

    @classmethod
    def _is_heading(
        cls, signals: BlockClassificationSignals, context: PageClassificationContext
    ) -> bool:
        if signals.font_size is None:
            return False

        # Font-size al menos 15% mayor que el promedio
        size_ratio = signals.font_size / context.median_font_size if context.median_font_size > 0 else 1.0
        if size_ratio < 1.15:
            return False

        # Bold ayuda a confirmar
        if signals.is_bold and size_ratio >= 1.1:
            return True

        # Texto corto (headings no son párrafos)
        if len(signals.text.strip()) > 200:
            return False

        return size_ratio >= 1.25

    @classmethod
    def _is_author_block(
        cls, text: str, signals: BlockClassificationSignals, context: PageClassificationContext
    ) -> bool:
        # Después del título, antes del abstract
        rel_y = cls._relative_y(signals.bbox, context.page_height)
        if rel_y is None or rel_y > 0.5:
            return False

        # Font-size cercano al promedio (no es título, no es cuerpo)
        if signals.font_size is None:
            return False
        size_ratio = signals.font_size / context.median_font_size if context.median_font_size > 0 else 1.0
        if size_ratio > 1.3 or size_ratio < 0.8:
            return False

        # Patrón de nombres con comas, "and", o símbolos de afiliación
        has_author_signals = bool(_AUTHOR_AFFILIATION_PATTERN.search(text))
        has_multiple_names = text.count(",") >= 1 or " and " in text.lower()

        return has_author_signals or has_multiple_names

    @staticmethod
    def _is_list(text: str) -> bool:
        lines = [line for line in text.split("\n") if line.strip()]
        if not lines:
            return False

        bullet_lines = sum(1 for line in lines if _LIST_BULLET_PATTERN.match(line))
        number_lines = sum(1 for line in lines if _LIST_NUMBER_PATTERN.match(line))

        # Al menos 50% de las líneas son items de lista
        list_ratio = (bullet_lines + number_lines) / len(lines)
        return list_ratio >= 0.5 and (bullet_lines + number_lines) >= 2

    @staticmethod
    def _is_reference_entry(text: str) -> bool:
        return bool(_REFERENCE_PATTERN.match(text.strip()))

    @classmethod
    def _is_footnote(
        cls, signals: BlockClassificationSignals, context: PageClassificationContext
    ) -> bool:
        if signals.font_size is None:
            return False

        rel_y = cls._relative_y(signals.bbox, context.page_height)
        if rel_y is None:
            return False

        # Font-size significativamente menor que el promedio
        size_ratio = signals.font_size / context.median_font_size if context.median_font_size > 0 else 1.0
        is_small = size_ratio < 0.85

        # En la parte inferior de la página
        is_bottom = rel_y > 0.85

        return is_small and is_bottom