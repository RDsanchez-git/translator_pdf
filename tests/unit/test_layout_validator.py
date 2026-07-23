from typing import Optional
import pytest
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
    RawContent,
)
from core.layout.validator import DocumentLayoutValidator


@pytest.fixture
def validator() -> DocumentLayoutValidator:
    return DocumentLayoutValidator()


def make_content(text: str = "sample") -> RawContent:
    return RawContent(original=text, normalized=text, cleaned=text)


def make_version() -> DomainVersion:
    return DomainVersion(version=1, origin=OriginType.EXTRACTOR)


def make_relationships() -> BlockRelationships:
    return BlockRelationships()


def make_metadata() -> LayoutMetadata:
    return LayoutMetadata()


def make_block(
    block_id: str,
    logical_type: LayoutBlockType = LayoutBlockType.PARAGRAPH,
    bbox: Optional[BoundingBox] = None,
) -> LayoutBlock:
    return LayoutBlock(
        block_id=BlockId(value=block_id),
        logical_type=logical_type,
        content=make_content(),
        bbox=bbox,
        metadata=make_metadata(),
        relationships=make_relationships(),
        versioning=make_version(),
    )


def make_page(page_number: int, blocks: Optional[list[LayoutBlock]] = None) -> LayoutPage:
    return LayoutPage(
        page_number=page_number,
        dimensions=PageDimensions(width=612.0, height=792.0, orientation=PageOrientation.PORTRAIT),
        blocks=blocks or [],
    )


def make_layout(pages: list[LayoutPage]) -> DocumentLayout:
    return DocumentLayout(
        source_path="test.pdf",
        total_pages=max(len(pages), 1),
        profile=DocumentProfile(),
        pages=pages,
    )


def test_valid_layout_passes_validation(validator: DocumentLayoutValidator) -> None:
    block = make_block("blk_01", bbox=BoundingBox(x0=10.0, y0=10.0, x1=100.0, y1=50.0))
    page = make_page(1, blocks=[block])
    layout = make_layout([page])
    report = validator.validate(layout)

    assert report.is_valid is True
    assert len(report.errors) == 0


def test_empty_pages_fails_validation(validator: DocumentLayoutValidator) -> None:
    layout = make_layout([])
    layout = layout.model_copy(update={"pages": []})
    report = validator.validate(layout)

    assert report.is_valid is False
    assert "El DocumentLayout no contiene páginas." in report.errors[0]


def test_invalid_page_number_fails(validator: DocumentLayoutValidator) -> None:
    page = LayoutPage.model_construct(
        page_number=0,
        dimensions=PageDimensions(width=612.0, height=792.0, orientation=PageOrientation.PORTRAIT),
        blocks=[],
    )
    layout = make_layout([page])
    report = validator.validate(layout)

    assert report.is_valid is False
    assert "Debe ser >= 1" in report.errors[0]


def test_duplicate_page_number_fails(validator: DocumentLayoutValidator) -> None:
    page1 = make_page(1)
    page2 = make_page(1)
    layout = make_layout([page1, page2])
    report = validator.validate(layout)

    assert report.is_valid is False
    assert any("Número de página duplicado" in err for err in report.errors)


def test_non_monotonic_page_sequence_fails(validator: DocumentLayoutValidator) -> None:
    page1 = make_page(1)
    page3 = make_page(3)
    page2 = make_page(2)
    layout = make_layout([page1, page3, page2])
    report = validator.validate(layout)

    assert report.is_valid is False
    assert any("Secuencia de páginas no monótona" in err for err in report.errors)


def test_duplicate_block_id_across_pages_fails(validator: DocumentLayoutValidator) -> None:
    block1 = make_block("dup_id", logical_type=LayoutBlockType.PARAGRAPH)
    block2 = make_block("dup_id", logical_type=LayoutBlockType.TITLE)

    page1 = make_page(1, blocks=[block1])
    page2 = make_page(2, blocks=[block2])
    layout = make_layout([page1, page2])
    report = validator.validate(layout)

    assert report.is_valid is False
    assert any("Colisión de BlockId duplicado" in err for err in report.errors)


def test_none_bbox_is_valid_for_neutral_provider(validator: DocumentLayoutValidator) -> None:
    block = make_block("no_bbox_blk", bbox=None)
    page = make_page(1, blocks=[block])
    layout = make_layout([page])
    report = validator.validate(layout)

    assert report.is_valid is True


def test_invalid_bbox_bounds_fails(validator: DocumentLayoutValidator) -> None:
    # 1. Bypasseamos la validación de Pydantic en BoundingBox y LayoutBlock para simular
    #    un bloque corrupto proveniente de un parser externo.
    invalid_bbox = BoundingBox.model_construct(
        x0=100.0, y0=10.0, x1=10.0, y1=50.0, is_normalized=False
    )
    block = LayoutBlock.model_construct(
        block_id=BlockId(value="invalid_bbox_blk"),
        logical_type=LayoutBlockType.PARAGRAPH,
        content=make_content(),
        bbox=invalid_bbox,
        metadata=make_metadata(),
        relationships=make_relationships(),
        versioning=make_version(),
    )
    page = make_page(1, blocks=[block])
    layout = make_layout([page])

    # 2. El validador de dominio debe detectar la falla
    report = validator.validate(layout)

    assert report.is_valid is False
    assert any("BoundingBox" in err for err in report.errors)