"""G3-B1: contrato de identidad del dominio, sin SQLite ni proveedor."""
from dataclasses import replace
import json

import pytest
from core.ast.models import ASTNode, ParagraphPayload, TranslationTaskType
from core.ast.enums import ContentNodeType
from core.ast.grouper import SemanticGroup
from core.chunking.semantic_chunking import TokenBudgetChunker, ChunkPolicy
from core.chunking.manifest_contract import ChunkPlan


class Estimator:
    def estimate_tokens(self, text: str) -> int:
        return len(text.split())


def node(node_id: str, sequence: int, text: str) -> ASTNode:
    return ASTNode(node_id=node_id, sequence_id=sequence, node_type=ContentNodeType.PARAGRAPH,
                   payload=ParagraphPayload(content=text))


def plan(ast, *, budget=30):
    chunker = TokenBudgetChunker(Estimator(), ChunkPolicy(max_tokens=budget, prompt_overhead_tokens=0))
    units = chunker.chunk_group(SemanticGroup(structural_path=(), context_id="ctx", nodes=list(ast)), 1)
    return ChunkPlan.build("doc-g3", "ast-g3", ast, units)


def test_g3_t01_two_nodes_one_chunk_distinct_member_identities():
    ast = [node("node_a", 1, "Alpha scientific sentence."), node("node_b", 2, "Beta scientific sentence.")]
    p = plan(ast)
    assert len(p.units) == 1
    assert p.units[0].node_count == 2
    assert [m.node_id for m in p.units[0].members] == ["node_a", "node_b"]
    assert p.units[0].chunk_id not in {"node_a", "node_b"}
    assert p.units[0].members[0].source_text != p.units[0].members[1].source_text


def test_g3_t02_deterministic_roundtrip_and_generation_binding(tmp_path):
    ast = [node("node_a", 1, "A short text."), node("node_b", 2, "Another text.")]
    p = plan(ast)
    saved = tmp_path / "manifest.json"
    saved.write_text(p.to_json(), encoding="utf-8")
    restored = ChunkPlan.from_json(saved.read_text(encoding="utf-8"), ast, document_id="doc-g3", ast_hash="ast-g3")
    assert restored == p and restored.digest == p.digest
    tampered = json.loads(saved.read_text(encoding="utf-8"))
    tampered["ast_hash"] = "another-generation"
    with pytest.raises(ValueError, match="GENERATION_MISMATCH"):
        ChunkPlan.from_json(json.dumps(tampered), ast, document_id="doc-g3", ast_hash="ast-g3")
    assert plan(ast).digest == p.digest


def test_g3_t03_sentence_overflow_preserves_parent_lineage_and_all_source_bytes():
    source = "Alpha first sentence. Beta second sentence. Gamma third sentence."
    ast = [node("parent_paragraph", 1, source)]
    p = plan(ast, budget=4)
    members = [m for u in p.units for m in u.members]
    assert len(p.units) >= 2
    assert len(members) == 3
    assert all(m.node_id == "parent_paragraph" for m in members)
    assert [m.segment_index for m in members] == [0, 1, 2]
    assert all(m.segment_count == 3 for m in members)
    assert "".join(m.source_text for m in members) == source
    assert ChunkPlan.from_json(p.to_json(), ast, document_id="doc-g3", ast_hash="ast-g3") == p


def test_g3_reject_missing_extra_duplicate_member_and_payload_tampering():
    ast = [node("node_a", 1, "Alpha sentence."), node("node_b", 2, "Beta sentence.")]
    p = plan(ast)
    u = p.units[0]
    with pytest.raises(ValueError):
        ChunkPlan.build("doc-g3", "ast-g3", ast, [replace(u, members=u.members[:1], node_count=1)])
    with pytest.raises(ValueError):
        ChunkPlan.build("doc-g3", "ast-g3", ast, [replace(u, members=(u.members[0], u.members[0]), node_count=2)])
    with pytest.raises(ValueError):
        ChunkPlan.build("doc-g3", "ast-g3", ast, [replace(u, target_payload="tampered")])


def test_g3_fails_closed_if_sentence_cannot_fit_budget():
    ast = [node("node_a", 1, "This sentence is too long for the configured hard budget.")]
    with pytest.raises(ValueError, match="G3_SENTENCE_EXCEEDS_BUDGET"):
        plan(ast, budget=2)


def test_g3_preserve_and_omit_are_not_sent_as_regular_translate_members():
    from core.ast.enums import TranslationStrategy
    from core.ast.models import MathPayload
    kept = node("narrative", 1, "A text to translate.")
    preserved = ASTNode(node_id="math", sequence_id=2, node_type=ContentNodeType.DISPLAY_EQUATION,
                        payload=MathPayload(content=r"E=mc^2"), strategy=TranslationStrategy.PASSTHROUGH)
    omitted = ASTNode(node_id="omitted", sequence_id=3, node_type=ContentNodeType.PARAGRAPH,
                      payload=ParagraphPayload(content="discard"), strategy=TranslationStrategy.OMIT)
    p = plan([kept, preserved, omitted])
    assert [u.chunk_type for u in p.units] == [TranslationTaskType.TRANSLATE, TranslationTaskType.PRESERVE]
    assert [m.node_id for u in p.units for m in u.members] == ["narrative", "math"]
    assert ChunkPlan.from_json(p.to_json(), [kept, preserved, omitted], document_id="doc-g3", ast_hash="ast-g3") == p


def test_g3_fail_closed_on_defer_strategy():
    from core.ast.enums import TranslationStrategy
    deferred = ASTNode(node_id="defer", sequence_id=1, node_type=ContentNodeType.PARAGRAPH,
                       payload=ParagraphPayload(content="defer to future"), strategy=TranslationStrategy.DEFER)
    with pytest.raises(ValueError, match="G3_UNRESOLVED_STRATEGY"):
        plan([deferred])


def test_g3_rejects_unimplemented_overflow_policy_instead_of_overbudget_unit():
    from core.ast.models import OverflowPolicy
    ast = [node("node_a", 1, "This paragraph greatly exceeds the tiny token budget.")]
    chunker = TokenBudgetChunker(Estimator(), ChunkPolicy(max_tokens=2, prompt_overhead_tokens=0,
                                                          overflow_policy=OverflowPolicy.BY_PARAGRAPH))
    with pytest.raises(ValueError, match="G3_UNSUPPORTED_OVERFLOW_POLICY"):
        chunker.chunk_group(SemanticGroup(structural_path=(), context_id="ctx", nodes=ast), 1)
