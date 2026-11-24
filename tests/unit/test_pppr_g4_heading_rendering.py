"""PPPR Gate 4/W4.2 consumer: heading provenance and physical geometry.

Tests use the real G5 mapper, TexBuilder and production geometry adapter.
They do not pretend to exercise Tectonic or infer linguistic quality.
"""
import pytest

from apps.compiler.__main__ import RenderGeometryAdapter
from apps.compiler.tex_builder import TexBuilder
from core.ast.enums import ContentNodeType, HeadingLevel, TranslationStrategy
from core.ast.models import ASTNode, HeadingPayload, NodeMetadata, PhysicalRegion
from core.compiler.rendering.context import RenderContextFactory
from core.compiler.rendering.mapper import DefaultRenderUnitMapper
from core.compiler.rendering.models import RenderUnit
from core.document_profile.models import InferredDocumentProfile, PageLayout
from core.domain.document import BoundingBox


class _NoAssets:
    def extract(self, node: ASTNode):
        return None


def _node(level: HeadingLevel, *, node_id: str = "h") -> ASTNode:
    return ASTNode(
        node_id=node_id, sequence_id=1,
        node_type=ContentNodeType.HEADING, strategy=TranslationStrategy.TRANSLATE,
        payload=HeadingPayload(content="Source", heading_level=level),
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("level", "expected_command"),
    [(HeadingLevel.H1, r"\section*{"),
     (HeadingLevel.H2, r"\subsection*{"),
     (HeadingLevel.H3, r"\subsubsection*{")],
)
def test_valid_heading_levels_survive_mapper_into_distinct_g5_commands(
    level: HeadingLevel, expected_command: str,
) -> None:
    node = _node(level)
    unit = DefaultRenderUnitMapper(RenderGeometryAdapter(), _NoAssets()).map_to_unit(
        [node], "Título traducido en español"
    )
    assert unit.heading_level == level
    assert unit.content == "Título traducido en español"
    tex = TexBuilder(RenderContextFactory.create(
        InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    )).build([unit])
    assert expected_command + "Título traducido en español}" in tex
    assert "Source" not in tex
    assert "Título traducido en español" in tex


@pytest.mark.unit
@pytest.mark.parametrize("level", [HeadingLevel.UNKNOWN, None])
def test_unknown_heading_level_fails_closed_in_real_builder(level):
    unit = RenderUnit(
        node_id="h", node_type=ContentNodeType.HEADING,
        content="Texto recibido", heading_level=level,
    )
    with pytest.raises(ValueError) as error:
        TexBuilder(RenderContextFactory.create(
            InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
        )).build([unit])
    assert str(error.value) == "PPPR_G4_HEADING_LEVEL_UNVERIFIED node_id='h'"


@pytest.mark.unit
def test_empty_heading_failure_is_attributable_without_metadata_line_injection():
    node_id = "h\n\\input{private.tex}"
    unit = RenderUnit(
        node_id=node_id, node_type=ContentNodeType.HEADING,
        content=" ", heading_level=HeadingLevel.H1,
    )
    with pytest.raises(ValueError) as error:
        TexBuilder(RenderContextFactory.create(
            InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
        )).build([unit])
    assert str(error.value) == f"PPPR_G4_HEADING_CONTENT_MISSING node_id={ascii(node_id)}"
    assert len(str(error.value).splitlines()) == 1


@pytest.mark.unit
def test_heading_does_not_retranslate_or_activate_textual_tex():
    unit = RenderUnit(
        node_id="h", node_type=ContentNodeType.HEADING,
        content=r"Métodos & \input{file.tex} $x_i$",
        heading_level=HeadingLevel.H2,
    )
    tex = TexBuilder(RenderContextFactory.create(
        InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    )).build([unit])
    assert r"\subsection*{Métodos \& \textbackslash{}input\{file.tex\} $x_i$}" in tex
    assert r"\input{" not in tex


@pytest.mark.unit
def test_physical_geometry_uses_accredited_page_dimensions_not_letter_fallback():
    bbox = BoundingBox(x0=40, y0=100, x1=140, y1=150)
    region = PhysicalRegion(
        source_document="synthetic.pdf", page_number=2,
        bbox=bbox, page_width=200, page_height=500,
    )
    node = _node(HeadingLevel.H1).model_copy(update={
        "metadata": NodeMetadata(physical_regions=(region,))
    })
    g = RenderGeometryAdapter().extract(node)
    assert g is not None
    assert g.page_number == 2
    assert (g.relative_x, g.relative_y, g.relative_width, g.relative_height) == pytest.approx(
        (.2, .2, .5, .1), rel=1e-12, abs=1e-12,
    )


@pytest.mark.unit
def test_missing_or_ambiguous_physical_geometry_does_not_fabricate_coordinates():
    bbox = BoundingBox(x0=40, y0=100, x1=140, y1=150)
    unverified = PhysicalRegion(
        source_document="synthetic.pdf", page_number=1,
        bbox=bbox, page_width=None, page_height=None,
    )
    repeated = PhysicalRegion(
        source_document="synthetic.pdf", page_number=2,
        bbox=bbox, page_width=200, page_height=500,
    )
    adapter = RenderGeometryAdapter()
    assert adapter.extract(_node(HeadingLevel.H1).model_copy(update={
        "metadata": NodeMetadata(bboxes=[bbox], pages=[1]),
    })) is None
    assert adapter.extract(_node(HeadingLevel.H1).model_copy(update={
        "metadata": NodeMetadata(physical_regions=(unverified,)),
    })) is None
    assert adapter.extract(_node(HeadingLevel.H1).model_copy(update={
        "metadata": NodeMetadata(physical_regions=(unverified, repeated)),
    })) is None


@pytest.mark.unit
def test_unverified_physical_region_does_not_reject_unrelated_paragraph(caplog):
    """FPPPR-04 R9: no invented geometry, no blanket document rejection."""
    from core.ast.models import ParagraphPayload
    from core.compiler.assembler import DocumentAssembler
    from core.compiler.assembly_context import AssemblyExecutionContext
    from core.compiler.service import CompilationService
    from core.execution.ports import ProjectionRecord

    class NoFallback:
        def get_verified_payload(self, job_id, chunk_id, expected_sha256):
            pytest.fail("Complete CURRENT projection must not call fallback")

    class ProfileStore:
        def get(self, document_id):
            assert document_id == "synthetic-doc"
            return InferredDocumentProfile(
                layout=PageLayout.SINGLE_COLUMN, document_type=None,
            )

    region = PhysicalRegion(
        source_document="synthetic-input.pdf", page_number=1,
        bbox=BoundingBox(x0=20, y0=35, x1=90, y1=75),
        page_width=None, page_height=None,
    )
    node = ASTNode(
        node_id="paragraph-1", sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        payload=ParagraphPayload(content="Original"),
        metadata=NodeMetadata(physical_regions=(region,)),
    )
    mapper = DefaultRenderUnitMapper(RenderGeometryAdapter(), _NoAssets())
    unit = mapper.map_to_unit([node], "Texto recibido")
    assert unit.geometry is None

    repository = NoFallback()
    service = CompilationService(
        DocumentAssembler(repository),
        repository, ProfileStore(), mapper,
    )
    context = AssemblyExecutionContext(
        document_id="synthetic-doc", ast_hash="ast-generation",
        ast_nodes=(node,),
        projections=(ProjectionRecord("paragraph-1", "Texto recibido", 1),),
        projection_version=1,
    )
    tex = service.compile_document(context)
    assert "Texto recibido" in tex
    assert "Original" not in tex
    assert "PPPR_G4_GEOMETRY_UNVERIFIED" in caplog.text
    assert "paragraph-1" in caplog.text
