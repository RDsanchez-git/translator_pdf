"""G2: procedencia física en la ruta real PDF → provider → AST, sin GT privado."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from infra.adapters.ast_profiling import NodeGeometryAdapter


@pytest.mark.integration
def test_production_parser_retains_verified_page_regions_with_mixed_sizes(
    tmp_path: Path,
) -> None:
    source = tmp_path / "physical_provenance_two_pages.pdf"
    with fitz.open() as pdf:
        first = pdf.new_page(width=300, height=400)
        first.insert_text((70, 100), "First measured result.", fontsize=10)
        second = pdf.new_page(width=400, height=500)
        second.insert_text((110, 120), "Second measured result.", fontsize=10)
        pdf.save(str(source))

    nodes = build_extraction_pipeline().parse(str(source))
    assert nodes, "G2_PHYSICAL_INGEST_EMPTY_AST"
    measured = [
        region
        for node in nodes
        for region in node.metadata.physical_regions
    ]
    assert measured, "G2_PHYSICAL_REGIONS_MISSING"
    assert {region.page_number for region in measured} == {1, 2}
    assert {region.source_document for region in measured} == {str(source)}
    assert {(region.page_number, region.page_width, region.page_height) for region in measured} == {
        (1, 300.0, 400.0),
        (2, 400.0, 500.0),
    }
    assert all(region.bbox is not None for region in measured)
    assert all(
        NodeGeometryAdapter().extract(node) is not None
        for node in nodes if len(node.metadata.physical_regions) == 1
        and node.metadata.physical_regions[0].bbox is not None
    )
