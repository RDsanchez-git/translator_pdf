"""B02.5: pure font risk and bounded physical crop; no providers or Docker."""
from pathlib import Path
import fitz
import pytest
from infra.extraction.providers.pymupdf_math_visual import (
    classify_math_font_block, render_math_visual_png,
)


def block(*font_text):
    return {"type": 0, "lines": [{"spans": [{"font": f, "text": text} for f, text in font_text]}]}


def test_ordinary_prose_not_rasterized():
    assert classify_math_font_block(block(("Helvetica", "Math variables x, y."))) == "none"


def test_generic_stix_font_not_rasterized():
    assert classify_math_font_block(block(("STIXGeneral", "Methods and conclusions"))) == "none"


@pytest.mark.parametrize("font", ["Symbol", "CMMI10", "CMSY8", "CMEX10", "Cambria Math", "STIX Two Math", "Asana Math", "MathJax_Main"])
def test_dedicated_math_font_is_visual_candidate(font):
    assert classify_math_font_block(block((font, "x+y"))) == "visual"


def test_mixed_math_prose_is_rejected_by_classifier():
    assert classify_math_font_block(block(("Helvetica", "The value is "), ("Symbol", "a"))) == "mixed"


def test_whitespace_span_is_ignored():
    assert classify_math_font_block(block(("Helvetica", "  "), ("Symbol", "ab"))) == "visual"


def test_nontext_block_ignored():
    assert classify_math_font_block({"type": 1, "image": b"data"}) == "none"


def test_formula_crop_is_valid_png_and_deterministic(tmp_path):
    pdf=tmp_path/"math.pdf"
    with fitz.open() as doc:
        p=doc.new_page()
        p.insert_text((65, 110), "abgDS", fontname="symb", fontsize=16)
        doc.save(pdf)
    with fitz.open(pdf) as doc:
        p=doc[0]
        b=p.get_text("dict")["blocks"][0]
        assert classify_math_font_block(b) == "visual"
        one=render_math_visual_png(p,b,page_number=1)
        two=render_math_visual_png(p,b,page_number=1)
    assert one == two and one.startswith(b"\x89PNG\r\n\x1a\n")
    pix=fitz.Pixmap(one)
    assert pix.width>20 and pix.height>20


def test_invalid_or_oversized_region_fails(tmp_path):
    with fitz.open() as doc:
        p=doc.new_page(width=200,height=200)
        for bbox in [(0,0,0,0), (-5,10,30,40), (0,0,201,190), (0,0,199,199), (1,float("nan"),5,8)]:
            if bbox == (0,0,199,199):
                assert render_math_visual_png(p,{"bbox":bbox},page_number=1).startswith(b"\x89PNG")
            else:
                with pytest.raises((ValueError,TypeError), match="B025_INVALID_MATH_BBOX"):
                    render_math_visual_png(p,{"bbox":bbox},page_number=1)
