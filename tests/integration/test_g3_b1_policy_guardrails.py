"""G3-B1-R1: invariantes de politica y payload no cubiertas en las ocho pruebas B1.

No requiere red, contenedores ni bases de datos. El parche no modifica las aserciones.
"""
from dataclasses import replace

import pytest

from core.ast.enums import ContentNodeType
from core.ast.models import (
    ASTNode, MathPayload, ParagraphPayload, TablePayload, TranslationTaskType,
)
from core.ast.grouper import SemanticGroup
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from core.chunking.manifest_contract import ChunkPlan


class WordEstimator:
    def estimate_tokens(self, text: str) -> int:
        return len(text.split())


def _node(name: str, typ: ContentNodeType, value: str) -> ASTNode:
    payload = (
        MathPayload(content=value) if typ == ContentNodeType.DISPLAY_EQUATION
        else TablePayload(content=value) if typ == ContentNodeType.TABLE_SIMPLE
        else ParagraphPayload(content=value)
    )
    return ASTNode(node_id=name, sequence_id=1, node_type=typ, payload=payload)


def _units(ast, budget=24):
    chunker = TokenBudgetChunker(WordEstimator(), ChunkPolicy(max_tokens=budget, prompt_overhead_tokens=0))
    return chunker.chunk_group(SemanticGroup(structural_path=(), context_id="G3R1", nodes=list(ast)), 1)


def test_g3_r1_single_translate_cannot_be_disguised_as_preserve():
    ast = [_node("prose", ContentNodeType.PARAGRAPH, "Scientific prose to translate.")]
    unit, = _units(ast)
    assert unit.chunk_type == TranslationTaskType.TRANSLATE
    with pytest.raises(ValueError, match="G3_TASK_POLICY_MISMATCH"):
        ChunkPlan.build("doc", "gen", ast, [replace(unit, chunk_type=TranslationTaskType.PRESERVE)])


def test_g3_r1_protected_equation_cannot_be_disguised_as_translate():
    ast = [_node("equation", ContentNodeType.DISPLAY_EQUATION, r"E=mc^2")]
    unit, = _units(ast)
    assert unit.chunk_type == TranslationTaskType.PRESERVE
    with pytest.raises(ValueError, match="G3_TASK_POLICY_MISMATCH"):
        ChunkPlan.build("doc", "gen", ast, [replace(unit, chunk_type=TranslationTaskType.TRANSLATE)])


def test_g3_r1_partial_table_cannot_be_disguised_as_preserve():
    ast = [_node("table", ContentNodeType.TABLE_SIMPLE, "| a | b |")]
    unit, = _units(ast)
    assert unit.chunk_type == TranslationTaskType.PARTIAL
    with pytest.raises(ValueError, match="G3_TASK_POLICY_MISMATCH"):
        ChunkPlan.build("doc", "gen", ast, [replace(unit, chunk_type=TranslationTaskType.PRESERVE)])


def test_g3_r1_co_located_segments_use_original_source_bytes_as_payload():
    text = "Alpha one. Beta two. Gamma three."
    ast = [_node("paragraph", ContentNodeType.PARAGRAPH, text)]
    units = _units(ast, budget=4)
    plan = ChunkPlan.build("doc", "gen", ast, units)
    paired = [u for u in plan.units if len(u.members) > 1]
    assert paired, "Fixture no produjo segmentos hermanos en un mismo chunk"
    for unit in paired:
        assert len({m.node_id for m in unit.members}) == 1
        assert unit.target_payload == "".join(m.source_text for m in unit.members)
    assert "".join(m.source_text for u in units for m in u.members) == text
