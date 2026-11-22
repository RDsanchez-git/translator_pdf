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
