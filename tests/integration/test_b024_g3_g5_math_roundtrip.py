"""B02.4: G3 math masking and G5 rendering use the same span boundaries."""

import pytest
from core.normalization.latex_sanitizer import InlineMathProtector
from core.compiler.rendering.implementations import TextRenderStrategy
from core.compiler.rendering.models import RenderUnit
from core.ast.enums import ContentNodeType


@pytest.mark.integration
@pytest.mark.parametrize("source, expected", [
    (r"The area is \(\pi r^2\) & measured.", r"The area is \(\pi r^2\) \& measured."),
    (r"The result $$E=mc^2$$ has 5% error.", r"The result $$E=mc^2$$ has 5\% error."),
    (r"The equation \begin{equation}x^2=1\end{equation} holds.",
     r"The equation \begin{equation}x^2=1\end{equation} holds."),
    (r"Literal ⟪TEXRENDER0⟫ and $x_i$.", r"Literal ⟪TEXRENDER0⟫ and $x_i$."),
])
def test_mask_restore_render_preserves_all_math_bytes(source, expected):
    masked, mapping = InlineMathProtector.mask(source)
    projected = InlineMathProtector.restore(masked, mapping)
    unit = RenderUnit(node_id="math-roundtrip", node_type=ContentNodeType.PARAGRAPH, content=projected)
    rendered = TextRenderStrategy().render(unit)
    assert rendered == expected


@pytest.mark.integration
def test_mathematical_delimiter_error_prevents_render():
    with pytest.raises(ValueError, match="B024_UNCLOSED_MATH"):
        TextRenderStrategy().render(RenderUnit(
            node_id="failed", node_type=ContentNodeType.PARAGRAPH, content=r"Lost \(math"
        ))
