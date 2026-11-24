"""Gate 4 Wave 4.2: image width uncertainty at real G5 boundaries.

Exercises the physical adapter, mapper, render factory, TexBuilder and
CompilationService. No Tectonic or scientific quality is claimed.
"""
from hashlib import sha256
from math import inf, nan

import pytest

from apps.compiler.__main__ import RenderAssetAdapter, RenderGeometryAdapter
from apps.compiler.tex_builder import TexBuilder
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import (
    ASTNode, ImagePayload, NodeMetadata, ParagraphPayload, PhysicalRegion,
)
from core.compiler.assembler import DocumentAssembler
from core.compiler.assembly_context import AssemblyExecutionContext
from core.compiler.exceptions import ASTConsistencyError
from core.compiler.rendering.context import RenderContextFactory
from core.compiler.rendering.mapper import DefaultRenderUnitMapper
from core.compiler.rendering.models import AssetReference, RenderGeometry, RenderUnit
from core.compiler.service import CompilationService
from core.document_profile.models import (
    InferredDocumentProfile, PageLayout, ProfileDiagnostics, SamplingCoverage,
)
from core.domain.document import BoundingBox
from core.execution.ports import ProjectionRecord


_DIGEST = sha256(b"fixture").hexdigest()
_ASSET = "data/assets/" + _DIGEST + ".png"


def _profile() -> InferredDocumentProfile:
    return InferredDocumentProfile(
        layout=PageLayout.DOUBLE_COLUMN, document_type=None,
        physical_diagnostics=ProfileDiagnostics(
            layout_confidence=1.0, type_confidence=1.0,
            sampling_coverage=SamplingCoverage.STRICT_SCOPE,
        ),
    )


def _region(width: float | None) -> PhysicalRegion:
    return PhysicalRegion(
        source_document="source.pdf", page_number=1,
        bbox=BoundingBox(x0=10, y0=20, x1=70, y1=50),
        page_width=width, page_height=100,
    )


def _image(regions: tuple[PhysicalRegion, ...]) -> ASTNode:
    return ASTNode(
        node_id="figure-1", sequence_id=1, node_type=ContentNodeType.IMAGE,
        strategy=TranslationStrategy.PRESERVE,
        payload=ImagePayload(asset_path=_ASSET),
        metadata=NodeMetadata(physical_regions=regions),
    )


def _mapper() -> DefaultRenderUnitMapper:
    return DefaultRenderUnitMapper(RenderGeometryAdapter(), RenderAssetAdapter())


@pytest.mark.unit
@pytest.mark.parametrize(
    ("page_width", "environment"),
    [(200.0, r"\begin{figure}"), (80.0, r"\begin{figure*}")],
)
def test_attested_narrow_and_wide_image(
    page_width: float, environment: str,
) -> None:
    unit = _mapper().map_to_unit([_image((_region(page_width),))], "")
    assert unit.geometry is not None
    tex = TexBuilder(RenderContextFactory.create(_profile())).build([unit])
    assert environment in tex
    assert "PPPR_G4_IMAGE_WIDTH_UNVERIFIED" not in tex
    assert "assets/" + _DIGEST + ".png" in tex


@pytest.mark.unit
@pytest.mark.parametrize("regions", [
    (),
    (_region(None),),
    (_region(200), _region(200)),
])
def test_absent_or_ambiguous_physical_image_width_is_not_verified_narrow(
    regions: tuple[PhysicalRegion, ...],
) -> None:
    unit = _mapper().map_to_unit([_image(regions)], "")
    assert unit.geometry is None
    tex = TexBuilder(RenderContextFactory.create(_profile())).build([unit])
    assert r"\begin{figure}" in tex
    assert r"\begin{figure*}" not in tex
    assert "% [PPPR_G4_IMAGE_WIDTH_UNVERIFIED] [NODE_ID: 'figure-1']" in tex


@pytest.mark.unit
@pytest.mark.parametrize("geometry", [
    None,
    RenderGeometry(0.1, 0.1, 0.0, 0.3, 1),
    RenderGeometry(0.1, 0.1, -0.2, 0.3, 1),
    RenderGeometry(0.1, 0.1, 1.1, 0.3, 1),
    RenderGeometry(0.1, 0.1, nan, 0.3, 1),
    RenderGeometry(0.1, 0.1, inf, 0.3, 1),
    RenderGeometry(0.9, 0.1, 0.4, 0.3, 1),
    RenderGeometry(0.1, 0.1, 0.3, 0.3, 0),
    RenderGeometry(nan, 0.1, 0.3, 0.3, 1),
])
def test_invalid_width_emits_attributable_safe_tex_comment(
    geometry: RenderGeometry | None,
) -> None:
    node_id = "image\n\\input{private.tex}"
    unit = RenderUnit(
        node_id=node_id, node_type=ContentNodeType.IMAGE,
        content=r"\input{private.tex}", geometry=geometry,
        asset=AssetReference(path=_ASSET),
    )
    tex = TexBuilder(RenderContextFactory.create(_profile())).build([unit])
    assert r"\begin{figure}" in tex
    assert r"\begin{figure*}" not in tex
    assert r"\input{private.tex}" not in tex
    comment_lines = [
        line for line in tex.splitlines()
        if line.startswith("% [PPPR_G4_IMAGE_WIDTH_UNVERIFIED]")
    ]
    assert comment_lines == [
        f"% [PPPR_G4_IMAGE_WIDTH_UNVERIFIED] [NODE_ID: {ascii(node_id)}]"
    ]
    assert tex.splitlines().count(r"\end{document}") == 1


class _NoFallback:
    def get_verified_payload(
        self, job_id: str, chunk_id: str, expected_sha256: str,
    ) -> str:
        pytest.fail("CURRENT projections must not fall back to original source")


class _Profiles:
    def get(self, document_id: str) -> InferredDocumentProfile:
        assert document_id == "synthetic-doc"
        return _profile()


def _service() -> CompilationService:
    repo = _NoFallback()
    return CompilationService(DocumentAssembler(repo), repo, _Profiles(), _mapper())


@pytest.mark.unit
def test_unverified_two_column_image_blocks_conforming_compilation(caplog) -> None:
    image = _image((_region(None),))
    paragraph = ASTNode(
        node_id="paragraph-2", sequence_id=2,
        node_type=ContentNodeType.PARAGRAPH,
        payload=ParagraphPayload(content="Original"),
        metadata=NodeMetadata(physical_regions=(_region(None),)),
    )
    context = AssemblyExecutionContext(
        document_id="synthetic-doc", ast_hash="generation",
        ast_nodes=(image, paragraph),
        projections=(
            ProjectionRecord("figure-1", "", 1),
            ProjectionRecord("paragraph-2", "Texto independiente", 1),
        ),
        projection_version=1,
    )
    with pytest.raises(ASTConsistencyError, match="PPPR_G4_IMAGE_WIDTH_UNVERIFIED.*figure-1"):
        _service().compile_document_with_assets(context)
    assert "PPPR_G4_IMAGE_WIDTH_UNVERIFIED" in caplog.text
    assert "figure-1" in caplog.text


@pytest.mark.unit
def test_independent_paragraph_survives_unknown_physical_geometry() -> None:
    paragraph = ASTNode(
        node_id="paragraph-1", sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        payload=ParagraphPayload(content="Original"),
        metadata=NodeMetadata(physical_regions=(_region(None),)),
    )
    context = AssemblyExecutionContext(
        document_id="synthetic-doc", ast_hash="generation",
        ast_nodes=(paragraph,),
        projections=(ProjectionRecord("paragraph-1", "Texto traducido", 1),),
        projection_version=1,
    )
    tex, assets = _service().compile_document_with_assets(context)
    assert "Texto traducido" in tex
    assert "PPPR_G4_IMAGE_WIDTH_UNVERIFIED" not in tex
    assert assets == ()
