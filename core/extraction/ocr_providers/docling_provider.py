import logging
from pathlib import Path
from typing import Any

from docling.document_converter import DocumentConverter
from docling_core.types.doc.items.text import TextItem
from docling_core.types.doc.labels import DocItemLabel

from core.domain.document import (
    BlockId,
    BlockRelationships,
    BoundingBox,
    DocumentLayout,
    DocumentProfile,
    DomainVersion,
    LayoutBlock,
    LayoutBlockType,
    LayoutMetadata,
    LayoutPage,
    OriginType,
    PageDimensions,
    PageOrientation,
    ProviderMetadata,
    RawContent,
)
from core.extraction.provider import ExtractionCapabilities, ExtractionProvider

logger = logging.getLogger(__name__)


class DoclingProvider(ExtractionProvider):
    _PROVIDER_NAME = "docling"

    _LABEL_MAPPING: dict[DocItemLabel, LayoutBlockType] = {
        DocItemLabel.TITLE: LayoutBlockType.TITLE,
        DocItemLabel.DOCUMENT_INDEX: LayoutBlockType.SECTION,
        DocItemLabel.SECTION_HEADER: LayoutBlockType.SECTION,
        DocItemLabel.PAGE_HEADER: LayoutBlockType.HEADER,
        DocItemLabel.PAGE_FOOTER: LayoutBlockType.FOOTNOTE,
        DocItemLabel.TABLE: LayoutBlockType.TABLE_SIMPLE,
        DocItemLabel.CODE: LayoutBlockType.CODE_BLOCK,
        DocItemLabel.FORMULA: LayoutBlockType.DISPLAY_EQUATION,
        DocItemLabel.LIST_ITEM: LayoutBlockType.LIST_ITEM,
        DocItemLabel.CAPTION: LayoutBlockType.CAPTION,
        DocItemLabel.FOOTNOTE: LayoutBlockType.FOOTNOTE,
        DocItemLabel.PARAGRAPH: LayoutBlockType.PARAGRAPH,
        DocItemLabel.TEXT: LayoutBlockType.PARAGRAPH,
        DocItemLabel.REFERENCE: LayoutBlockType.REFERENCE_ENTRY,
    }

    def __init__(self) -> None:
        self._converter = DocumentConverter()

    @property
    def provider_name(self) -> str:
        return self._PROVIDER_NAME

    @property
    def capabilities(self) -> ExtractionCapabilities:
        return ExtractionCapabilities(
            has_bbox=True,
            has_tables=True,
            has_images=True,
            has_font_info=False,
            has_vector_text=True,
            supports_math=True,
            supports_multicolumn=True,
            supports_rotation=True,
        )

    def extract(self, pdf_path: str) -> DocumentLayout:
        file_path = Path(pdf_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo PDF no encontrado: {file_path}")

        result = self._converter.convert(str(file_path))
        docling_doc = result.document

        return self._map_to_domain(str(file_path), docling_doc)

    def _map_to_domain(self, source_path: str, docling_doc: Any) -> DocumentLayout:
        pages_blocks: dict[int, list[LayoutBlock]] = {}
        pages_dimensions: dict[int, tuple[float, float]] = {}

        if hasattr(docling_doc, "pages"):
            for page_no, page_obj in docling_doc.pages.items():
                pages_dimensions[page_no] = (page_obj.size.width, page_obj.size.height)
                pages_blocks[page_no] = []

        block_counter = 0
        for item, _level in docling_doc.iterate_items():
            prov_data = self._extract_provenance(item)
            if not prov_data:
                continue

            page_no, (x0, y0, x1, y1) = prov_data
            if page_no not in pages_blocks:
                pages_blocks[page_no] = []

            if x1 <= x0:
                x1 = x0 + 0.01
            if y1 <= y0:
                y1 = y0 + 0.01

            label = getattr(item, "label", None)
            if isinstance(label, DocItemLabel) and label in self._LABEL_MAPPING:
                logical_type = self._LABEL_MAPPING[label]
            else:
                logger.warning(
                    "Etiqueta de Docling no mapeada o nula: %s. Degradando a PARAGRAPH.", label
                )
                logical_type = LayoutBlockType.PARAGRAPH

            text_content = getattr(item, "text", "").strip() if isinstance(item, TextItem) else ""

            block_counter += 1
            block = LayoutBlock(
                block_id=BlockId(value=f"docling_p{page_no}_b{block_counter}"),
                logical_type=logical_type,
                content=RawContent(
                    original=text_content,
                    normalized=text_content,
                    cleaned=text_content,
                ),
                bbox=BoundingBox(x0=x0, y0=y0, x1=x1, y1=y1),
                metadata=LayoutMetadata(
                    provider=ProviderMetadata(
                        provider_name=self._PROVIDER_NAME,
                        native_block_index=block_counter,
                    )
                ),
                relationships=BlockRelationships(),
                versioning=DomainVersion(version=1, origin=OriginType.EXTRACTOR),
            )
            pages_blocks[page_no].append(block)

        pages: list[LayoutPage] = []
        sorted_page_numbers = sorted(pages_blocks.keys())

        for page_no in sorted_page_numbers:
            width, height = pages_dimensions.get(page_no, (612.0, 792.0))
            orientation = (
                PageOrientation.PORTRAIT if height >= width else PageOrientation.LANDSCAPE
            )

            pages.append(
                LayoutPage(
                    page_number=page_no,
                    dimensions=PageDimensions(
                        width=width,
                        height=height,
                        orientation=orientation,
                    ),
                    blocks=pages_blocks[page_no],
                )
            )

        total_pages = len(pages) if pages else 1

        return DocumentLayout(
            source_path=source_path,
            total_pages=total_pages,
            profile=DocumentProfile(),
            pages=pages,
        )

    @staticmethod
    def _extract_provenance(item: Any) -> tuple[int, tuple[float, float, float, float]] | None:
        provs = getattr(item, "prov", None)
        if not provs:
            return None

        try:
            first = provs[0]
        except (IndexError, TypeError):
            return None

        bbox = getattr(first, "bbox", None)
        if not bbox:
            return None

        return (
            getattr(first, "page_no", 1),
            (
                getattr(bbox, "l", 0.0),
                getattr(bbox, "t", 0.0),
                getattr(bbox, "r", 0.0),
                getattr(bbox, "b", 0.0),
            ),
        )