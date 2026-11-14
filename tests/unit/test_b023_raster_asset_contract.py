"""B02.3: immutable raster storage and image coverage, no real PDF/producers."""
from hashlib import sha256
from pathlib import Path

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ImagePayload
from core.chunking.manifest_contract import ChunkPlan, validate_chunk_coverage
from infra.extraction.providers.pymupdf_image_assets import persist_png_asset
from infra.extraction.providers.pymupdf_integrity import (
    UnrepresentedPdfContentError, validate_pymupdf_page_coverage,
)

PNG = b"\x89PNG\r\n\x1a\n" + b"synthetic payload"


@pytest.mark.unit
def test_png_is_published_once_and_canonical(tmp_path):
    ref = persist_png_asset(PNG, source_root=tmp_path)
    assert ref == "data/assets/" + sha256(PNG).hexdigest() + ".png"
    assert persist_png_asset(PNG, source_root=tmp_path) == ref
    assert (tmp_path / ref).read_bytes() == PNG
    assert list((tmp_path / "data" / "assets").iterdir()) == [tmp_path / ref]


@pytest.mark.unit
def test_invalid_png_rejected_before_publication(tmp_path):
    with pytest.raises(ValueError, match="B023_IMAGE_NOT_PNG"):
        persist_png_asset(b"not-png", source_root=tmp_path)
    assert not (tmp_path / "data").exists()


@pytest.mark.unit
def test_existing_asset_cannot_be_overwritten(tmp_path):
    ref = persist_png_asset(PNG, source_root=tmp_path)
    (tmp_path / ref).write_bytes(b"tamper")
    with pytest.raises(ValueError, match="B023_IMAGE_EXISTING_ASSET_CONFLICT"):
        persist_png_asset(PNG, source_root=tmp_path)
    assert (tmp_path / ref).read_bytes() == b"tamper"


@pytest.mark.unit
def test_directory_symlink_rejected(tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    try:
        (tmp_path / "data").symlink_to(other, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink unavailable to test user")
    with pytest.raises(ValueError, match="B023_IMAGE_ASSET_DIRECTORY_SYMLINK"):
        persist_png_asset(PNG, source_root=tmp_path)


@pytest.mark.unit
def test_image_representability_is_explicitly_opt_in():
    image = [{"type": 1, "number": 5}]
    with pytest.raises(UnrepresentedPdfContentError, match="B02_UNREPRESENTED_IMAGE_BLOCK"):
        validate_pymupdf_page_coverage(image, page_number=1, has_vector_drawings=False)
    validate_pymupdf_page_coverage(
        image, page_number=1, has_vector_drawings=False, allow_image_blocks=True,
    )
    with pytest.raises(UnrepresentedPdfContentError, match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        validate_pymupdf_page_coverage(
            image, page_number=1, has_vector_drawings=True, allow_image_blocks=True,
        )


@pytest.mark.unit
def test_image_node_text_content_is_canonical_asset_reference():
    ref = "data/assets/" + sha256(PNG).hexdigest() + ".png"
    node = ASTNode(
        node_id="p1_b2", sequence_id=1, node_type=ContentNodeType.IMAGE,
        strategy=TranslationStrategy.PASSTHROUGH,
        payload=ImagePayload(asset_path=ref),
    )
    assert node.text_content == ref
    assert ASTNode.model_validate_json(node.model_dump_json()).text_content == ref


@pytest.mark.unit
def test_missing_asset_reference_fails_at_chunk_plan_gate():
    node = ASTNode(
        node_id="p1_b2", sequence_id=1, node_type=ContentNodeType.IMAGE,
        strategy=TranslationStrategy.PASSTHROUGH, payload=ImagePayload(),
    )
    with pytest.raises(ValueError, match="G3_IMAGE_ASSET_REFERENCE_MISSING"):
        validate_chunk_coverage([node], [])
