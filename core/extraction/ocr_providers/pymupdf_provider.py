import re
from dataclasses import dataclass
from typing import cast, Any, List, Dict, Tuple, Optional
from collections import defaultdict
import fitz  # PyMuPDF

from core.domain.document import (
    DocumentLayout,
    DocumentProfile,
    LayoutPage,
    PageDimensions,
    PageOrientation,
    LayoutBlock,
    LayoutBlockType,
    BlockId,
    RawContent,
    BoundingBox,
    LayoutMetadata,
    TypographyMetadata,
    SpatialMetadata,
    ConfidenceMetadata,
    ProviderMetadata,
    BlockRelationships,
    DomainVersion,
    OriginType,
)
from core.extraction.provider import ExtractionProvider, ExtractionCapabilities
from core.layout.classification import LayoutClassifier, BlockClassificationSignals, PageClassificationContext
import statistics

@dataclass(frozen=True, slots=True)
class _PhysicalBlock:
    """DTO interno privado para aislar la inspección física del mapeo de dominio."""
    native_index: int
    raw_text: str
    bbox: tuple[float, float, float, float]
    lines: list[dict]
    rotation: float




class PyMuPDFProvider(ExtractionProvider):
    def __init__(
        self,
        classifier: LayoutClassifier,
        write_images: bool = True,
    ) -> None:
        self._classifier = classifier
        self._write_images = write_images
        self._capabilities = ExtractionCapabilities(
            has_bbox=True,
            has_tables=False,
            has_images=False,
            has_font_info=True,
            has_vector_text=True,
            supports_math=False,
            supports_multicolumn=False,
            supports_rotation=False,
        )

    @property
    def capabilities(self) -> ExtractionCapabilities:
        return self._capabilities

    def extract(self, pdf_path: str) -> DocumentLayout:
        pages: List[LayoutPage] = []

        with fitz.open(pdf_path) as doc:
            total_pages = len(doc)
            for page_idx in range(total_pages):
                page = doc[page_idx]
                layout_page = self._build_page(
                    page,
                    page_number=page_idx + 1,
                    total_pages=total_pages,
                )
                pages.append(layout_page)

        profile = DocumentProfile()

        return DocumentLayout(
            source_path=pdf_path,
            total_pages=len(pages),
            profile=profile,
            pages=pages,
        )
    # =========================================================================
    # Métodos Privados de Extracción Física
    # =========================================================================

    def _build_page(self, page: fitz.Page, page_number: int, total_pages: int) -> LayoutPage:
        rect = page.rect
        rotation = float(page.rotation % 360)

        if rotation in (90.0, 270.0):
            width, height = float(rect.height), float(rect.width)
        else:
            width, height = float(rect.width), float(rect.height)

        orientation = (
            PageOrientation.PORTRAIT
            if height >= width
            else PageOrientation.LANDSCAPE
        )
        dimensions = PageDimensions(
            width=width, height=height, orientation=orientation
        )

        page_dict = cast(dict[str, Any], page.get_text("dict"))
        raw_blocks = page_dict.get("blocks", [])

        # Fase 1: Extraer todos los bloques físicos
        physical_blocks: list[_PhysicalBlock] = []
        for raw_b in raw_blocks:
            if raw_b.get("type") != 0:
                continue
            phys = self._extract_physical_block(
                raw_block=raw_b,
                default_idx=len(physical_blocks),
                rotation=rotation,
            )
            physical_blocks.append(phys)

        # Fase 2: Calcular contexto estadístico de la página
        page_context = self._build_page_context(
            physical_blocks, page_number, total_pages, height, width
        )

        # Fase 3: Clasificar y construir LayoutBlocks
        blocks: List[LayoutBlock] = []
        for idx, phys in enumerate(physical_blocks):
            typography = self._extract_dominant_typography(phys.lines)
            bbox = self._build_bbox(phys.bbox)

            signals = BlockClassificationSignals(
                text=phys.raw_text,
                font_name=typography.font_name,
                font_size=typography.font_size,
                is_bold=typography.is_bold,
                is_italic=typography.is_italic,
                bbox=bbox,
                reading_order=idx,
            )

            # Clasificar ANTES de construir el Aggregate
            logical_type = self._classifier.classify(signals, page_context)

            block = self._build_layout_block(
                phys_block=phys,
                typography=typography,
                logical_type=logical_type,
                bbox=bbox,
                page_number=page_number,
                reading_order=idx,
            )

            if block is not None:
                blocks.append(block)

        return LayoutPage(
            page_number=page_number,
            dimensions=dimensions,
            blocks=blocks,
        )

    def _extract_physical_block(
        self, raw_block: dict, default_idx: int, rotation: float
    ) -> _PhysicalBlock:
        native_idx = raw_block.get("number", default_idx)
        bbox_tuple = raw_block.get("bbox", (0.0, 0.0, 0.0, 0.0))
        lines = raw_block.get("lines", [])
        
        line_texts: List[str] = []
        for line in lines:
            span_text = "".join(span.get("text", "") for span in line.get("spans", []))
            if span_text:
                line_texts.append(span_text)

        raw_text = "\n".join(line_texts)

        return _PhysicalBlock(
            native_index=native_idx,
            raw_text=raw_text,
            bbox=bbox_tuple,
            lines=lines,
            rotation=rotation,
        )

    def _build_layout_block(
        self,
        phys_block: _PhysicalBlock,
        typography: TypographyMetadata,
        logical_type: LayoutBlockType,
        bbox: BoundingBox,
        page_number: int,
        reading_order: int,
    ) -> Optional[LayoutBlock]:
        content = self._extract_raw_content(phys_block.raw_text)

        if not content.cleaned:
            return None

        spatial = SpatialMetadata(
            reading_order=reading_order,
            column_index=0,
            rotation=phys_block.rotation,
        )
        confidence = ConfidenceMetadata(
            ocr=1.0,
            layout_classification=1.0,
        )
        provider_meta = ProviderMetadata(
            provider_name="pymupdf",
            native_block_index=phys_block.native_index,
        )

        metadata = LayoutMetadata(
            typography=typography,
            spatial=spatial,
            confidence=confidence,
            provider=provider_meta,
        )

        block_id = BlockId(value=f"p{page_number}_b{phys_block.native_index}")
        relationships = BlockRelationships()
        versioning = DomainVersion(version=1, origin=OriginType.EXTRACTOR)

        # El Aggregate nace consistente: logical_type ya está resuelto
        return LayoutBlock(
            block_id=block_id,
            logical_type=logical_type,
            content=content,
            bbox=bbox,
            metadata=metadata,
            relationships=relationships,
            versioning=versioning,
        )

    def _extract_raw_content(self, raw_text: str) -> RawContent:
        normalized_text = raw_text.strip()
        cleaned_text = re.sub(r"\s+", " ", normalized_text)

        return RawContent(
            original=raw_text,
            normalized=normalized_text,
            cleaned=cleaned_text,
        )

    def _extract_dominant_typography(self, lines: list[dict]) -> TypographyMetadata:
        style_weights: Dict[Tuple[str, float, bool, bool], int] = defaultdict(int)

        for line in lines:
            for span in line.get("spans", []):
                text = span.get("text", "")
                visible_chars = len(re.sub(r"\s", "", text))
                if visible_chars == 0:
                    continue

                font_name = span.get("font", "Unknown")
                font_size = round(float(span.get("size", 0.0)), 1)
                flags = span.get("flags", 0)

                is_bold = bool(flags & 16) or ("bold" in font_name.lower())
                is_italic = bool(flags & 2) or (
                    "italic" in font_name.lower() or "oblique" in font_name.lower()
                )

                style_key = (font_name, font_size, is_bold, is_italic)
                style_weights[style_key] += visible_chars

        if not style_weights:
            return TypographyMetadata()

        dominant_key = max(style_weights, key=lambda k: style_weights[k])

        return TypographyMetadata(
            font_name=dominant_key[0],
            font_size=dominant_key[1],
            is_bold=dominant_key[2],
            is_italic=dominant_key[3],
        )

    def _build_bbox(self, raw_bbox: tuple) -> BoundingBox:
        x0, y0, x1, y1 = (
            float(raw_bbox[0]),
            float(raw_bbox[1]),
            float(raw_bbox[2]),
            float(raw_bbox[3]),
        )

        if x1 <= x0 or y1 <= y0:
            raise ValueError(
                f"Geometría degenerada detectada por PyMuPDF: [{x0}, {y0}, {x1}, {y1}]"
            )

        return BoundingBox(x0=x0, y0=y0, x1=x1, y1=y1, is_normalized=False)

    def _build_page_context(
        self,
        physical_blocks: list[_PhysicalBlock],
        page_number: int,
        total_pages: int,
        page_height: float,
        page_width: float,
    ) -> PageClassificationContext:
        """Calcula estadísticas tipográficas de la página para clasificación relativa."""
        font_sizes: list[float] = []

        for phys in physical_blocks:
            typo = self._extract_dominant_typography(phys.lines)
            if typo.font_size is not None and typo.font_size > 0:
                # Ponderar por cantidad de caracteres visibles
                visible_chars = len(re.sub(r"\s", "", phys.raw_text))
                font_sizes.extend([typo.font_size] * max(1, visible_chars))

        if font_sizes:
            median_size = float(statistics.median(font_sizes))
            # Dominant = moda (tamaño más frecuente)
            dominant_size = float(statistics.mode(font_sizes))
        else:
            median_size = 12.0
            dominant_size = 12.0

        return PageClassificationContext(
            median_font_size=median_size,
            dominant_font_size=dominant_size,
            page_number=page_number,
            total_pages=total_pages,
            block_count=len(physical_blocks),
            page_height=page_height,
            page_width=page_width,
        )