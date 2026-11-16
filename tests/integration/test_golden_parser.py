"""B-01: technical extraction contract over a disposable, text-only PDF.

This is NOT a scientific golden fingerprint or PDF-to-PDF E2E assertion.
The production extraction root and physical parser are both exercised.
"""
from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from apps.bootstrap.pipeline_factory import build_extraction_pipeline


@pytest.mark.integration
def test_production_parser_preserves_known_text_from_disposable_pdf(
    tmp_path: Path,
) -> None:
    """Independently known text must survive the real PDF->AST extraction."""
    source = tmp_path / "known_text_b01.pdf"
    expected_lines = (
        "B01 Alpha controlled paragraph.",
        "B01 Beta independent observation.",
    )

    with fitz.open() as pdf:
        page = pdf.new_page(width=595, height=842)
        for y, line in zip((100, 160), expected_lines):
            page.insert_text((72, y), line, fontsize=11)
        pdf.save(str(source))

    # Deliberately no patch of adapter.parse or generated expected fingerprint.
    nodes = build_extraction_pipeline().parse(str(source))
    assert nodes, "El parser real no debe perder todos los nodos del PDF."

    # Join node text rather than lock in incidental physical block segmentation.
    extracted_text = " ".join(
        " ".join((node.text_content or "").split()) for node in nodes
    )
    for line in expected_lines:
        assert line in extracted_text, (
            f"El parser real perdió texto conocido del PDF sintético: {line!r}"
        )

    ids = [str(node.node_id) for node in nodes]
    assert all(ids), "Cada nodo extraído debe tener identidad."
    assert len(ids) == len(set(ids)), "Identidades AST duplicadas."
