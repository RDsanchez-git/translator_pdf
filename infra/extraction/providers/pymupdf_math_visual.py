"""B02.5: conservative visual preservation of *identified* math-font blocks.

The PDF image is evidence of the original glyph appearance, not typed/semantic
LaTeX. No claim of general formula detection, layout preservation, or recovery
of source glyph Unicode. Mixed math/prose is deliberately not rasterized: its
text must remain translatable, and no safe segmentation exists yet.
"""
from __future__ import annotations

import re
from typing import Any, Literal, Mapping

import fitz


MathFontClassification = Literal["none", "visual", "mixed"]

# Target dedicated math-font families only. Generic Times/Helvetica/STIXGeneral
# are excluded: selecting them would rasterize ordinary scientific prose.
_MATH_FONT_RE = re.compile(
    r"(?:^symbol(?:mt)?$|cm(?:mi|sy|ex|msy|mib|bsy)\d*|"
    r"(?:cambria|asana|xits|latin[ -]?modern|stix(?:[ -]?two)?)\s*math|"
    r"mathjax|mt(?:mi|sy|ex)\d*|euclid(?:math)?|mathematica)",
    flags=re.IGNORECASE,
)


def classify_math_font_block(block: Mapping[str, Any]) -> MathFontClassification:
    """Inspect extracted font metadata without pretending to parse an equation.

    Exactly one native text block is the possible visual replacement unit.
    Dedicated math fonts mixed with text fonts are *not* a safe visual unit:
    replacing the full block would also prevent normal prose translation.
    """
    if block.get("type") != 0:
        return "none"
    spans = [
        span
        for line in block.get("lines", ())
        for span in line.get("spans", ())
        if isinstance(span.get("text"), str) and span["text"].strip()
    ]
    if not spans:
        return "none"
    flags = [bool(_MATH_FONT_RE.search(str(span.get("font", "")))) for span in spans]
    if not any(flags):
        return "none"
    return "visual" if all(flags) else "mixed"


def render_math_visual_png(
    page: fitz.Page, block: Mapping[str, Any], *, page_number: int,
) -> bytes:
    """Rasterize the original PDF glyphs in a bounded, non-lossy-to-meaning crop.

    Crop is deliberately only an approximate visual fallback; Unicode/math
    semantics and LaTeX structure are not recovered. The resulting PNG is
    content-addressed and staged by the existing B02.3→G5 image contract.
    """
    coords = block.get("bbox")
    if not isinstance(coords, (list, tuple)) or len(coords) != 4:
        raise ValueError(f"B025_INVALID_MATH_BBOX: page={page_number}")
    try:
        rect = fitz.Rect(*map(float, coords))
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"B025_INVALID_MATH_BBOX: page={page_number}") from exc
    if rect.is_empty or rect.is_infinite or not page.rect.contains(rect):
        raise ValueError(f"B025_INVALID_MATH_BBOX: page={page_number}")
    # Small fixed padding protects antialiasing without capturing a full line
    # of neighbouring prose; the bounding box remains the upstream identity.
    clip = fitz.Rect(rect.x0-1, rect.y0-1, rect.x1+1, rect.y1+1) & page.rect
    scale = 3.0
    if clip.width * clip.height * scale * scale > 16_000_000:
        raise ValueError(f"B025_MATH_CROP_TOO_LARGE: page={page_number}")
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB,
                          clip=clip, alpha=False)
    if pix.width < 1 or pix.height < 1:
        raise ValueError(f"B025_EMPTY_MATH_CROP: page={page_number}")
    return pix.tobytes("png")
