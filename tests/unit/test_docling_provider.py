from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from docling_core.types.doc.items.text import TextItem
from docling_core.types.doc.labels import DocItemLabel

from core.domain.document import LayoutBlockType
from infra.extraction.providers.docling_provider import DoclingProvider


def test_docling_provider_name():
    provider = DoclingProvider()
    assert provider.provider_name == "docling"


def test_docling_provider_file_not_found():
    provider = DoclingProvider()
    with pytest.raises(FileNotFoundError):
        provider.extract("non_existent_file.pdf")


@patch("infra.extraction.providers.docling_provider.DocumentConverter")
def test_docling_provider_domain_mapping(mock_converter_cls, tmp_path: Path):
    dummy_pdf = tmp_path / "test.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 dummy content")

    mock_page = MagicMock()
    mock_page.size.width = 612.0
    mock_page.size.height = 792.0

    mock_bbox = MagicMock()
    mock_bbox.l = 10.5
    mock_bbox.t = 20.25
    mock_bbox.r = 100.123
    mock_bbox.b = 200.456

    mock_prov = MagicMock()
    mock_prov.page_no = 1
    mock_prov.bbox = mock_bbox

    mock_title_item = MagicMock(spec=TextItem)
    mock_title_item.label = DocItemLabel.TITLE
    mock_title_item.text = "Document Title"
    mock_title_item.prov = [mock_prov]

    mock_doc = MagicMock()
    mock_doc.pages = {1: mock_page}
    mock_doc.iterate_items.return_value = [(mock_title_item, 0)]

    mock_result = MagicMock()
    mock_result.document = mock_doc

    mock_converter_inst = MagicMock()
    mock_converter_inst.convert.return_value = mock_result
    mock_converter_cls.return_value = mock_converter_inst

    provider = DoclingProvider()
    layout = provider.extract(str(dummy_pdf))

    assert layout.source_path == str(dummy_pdf)
    assert layout.total_pages == 1
    assert len(layout.pages) == 1

    page = layout.pages[0]
    assert page.page_number == 1
    assert page.dimensions.width == 612.0
    assert page.dimensions.height == 792.0
    assert len(page.blocks) == 1

    block = page.blocks[0]
    assert block.logical_type == LayoutBlockType.TITLE
    assert block.content.original == "Document Title"
    
    # Afirmaciones para type-checking de Pyright
    assert block.bbox is not None
    assert block.bbox.x0 == 10.5
    assert block.bbox.y0 == 20.25

    assert block.metadata.provider is not None
    assert block.metadata.provider.provider_name == "docling"
