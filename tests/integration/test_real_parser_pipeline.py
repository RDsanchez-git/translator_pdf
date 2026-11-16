"""B-03: repeatable real PDF extraction on a disposable multipage fixture.

Uses the supported extraction composition root, not an adapter.parse mock.
No scientific golden, production PDF-to-PDF pipeline, or tests/fixtures writes.
"""
from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from core.ast.models import ASTNode


@pytest.mark.integration
def test_real_parser_repeatable_ids_and_text_across_two_temporary_pages(
    tmp_path: Path,
) -> None:
    source = tmp_path / "b03_two_pages.pdf"
    expected = (
        "B03 first page independent observation.",
        "B03 first page distinct measurement.",
        "B03 second page experimental result.",
        "B03 second page final conclusion.",
    )
    with fitz.open() as pdf:
        for pair in (expected[:2], expected[2:]):
            page = pdf.new_page(width=595, height=842)
            for y, text in zip((100, 175), pair):
                page.insert_text((72, y), text, fontsize=11)
        pdf.save(str(source))

    parser = build_extraction_pipeline()
    first = parser.parse(str(source))
    second = parser.parse(str(source))

    assert first and second, "B03_REAL_PARSER_EMPTY_AST"
    assert all(isinstance(node, ASTNode) for node in first)
    assert [node.node_id for node in first] == [node.node_id for node in second], (
        "B03_REAL_PARSER_UNSTABLE_NODE_IDS"
    )
    identities = [str(node.node_id) for node in first]
    assert len(identities) == len(set(identities)), "B03_REAL_PARSER_DUPLICATE_IDS"
    extracted = " ".join(" ".join((node.text_content or "").split()) for node in first)
    for line in expected:
        assert line in extracted, f"B03_REAL_PARSER_SOURCE_TEXT_MISSING: {line!r}"
