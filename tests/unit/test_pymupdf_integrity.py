"""B02: la guardia es determinista; no necesita PDF, Docker ni proveedor."""

import pytest

from infra.extraction.providers.pymupdf_integrity import (
    UnrepresentedPdfContentError,
    validate_pymupdf_page_coverage,
)


@pytest.mark.unit
def test_text_without_observed_unsupported_content_is_not_blocked():
    validate_pymupdf_page_coverage(
        [{"type": 0, "number": 3, "lines": [{"spans": [{"text": "E = mc²; α + β"}]}]}],
        page_number=2,
        has_vector_drawings=False,
    )


@pytest.mark.unit
@pytest.mark.parametrize("block_type,category", [(1, "IMAGE"), (2, "UNSUPPORTED"), (None, "UNSUPPORTED")])
def test_nontext_blocks_never_disappear_silently(block_type, category):
    with pytest.raises(UnrepresentedPdfContentError, match=f"B02_UNREPRESENTED_{category}_BLOCK") as exc:
        validate_pymupdf_page_coverage(
            [{"type": block_type, "number": 7}], page_number=4, has_vector_drawings=False
        )
    assert "page=4" in str(exc.value)
    assert "block=7" in str(exc.value)


@pytest.mark.unit
@pytest.mark.parametrize("glyph,codepoint", [("\ufffd", "U+FFFD"), ("\uffff", "U+FFFF")])
def test_unmapped_glyph_signals_are_distinguished(glyph, codepoint):
    blocks = [{"type": 0, "number": 9, "lines": [{"spans": [{"text": "x " + glyph + " y"}]}]}]
    with pytest.raises(UnrepresentedPdfContentError, match="B02_UNMAPPED_GLYPH") as exc:
        validate_pymupdf_page_coverage(blocks, page_number=1, has_vector_drawings=False)
    assert codepoint in str(exc.value)
    assert "block=9" in str(exc.value)


@pytest.mark.unit
def test_vector_drawings_fail_closed_even_if_all_blocks_are_text():
    with pytest.raises(UnrepresentedPdfContentError, match="B02_UNREPRESENTED_VECTOR_DRAWING"):
        validate_pymupdf_page_coverage(
            [{"type": 0, "lines": [{"spans": [{"text": "Tabla 1"}]}]}],
            page_number=3,
            has_vector_drawings=True,
        )


@pytest.mark.unit
def test_empty_page_is_not_misdiagnosed_as_vector_loss():
    validate_pymupdf_page_coverage([], page_number=1, has_vector_drawings=False)
