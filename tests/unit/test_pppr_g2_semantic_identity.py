"""G2/W2.2 T2.2.1: falsadores de identidad semántica y Unicode STEM."""

from __future__ import annotations

import pytest

from core.ast.enums import ContentNodeType, HeadingLevel
from core.ast.hashing import compute_ast_hash
from core.ast.models import (
    ASTNode, HeadingPayload, NodeMetadata, ParagraphPayload,
)
from core.ast.builder import FlatASTBuilder
from core.layout.models import LayoutBlockDraft, LayoutBlockCollection


def _heading(level: HeadingLevel, content: str = "Methods", *, node_id: str = "h") -> ASTNode:
    return ASTNode(
        node_id=node_id,
        node_type=ContentNodeType.HEADING,
        payload=HeadingPayload(content=content, heading_level=level),
        depth=1,
    )


def _paragraph(content: str, *, node_id: str = "p", depth: int = 1) -> ASTNode:
    return ASTNode(
        node_id=node_id, node_type=ContentNodeType.PARAGRAPH,
        payload=ParagraphPayload(content=content), depth=depth,
    )


@pytest.mark.unit
def test_h1_and_h2_have_distinct_semantic_hash_even_with_identical_text() -> None:
    assert compute_ast_hash([_heading(HeadingLevel.H1)]) != compute_ast_hash(
        [_heading(HeadingLevel.H2)]
    )


@pytest.mark.unit
def test_unknown_heading_cannot_be_silently_aliased_to_h1() -> None:
    assert compute_ast_hash([_heading(HeadingLevel.UNKNOWN)]) != compute_ast_hash(
        [_heading(HeadingLevel.H1)]
    )


@pytest.mark.unit
def test_semantic_depth_and_order_change_identity() -> None:
    heading = _heading(HeadingLevel.H1)
    paragraph = _paragraph("Result", depth=1)
    assert compute_ast_hash([heading, paragraph]) != compute_ast_hash(
        [paragraph, heading]
    )
    assert compute_ast_hash([paragraph]) != compute_ast_hash(
        [_paragraph("Result", depth=2)]
    )


@pytest.mark.unit
def test_only_physical_metadata_and_runtime_ids_are_excluded() -> None:
    original = _paragraph("E = mc²", node_id="one")
    relabelled = _paragraph("E = mc²", node_id="two").model_copy(update={
        "metadata": NodeMetadata(pages=[9], confidence=0.2),
        "sequence_id": 143,
        "control_plane": {"execution_id": "retry-2"},
    })
    assert compute_ast_hash([original]) == compute_ast_hash([relabelled])


@pytest.mark.unit
def test_unicode_latin_combining_sequence_is_stable_when_unambiguous() -> None:
    assert compute_ast_hash([_paragraph("cafe\u0301")]) == compute_ast_hash(
        [_paragraph("café")]
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("left", "right"), [
        ("ℝ", "R"), ("µ", "μ"), ("K", "K"), ("Ω", "Ω"),
        ("−", "-"), ("x²", "x2"), ("fi", "ﬁ"),
    ],
)
def test_stem_symbols_are_not_collapsed_by_unicode_normalization(
    left: str, right: str,
) -> None:
    assert compute_ast_hash([_paragraph(left)]) != compute_ast_hash(
        [_paragraph(right)]
    )


@pytest.mark.unit
def test_same_input_has_reproducible_versioned_hash_and_ordered_nodes() -> None:
    first = [_heading(HeadingLevel.H3), _paragraph("H₂O + ℝ", depth=3)]
    assert compute_ast_hash(first) == compute_ast_hash(list(first))
    assert len(compute_ast_hash(first)) == 64


@pytest.mark.unit
def test_layout_draft_transports_explicit_heading_level_and_defaults_unknown() -> None:
    known = LayoutBlockDraft(
        logical_type="SECTION", content="Methods", page_index=1, level=2,
    )
    unknown = LayoutBlockDraft(
        logical_type="SECTION", content="Methods", page_index=1,
    )
    assert FlatASTBuilder._map_physical_to_logical(known, 0).payload == HeadingPayload(
        content="Methods", heading_level=HeadingLevel.H2,
    )
    assert FlatASTBuilder._map_physical_to_logical(unknown, 0).payload == HeadingPayload(
        content="Methods", heading_level=HeadingLevel.UNKNOWN,
    )
    assert compute_ast_hash(FlatASTBuilder.build(LayoutBlockCollection(blocks=[known]))) != (
        compute_ast_hash(FlatASTBuilder.build(LayoutBlockCollection(blocks=[unknown])))
    )


@pytest.mark.unit
def test_invalid_heading_level_cannot_be_accredited_by_layout_draft() -> None:
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        LayoutBlockDraft(logical_type="SECTION", content="Methods", page_index=1, level=4)


@pytest.mark.unit
@pytest.mark.parametrize(("text", "expected"), [
    ("1 Methods", HeadingLevel.H1),
    ("1.2 Data", HeadingLevel.H2),
    ("1.2.3 Measurements", HeadingLevel.H3),
    ("Methods", HeadingLevel.UNKNOWN),
    ("1.2.3.4 Deeper heading", HeadingLevel.UNKNOWN),
    ("2.3e5 not a section", HeadingLevel.UNKNOWN),
])
def test_only_numbered_section_evidence_can_create_a_heading_level(
    text: str, expected: HeadingLevel,
) -> None:
    draft = LayoutBlockDraft(logical_type="SECTION", content=text, page_index=2)
    result = FlatASTBuilder._map_physical_to_logical(draft, 0)
    assert isinstance(result.payload, HeadingPayload)
    assert result.payload.heading_level == expected
