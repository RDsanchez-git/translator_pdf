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


@dataclass(frozen=True, slots=True)
class _PhysicalBlock:
    """DTO interno privado para aislar la inspección física del mapeo de dominio."""
    native_index: int
    raw_text: str
    bbox: tuple[float, float, float, float]
    lines: list[dict]
    rotation: float


class PyMuPDFProvider(ExtractionProvider):
    """
    Capa de Reconstrucción Física (Physical Reconstruction Layer).
    
    Responsabilidad única: Materializar la representación física del documento 
    respetando las invariantes del Aggregate Root, de forma totalmente agnóstica a la semántica.
    """

    def __init__(self, write_images: bool = True) -> None:
        self._write_images = write_images
        self._capabilities = ExtractionCapabilities(
            has_bbox=True,
            has_tables=False,
            has_images=self._write_images,
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
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                layout_page = self._build_page(page, page_number=page_idx + 1)
                pages.append(layout_page)

        # Profile con valores base del dominio; la clasificación pertenece a DocumentProfiler
        profile = DocumentProfile()

        return DocumentLayout(
            source_path=pdf_path,
            total_pages=len(pages),  # Si len(pages) == 0, el Aggregate Root elevará la infracción ge=1
            profile=profile,
            pages=pages,
        )

    # =========================================================================
    # Métodos Privados de Extracción Física
    # =========================================================================

    def _build_page(self, page: fitz.Page, page_number: int) -> LayoutPage:
        rect = page.rect
        rotation = float(page.rotation % 360)
        
        # Orientación considerando el Viewport rotado
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

        # Hacemos el cast explícito a dict[str, Any] para satisfacer a Pyright/Pylance
        page_dict = cast(dict[str, Any], page.get_text("dict"))
        raw_blocks = page_dict.get("blocks", [])

        blocks: List[LayoutBlock] = []
        valid_counter = 0

        for raw_b in raw_blocks:
            # Tipo 0 indica bloque de texto vectorial en PyMuPDF
            if raw_b.get("type") != 0:
                continue

            physical_block = self._extract_physical_block(
                raw_block=raw_b, 
                default_idx=valid_counter, 
                rotation=rotation
            )
            block = self._map_to_layout_block(
                phys_block=physical_block,
                page_number=page_number,
                reading_order=valid_counter,
            )

            if block is not None:
                blocks.append(block)
                valid_counter += 1

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

    def _map_to_layout_block(
        self,
        phys_block: _PhysicalBlock,
        page_number: int,
        reading_order: int,
    ) -> Optional[LayoutBlock]:
        content = self._extract_raw_content(phys_block.raw_text)

        if not content.cleaned:
            return None

        bbox = self._build_bbox(phys_block.bbox)
        typography = self._extract_dominant_typography(phys_block.lines)

        spatial = SpatialMetadata(
            reading_order=reading_order,
            column_index=0,  # Alineado a la definición del dominio (0 = Única/Izquierda)
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

        return LayoutBlock(
            block_id=block_id,
            logical_type=LayoutBlockType.UNKNOWN,
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