"""Falsadores PPPR G2 / NADR-FPPPR-04 (físicos, sin PDFs privados)."""

from __future__ import annotations

import pytest

from core.ast.builder import FlatASTBuilder
from core.ast.cross_page import MetadataMerger
from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, NodeMetadata, ParagraphPayload, PhysicalRegion
from core.document_profile.models import ProfileInput, SamplingCoverage
from core.document_profile.detectors.layout import HeuristicLayoutDetector
from core.document_profile.detectors.semantic import HeuristicTypeDetector
from core.document_profile.profiler import HeuristicDocumentProfiler
from core.domain.document import BoundingBox
from core.layout.models import LayoutBlockDraft, LayoutBlockCollection
from infra.adapters.ast_profiling import (
    FirstPagesSamplingPolicy,
    NodeGeometryAdapter,
    NodeSemanticAdapter,
)


def _region(
    page: int,
    *,
    width: float | None = 300.0,
    bbox: BoundingBox | None = None,
    document: str = "document-a.pdf",
) -> PhysicalRegion:
    if bbox is None:
        bbox = BoundingBox(x0=195, y0=50, x1=225, y1=75)
    return PhysicalRegion(
        source_document=document,
        page_number=page,
        page_width=width,
        page_height=400.0,
        bbox=bbox,
    )


def _node(node_id: str, regions: list[PhysicalRegion]) -> ASTNode:
    return ASTNode(
        node_id=node_id,
        sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        payload=ParagraphPayload(content="A well-formed paragraph."),
        metadata=NodeMetadata(
            pages=[r.page_number for r in regions],
            bboxes=[r.bbox for r in regions if r.bbox is not None],
            physical_regions=regions,
        ),
    )


@pytest.mark.unit
def test_geometry_uses_accredited_300_point_page_not_612_fallback() -> None:
    geom = NodeGeometryAdapter().extract(_node("a", [_region(2)]))
    assert geom is not None
    assert geom.page_number == 2
    assert geom.center_x == pytest.approx(210.0)
    assert geom.relative_center_x == pytest.approx(0.70)


@pytest.mark.unit
def test_geometry_respects_mixed_page_dimensions() -> None:
    bbox = BoundingBox(x0=285, y0=50, x1=315, y1=75)
    geom = NodeGeometryAdapter().extract(_node("b", [_region(3, width=400, bbox=bbox)]))
    assert geom is not None
    assert geom.relative_center_x == pytest.approx(0.75)


@pytest.mark.unit
def test_already_normalized_coordinates_not_divided_again() -> None:
    bbox = BoundingBox(x0=0.6, y0=0.1, x1=0.8, y1=0.2, is_normalized=True)
    geom = NodeGeometryAdapter().extract(_node("c", [_region(1, width=None, bbox=bbox)]))
    assert geom is not None
    assert geom.relative_center_x == pytest.approx(0.7)


@pytest.mark.unit
def test_legacy_parallel_bbox_page_lists_do_not_prove_correspondence() -> None:
    bbox = BoundingBox(x0=10, y0=2, x1=30, y1=20)
    legacy = ASTNode(
        node_id="legacy",
        node_type=ContentNodeType.PARAGRAPH,
        payload=ParagraphPayload(content="unverified geometry"),
        metadata=NodeMetadata(pages=[1, 2], bboxes=[bbox, bbox]),
    )
    assert NodeGeometryAdapter().extract(legacy) is None


@pytest.mark.unit
def test_multiregion_node_not_reported_as_integral_single_page_geometry() -> None:
    node = _node("multi", [_region(2), _region(3)])
    assert NodeGeometryAdapter().extract(node) is None


@pytest.mark.unit
@pytest.mark.parametrize("width", [None, float("inf")])
def test_absolute_geometry_without_verified_page_width_is_not_derived(width: float | None) -> None:
    node = _node("no-width", [_region(2, width=width)])
    assert NodeGeometryAdapter().extract(node) is None


@pytest.mark.unit
def test_cross_page_merge_preserves_region_page_pairing() -> None:
    left = NodeMetadata(pages=[2], physical_regions=[_region(2)])
    right_bbox = BoundingBox(x0=40, y0=20, x1=90, y1=60)
    right = NodeMetadata(pages=[3], physical_regions=[_region(3, width=400, bbox=right_bbox)])
    merged = MetadataMerger.merge(left, right)
    assert [r.page_number for r in merged.physical_regions] == [2, 3]
    assert [r.page_width for r in merged.physical_regions] == [300, 400]
    assert merged.physical_regions[1].bbox == right_bbox
    assert NodeGeometryAdapter().extract(_node("merged", merged.physical_regions)) is None


@pytest.mark.unit
def test_builder_maps_real_physical_reference_without_parallel_guess() -> None:
    bbox = BoundingBox(x0=195, y0=50, x1=225, y1=75)
    draft = LayoutBlockDraft(
        content="physical paragraph.",
        logical_type="PARAGRAPH",
        page_index=2,
        bbox=bbox,
        source_document="physical.pdf",
        page_width=300,
        page_height=400,
    )
    node = FlatASTBuilder.build(LayoutBlockCollection(blocks=[draft]))[0]
    assert node.metadata.physical_regions == [
        PhysicalRegion(
            source_document="physical.pdf",
            page_number=2,
            page_width=300,
            page_height=400,
            bbox=bbox,
        )
    ]
    assert NodeGeometryAdapter().extract(node) is not None


@pytest.mark.unit
def test_builder_does_not_forge_geometry_when_bbox_is_missing() -> None:
    draft = LayoutBlockDraft(
        content="content without physical box.",
        logical_type="PARAGRAPH",
        page_index=2,
        bbox=None,
        source_document="physical.pdf",
        page_width=300,
        page_height=400,
    )
    node = FlatASTBuilder.build(LayoutBlockCollection(blocks=[draft]))[0]
    assert node.metadata.bboxes == []
    assert len(node.metadata.physical_regions) == 1
    assert node.metadata.physical_regions[0].bbox is None
    assert NodeGeometryAdapter().extract(node) is None


@pytest.mark.unit
def test_first_n_physical_pages_not_first_n_encountered() -> None:
    sampler = FirstPagesSamplingPolicy(NodeGeometryAdapter(), max_pages=2)
    nodes = [_node("late", [_region(5)]), _node("second", [_region(2)])]
    report = sampler.sample_with_report(nodes)
    assert [node.node_id for node in report.nodes] == ["second"]
    assert report.coverage == SamplingCoverage.STRICT_SCOPE


@pytest.mark.unit
def test_cross_boundary_node_is_not_accepted_as_strict_and_reports_loss() -> None:
    sampler = FirstPagesSamplingPolicy(NodeGeometryAdapter(), max_pages=2)
    nodes = [_node("first", [_region(1)]), _node("crosses", [_region(2), _region(3)])]
    report = sampler.sample_with_report(nodes)
    assert [node.node_id for node in report.nodes] == ["first"]
    assert report.coverage == SamplingCoverage.PARTIAL
    assert "crosses:CROSS_BOUNDARY_CONTENT_OMITTED" in report.reasons


@pytest.mark.unit
def test_uncertain_node_cannot_be_assigned_to_fake_page_zero() -> None:
    sampler = FirstPagesSamplingPolicy(NodeGeometryAdapter(), max_pages=2)
    legacy = _node("legacy", [])
    report = sampler.sample_with_report([legacy, _node("valid", [_region(1)])])
    assert [node.node_id for node in report.nodes] == ["valid"]
    assert report.coverage == SamplingCoverage.INDETERMINATE
    assert "legacy:UNVERIFIED_PHYSICAL_PROVENANCE" in report.reasons


@pytest.mark.unit
def test_sampler_must_not_combine_different_source_documents() -> None:
    sampler = FirstPagesSamplingPolicy(NodeGeometryAdapter(), max_pages=2)
    mixed = _node("mixed", [_region(1, document="a.pdf"), _region(2, document="b.pdf")])
    report = sampler.sample_with_report([mixed])
    assert report.nodes == ()
    assert report.coverage == SamplingCoverage.INDETERMINATE
    assert "mixed:MIXED_SOURCE_DOCUMENTS" in report.reasons


@pytest.mark.unit
def test_sampler_rejects_multiple_source_documents_across_nodes() -> None:
    sampler = FirstPagesSamplingPolicy(NodeGeometryAdapter(), max_pages=2)
    nodes = [
        _node("a", [_region(1, document="a.pdf")]),
        _node("b", [_region(2, document="b.pdf")]),
    ]
    report = sampler.sample_with_report(nodes)
    assert report.nodes == ()
    assert report.coverage == SamplingCoverage.INDETERMINATE
    assert report.reasons == ("MIXED_SOURCE_DOCUMENTS_IN_PROFILE",)


@pytest.mark.unit
def test_sampling_never_infers_page_from_legacy_parallel_lists() -> None:
    sampler = FirstPagesSamplingPolicy(NodeGeometryAdapter(), max_pages=1)
    bbox = BoundingBox(x0=10, y0=20, x1=20, y1=30)
    legacy = ASTNode(
        node_id="legacy-bbox",
        node_type=ContentNodeType.PARAGRAPH,
        payload=ParagraphPayload(content="unknown physical attribution"),
        metadata=NodeMetadata(pages=[1], bboxes=[bbox]),
    )
    report = sampler.sample_with_report([legacy])
    assert report.nodes == ()
    assert report.coverage == SamplingCoverage.INDETERMINATE


@pytest.mark.unit
def test_sampler_rejects_nonpositive_max_pages() -> None:
    with pytest.raises(ValueError, match=">= 1"):
        FirstPagesSamplingPolicy(NodeGeometryAdapter(), max_pages=0)


@pytest.mark.unit
def test_profiler_exposes_partial_sampling_in_diagnostics() -> None:
    geometry = NodeGeometryAdapter()
    sampler = FirstPagesSamplingPolicy(geometry, max_pages=2)
    profiler = HeuristicDocumentProfiler(
        layout_detector=HeuristicLayoutDetector(geometry),
        type_detector=HeuristicTypeDetector(NodeSemanticAdapter()),
        sampler=sampler,
    )
    input_data = ProfileInput(
        nodes=[_node("p1", [_region(1)]), _node("mixed", [_region(2), _region(3)])]
    )
    result = profiler.profile(input_data)
    assert result.diagnostics.sampling_coverage == SamplingCoverage.PARTIAL
    assert "mixed:CROSS_BOUNDARY_CONTENT_OMITTED" in result.diagnostics.sampling_reasons
