"""B02.2/G5: image references render to a safe, staged TeX path."""
from hashlib import sha256

import pytest

from core.ast.enums import ContentNodeType
from core.compiler.rendering.image_assets import canonical_image_name
from core.compiler.rendering.implementations import AdaptiveFloatStrategy
from core.compiler.rendering.models import (
    AssetReference, RenderGeometry, RenderingConfiguration, RenderUnit,
)

_DIGEST = sha256(b"test-image").hexdigest()
_REF = "data/assets/" + _DIGEST + ".png"


def _unit(asset=None, *, wide=False, content=r"\input{evil.tex}"):
    return RenderUnit(
        node_id="p1_b3", node_type=ContentNodeType.IMAGE, content=content,
        geometry=RenderGeometry(.1, .1, .9 if wide else .3, .2, 1),
        asset=asset,
    )


@pytest.mark.unit
def test_single_column_renders_graphic_not_untrusted_content():
    strategy = AdaptiveFloatStrategy(RenderingConfiguration(is_multi_column=False))
    tex = strategy.render(_unit(AssetReference(path=_REF)))
    assert r"\includegraphics[width=\linewidth,keepaspectratio]{assets/" + _DIGEST + ".png}" in tex
    assert r"\input" not in tex
    assert r"\begin{figure}" in tex


@pytest.mark.unit
def test_double_column_wide_uses_figure_star():
    strategy = AdaptiveFloatStrategy(RenderingConfiguration(is_multi_column=True))
    assert r"\begin{figure*}" in strategy.render(_unit(AssetReference(path=_REF), wide=True))


@pytest.mark.unit
def test_double_column_narrow_uses_ordinary_figure():
    strategy = AdaptiveFloatStrategy(RenderingConfiguration(is_multi_column=True))
    assert r"\begin{figure}" in strategy.render(_unit(AssetReference(path=_REF)))


@pytest.mark.unit
def test_image_without_reference_rejected():
    strategy = AdaptiveFloatStrategy(RenderingConfiguration(is_multi_column=False))
    with pytest.raises(ValueError, match="B02_G5_IMAGE_ASSET_REFERENCE_MISSING"):
        strategy.render(_unit())


@pytest.mark.unit
@pytest.mark.parametrize("path", [
    "../escape.png", "/tmp/escape.png", "data/assets/../../bad.png",
    "data/assets/" + _DIGEST + ".jpg", "data\\assets\\" + _DIGEST + ".png",
    "data/assets/" + _DIGEST.upper() + ".png", "data/assets/" + _DIGEST + ".png%",
])
def test_noncanonical_asset_is_not_embedded_in_tex(path):
    with pytest.raises(ValueError, match="B02_G5_IMAGE_NONCANONICAL_REFERENCE"):
        canonical_image_name(AssetReference(path=path))


@pytest.mark.unit
def test_non_png_mime_rejected():
    with pytest.raises(ValueError, match="B02_G5_IMAGE_UNSUPPORTED_MIME"):
        canonical_image_name(AssetReference(path=_REF, mime_type="image/jpeg"))
