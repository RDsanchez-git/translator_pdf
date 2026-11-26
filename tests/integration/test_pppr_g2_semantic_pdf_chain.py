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


@pytest.mark.integration
def test_real_unnumbered_title_keeps_safe_root_context_without_aborting(tmp_path: Path) -> None:
    """Real PyMuPDF title is UNKNOWN; it is preserved rather than fabricated H1."""
    from core.ast.models import TranslationTaskType
    from core.chunking.contextual_plan import prepare_contextual_plan
    source = tmp_path / "unlabeled_title.pdf"
    with fitz.open() as document:
        page = document.new_page(width=400, height=600)
        page.insert_text((90, 130), "A Scientific Study", fontsize=23)
        for index in range(3):
            page.insert_text((65, 210 + 38 * index), "Repeated experiment observations.", fontsize=10)
        document.save(str(source))
    nodes = build_extraction_pipeline().parse(str(source))
    assert any(
        node.node_type == ContentNodeType.HEADING
        and isinstance(node.payload, HeadingPayload)
        and node.payload.heading_level == HeadingLevel.UNKNOWN
        for node in nodes
    )
    class Estimator:
        def estimate_tokens(self, text: str) -> int:
            return max(1, len(text) // 4)

    prepared = prepare_contextual_plan(document_id="synthetic", raw_ast=nodes, estimator=Estimator())
    assert prepared.plan.ast_hash == compute_ast_hash(nodes)
    for unit in prepared.plan.units:
        if any(member.node_type == ContentNodeType.HEADING.value for member in unit.members):
            assert unit.chunk_type == TranslationTaskType.PRESERVE
            assert all(
                member.source_text == next(node.text_content for node in nodes if node.node_id == member.node_id)
                for member in unit.members
            )
