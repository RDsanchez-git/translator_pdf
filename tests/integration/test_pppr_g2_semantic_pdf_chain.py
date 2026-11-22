"""Wave 2.2: frontera PDF real -> AST -> identidad, sin fabricar H1/H2/H3."""

from pathlib import Path

import fitz
import pytest

from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from core.ast.enums import ContentNodeType, HeadingLevel
from core.ast.hashing import compute_ast_hash
from core.ast.models import HeadingPayload


@pytest.mark.integration
def test_connected_pdf_parser_does_not_invent_heading_level_and_hashes_real_ast(
    tmp_path: Path,
) -> None:
    path = tmp_path / "physical-heading.pdf"
    with fitz.open() as pdf:
        page = pdf.new_page(width=300, height=400)
        page.insert_text((60, 80), "Methods", fontsize=20)
        page.insert_text((60, 130), "A reproducible experiment.", fontsize=10)
        pdf.save(str(path))
    nodes = build_extraction_pipeline().parse(str(path))
    assert nodes
    headings = [node for node in nodes if node.node_type == ContentNodeType.HEADING]
    # La señal tipográfica no acredita por sí sola H1, H2 o H3.
    assert all(
        isinstance(node.payload, HeadingPayload)
        and node.payload.heading_level == HeadingLevel.UNKNOWN
        for node in headings
    )
    assert compute_ast_hash(nodes) == compute_ast_hash(tuple(nodes))


@pytest.mark.integration
def test_connected_pdf_chain_preserves_explicitly_numbered_h1_h2_h3(
    tmp_path: Path,
) -> None:
    """Synthetic physical PDF witnesses H1/H2/H3; unnumbered stays UNKNOWN."""
    source = tmp_path / "numbered-sections.pdf"
    with fitz.open() as pdf:
        page = pdf.new_page(width=350, height=500)
        page.insert_text((60, 160), "Introductory unnumbered text.", fontsize=10)
        for section in ("1 Methods", "1.2 Data", "1.2.3 Measurements"):
            page = pdf.new_page(width=350, height=500)
            page.insert_text((60, 140), section, fontsize=20)
            for index in range(3):
                page.insert_text(
                    (60, 220 + 35 * index),
                    f"Experimental detail paragraph {index} on this page.",
                    fontsize=10,
                )
        pdf.save(str(source))
    nodes = build_extraction_pipeline().parse(str(source))
    levels = {
        node.text_content: node.payload.heading_level
        for node in nodes
        if node.node_type == ContentNodeType.HEADING
        and isinstance(node.payload, HeadingPayload)
    }
    assert levels["1 Methods"] == HeadingLevel.H1
    assert levels["1.2 Data"] == HeadingLevel.H2
    assert levels["1.2.3 Measurements"] == HeadingLevel.H3
    assert len(compute_ast_hash(nodes)) == 64
