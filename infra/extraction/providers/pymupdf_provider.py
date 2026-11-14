import os
import re
from pathlib import Path
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
from core.execution.exceptions import LayoutRecoveryError
from infra.extraction.providers.pymupdf_integrity import (
    UnrepresentedPdfContentError, validate_pymupdf_page_coverage,
)
from infra.extraction.providers.pymupdf_image_assets import persist_png_asset
from infra.extraction.providers.pymupdf_math_visual import classify_math_font_block, render_math_visual_png
import statistics

@dataclass(frozen=True, slots=True)
class _PhysicalBlock:
    """DTO interno privado para aislar la inspección física del mapeo de dominio."""
    native_index: int
    raw_text: str
    bbox: tuple[float, float, float, float]
    lines: list[dict]
    rotation: float
    native_type: int = 0




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
            total_pages = len(doc)
            for page_idx in range(total_pages):
                page = doc[page_idx]
                try:
                    layout_page = self._build_page(
                        page,
                        page_number=page_idx + 1,
                        total_pages=total_pages,
                    )
                except UnrepresentedPdfContentError as exc:
                    raise LayoutRecoveryError(
                        message=str(exc), provider_name="pymupdf", pdf_path=pdf_path
                    ) from exc
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
        validate_pymupdf_page_coverage(
            raw_blocks,
            page_number=page_number,
            has_vector_drawings=bool(page.get_drawings()),
            allow_image_blocks=self._write_images,
        )

        # Preserve native block order, including images. No invisible IMAGE nodes.
        physical_blocks: list[_PhysicalBlock] = []
        for block_index, raw_b in enumerate(raw_blocks):
            if raw_b.get("type") == 1:
                png = self._image_block_to_png(raw_b, page_number=page_number)
                reference = persist_png_asset(
                    png, source_root=Path(os.getenv("APP_ROOT") or ".")
                )
                phys = _PhysicalBlock(
                    native_index=int(raw_b.get("number", block_index)),
                    raw_text=reference,
                    bbox=tuple(raw_b.get("bbox", ())),
                    lines=[], rotation=rotation, native_type=1,
                )
            else:
                math_class = classify_math_font_block(raw_b)
                if math_class == "mixed":
                    raise UnrepresentedPdfContentError(
                        f"B025_MIXED_MATH_FONT_BLOCK: page={page_number} "
                        f"block={raw_b.get('number', block_index)}; "
                        "no se puede separar matemática y prosa sin alterar lectura"
                    )
                if math_class == "visual":
                    if not self._write_images:
                        raise UnrepresentedPdfContentError(
                            f"B025_MATH_VISUAL_DISABLED: page={page_number}"
                        )
                    png = render_math_visual_png(page, raw_b, page_number=page_number)
                    reference = persist_png_asset(
                        png, source_root=Path(os.getenv("APP_ROOT") or ".")
                    )
                    phys = _PhysicalBlock(
                        native_index=int(raw_b.get("number", block_index)),
                        raw_text=reference,
                        bbox=tuple(raw_b.get("bbox", ())),
                        lines=[], rotation=rotation, native_type=1,
                    )
                else:
                    phys = self._extract_physical_block(
                        raw_block=raw_b,
                        default_idx=block_index,
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
            logical_type = (
                LayoutBlockType.IMAGE if phys.native_type == 1
                else self._classifier.classify(signals, page_context)
            )

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

    @staticmethod
    def _image_block_to_png(raw_block: dict, *, page_number: int) -> bytes:
        """Decode an embedded raster; do not synthesize or OCR image contents.

        Unsupported masks and colour spaces fail rather than dropping detail.
        """
        image = raw_block.get("image")
        if raw_block.get("mask"):
            raise UnrepresentedPdfContentError(
                f"B023_IMAGE_ALPHA_MASK_UNSUPPORTED: page={page_number}"
            )
        if not isinstance(image, bytes) or not image:
            raise UnrepresentedPdfContentError(
                f"B023_IMAGE_BYTES_MISSING: page={page_number}"
            )
        try:
            pixmap = fitz.Pixmap(image)
            if pixmap.colorspace is None or pixmap.colorspace.n not in (1, 3):
                raise ValueError("unsupported colorspace")
            return pixmap.tobytes("png")
        except Exception as exc:
            raise UnrepresentedPdfContentError(
                f"B023_IMAGE_DECODE_UNSUPPORTED: page={page_number}"
            ) from exc

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
            if phys.native_type != 0:
                continue  # asset references are not textual typography samples.
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