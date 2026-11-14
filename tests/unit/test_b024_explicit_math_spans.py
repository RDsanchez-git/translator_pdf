"""B02.4: deterministic, exact preservation of explicit source math."""

import pytest
from core.normalization.explicit_math import find_explicit_math_spans
from core.normalization.latex_sanitizer import InlineMathProtector


@pytest.mark.unit
@pytest.mark.parametrize("source", [
    r"The value $x_{i,j}^2$ remains.",
    r"The result $$E=mc^2$$ follows.",
    r"Example \(\alpha + \beta\) and \[x^2=y\] confirmed.",
    r"A \begin{equation}\frac{a}{b}=1\end{equation} statement.",
    r"B \begin{align*}x&=1\\y&=2\end{align*} follows.",
    r"Math $a\$b$ and $$\frac{1}{2}$$ is protected.",
    r"The value $x$ and \(y\) and $$z$$.",
])
def test_exact_mask_restore_and_determinism(source):
    masked, mapping = InlineMathProtector.mask(source)
    assert mapping
    assert source == InlineMathProtector.restore(masked, mapping)
    assert (masked, mapping) == InlineMathProtector.mask(source)
    assert [source[a:b] for a, b in find_explicit_math_spans(source)] == list(mapping.values())
    assert len(set(mapping)) == len(mapping)


@pytest.mark.unit
@pytest.mark.parametrize("source", [
    "$unclosed", "$$unclosed", r"\(unclosed", r"\[unclosed",
    r"\begin{equation}unclosed", r"\end{equation}",
    r"\)orphan", "$ $", "$x$$y$",
])
def test_unbalanced_or_ambiguous_source_fails_closed(source):
    with pytest.raises(ValueError, match="B024_"):
        InlineMathProtector.mask(source)


@pytest.mark.unit
def test_escaped_dollar_and_ordinary_prose_not_masked():
    source = r"Price \$100 and file_name is not a formula."
    assert InlineMathProtector.mask(source) == (source, {})
    assert find_explicit_math_spans(r"Literal \\( not math") == []


@pytest.mark.unit
def test_no_collision_with_existing_render_token_like_user_text():
    source = r"Source ⟪TEXRENDER0⟫ $x_1$ and __OTHER__."
    masked, mapping = InlineMathProtector.mask(source)
    assert InlineMathProtector.restore(masked, mapping) == source
