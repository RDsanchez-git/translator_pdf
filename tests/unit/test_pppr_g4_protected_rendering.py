"""PPPR G4/W4.1: protected literal content vs contractually active TeX."""

import pytest

from apps.compiler.tex_builder import TexBuilder
from core.ast.enums import ContentNodeType
from core.compiler.rendering.context import RenderContextFactory
from core.compiler.rendering.implementations import (
    LiteralProtectedRenderStrategy,
    PassthroughRenderStrategy,
)
from core.compiler.rendering.models import RenderUnit
from core.document_profile.models import InferredDocumentProfile, PageLayout


def _unit(kind: ContentNodeType, text: str, node: str = "n") -> RenderUnit:
    return RenderUnit(node_id=node, node_type=kind, content=text)


@pytest.mark.unit
@pytest.mark.parametrize(
    "kind",
    [ContentNodeType.CODE, ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX],
)
def test_literal_special_characters_never_activate_tex(kind: ContentNodeType) -> None:
    source = "path\\file_1% $5 & value_{x} # ~ ^"
    rendered = LiteralProtectedRenderStrategy().render(_unit(kind, source))
    assert r"\textbackslash{}" in rendered
    for escaped in (r"\_", r"\%", r"\$", r"\&", r"\{", r"\}", r"\#", r"\textasciitilde{}", r"\textasciicircum{}"):
        assert escaped in rendered
    assert r"\input{" not in rendered
    assert r"\begin{equation}" not in rendered


@pytest.mark.unit
def test_literal_source_macro_and_math_like_text_are_never_executed() -> None:
    source = r"\input{private.tex} \textbf{not-markup} $x_i$"
    rendered = LiteralProtectedRenderStrategy().render(_unit(ContentNodeType.CODE, source))
    assert r"\input{" not in rendered
    assert r"\textbf{" not in rendered
    assert "$x_i$" not in rendered
    assert r"\$x\_i\$" in rendered
    assert r"\textbackslash{}" in rendered


@pytest.mark.unit
def test_literal_preserves_whitespace_and_logical_lines() -> None:
    source = "  indented_line\n\tsecond  line\n"
    rendered = LiteralProtectedRenderStrategy().render(_unit(ContentNodeType.CODE, source))
    assert r"\ \ indented\_line" in rendered
    assert r"\hspace*{4em}second\ \ line" in rendered
    assert rendered.count(r"\par\noindent ") == 2


@pytest.mark.unit
def test_literal_empty_does_not_create_ghost_block() -> None:
    assert LiteralProtectedRenderStrategy().render(_unit(ContentNodeType.CODE, "")) == ""


@pytest.mark.unit
def test_active_equation_is_not_escaped_or_reclassified_as_literal() -> None:
    formula = r"\begin{equation}x_i^2=y\end{equation}"
    assert PassthroughRenderStrategy().render(_unit(ContentNodeType.DISPLAY_EQUATION, formula)) == formula


@pytest.mark.unit
def test_real_factory_and_tex_builder_keep_each_classification_separate() -> None:
    profile = InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    builder = TexBuilder(RenderContextFactory.create(profile))
    source_literal = r"\input{private.tex} $x_i$"
    source_math = r"\begin{equation}x_i^2=y\end{equation}"
    tex = builder.build([
        _unit(ContentNodeType.CODE, source_literal, "code"),
        _unit(ContentNodeType.TABLE_SIMPLE, "first_col & second_col %", "table"),
        _unit(ContentNodeType.DISPLAY_EQUATION, source_math, "math"),
    ])
    assert r"\input{" not in tex
    assert r"\$x\_i\$" in tex
    assert r"first\_col\ \&\ second\_col\ \%" in tex
    assert source_math in tex
    assert tex.count(r"\begin{equation}") == 1


@pytest.mark.unit
def test_unclassified_composite_fails_closed_in_real_render_path() -> None:
    profile = InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    builder = TexBuilder(RenderContextFactory.create(profile))
    with pytest.raises(ValueError, match="PPPR_G4_UNCLASSIFIED_MIXED_RENDER_UNIT"):
        builder.build([_unit(ContentNodeType.COMPOSITE_BLOCK, r"Literal \input{foo} and $x$")])


@pytest.mark.unit
def test_mathematical_text_in_paragraph_keeps_accredited_span_only() -> None:
    profile = InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    builder = TexBuilder(RenderContextFactory.create(profile))
    tex = builder.build([_unit(ContentNodeType.PARAGRAPH, r"Result $x_i$ and \input{foo}", "paragraph")])
    assert "$x_i$" in tex
    assert r"\input{" not in tex
    assert r"\textbackslash{}input" in tex
