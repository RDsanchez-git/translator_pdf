"""G3-B4/3a: mocked provider + real queue.db; no Groq/OCR/daemon.

Exercises the bridge-to-receipt seam without ever enabling publication or FSM.
"""
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from threading import Semaphore
from types import SimpleNamespace
from typing import cast
import time

import pytest

from apps.llm_workers.sync_bridge import SyncProviderBridge
from apps.llm_workers.routing import LLMProvider
from apps.llm_workers.prompt_builder import PromptBuilder
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, MathPayload, ParagraphPayload, TranslationTaskType
from core.ast.grouper import SemanticGroup
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from runtime.chunk_staging import stage_claimed_unit
from core.chunking.result_contract import parse_chunk_response
from infra.db.control_repo import ControlPlaneRepository

ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return len(text.split())


def _fixture():
    nodes = [
        ASTNode(node_id="math", sequence_id=1, node_type=ContentNodeType.DISPLAY_EQUATION,
                strategy=TranslationStrategy.PASSTHROUGH, payload=MathPayload(content="E=mc^2")),
        ASTNode(node_id="a", sequence_id=2, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Alpha.")),
        ASTNode(node_id="b", sequence_id=3, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content=" Beta.")),
    ]
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0),
    ).chunk_group(SemanticGroup(structural_path=(), context_id="ctx", nodes=nodes), 1)
    plan = ChunkPlan.build("doc_b4_3a", "ast_b4_3a", nodes, units)
    assert len(plan.units) == 2
    return nodes, plan


def _response(plan, unit, *, bad_hash=False):
    return json.dumps({
        "schema_version": 1, "document_id": plan.document_id,
        "ast_hash": plan.ast_hash, "manifest_sha256": "x" * 64 if bad_hash else plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [{
            "node_id": m.node_id, "segment_index": m.segment_index,
            "source_sha256": sha256(m.source_text.encode("utf8")).hexdigest(),
            "translated_text": f"Traduccion-{i}",
        } for i, m in enumerate(unit.members)],
    }, ensure_ascii=False, separators=(",", ":"))


class _Processor:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def execute_chunk(self, plan, unit):
        self.calls.append((plan, unit))
        return self.content


@pytest.fixture
def queue(tmp_path):
    nodes, plan = _fixture()
    connection = sqlite3.connect(tmp_path / "queue.db")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    repo = ControlPlaneRepository(connection)
    repo.enqueue_chunk_plan(plan, nodes)
    try:
        yield SimpleNamespace(repo=repo, db=connection, ast=nodes, plan=plan)
    finally:
        connection.close()


def _get_lease(q, wanted):
    leases = [q.repo.pick_task("worker_b43", q.plan.document_id, q.plan.ast_hash)
              for _ in q.plan.units]
    assert all(leases)
    return next(lease for lease in leases if lease.node_id == wanted.chunk_id)


def test_translation_members_are_staged_not_acked(queue):
    unit = next(u for u in queue.plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    lease = _get_lease(queue, unit)
    raw = _response(queue.plan, unit)
    proc = _Processor(raw)
    assert stage_claimed_unit(queue.repo, queue.plan, queue.ast, unit, lease,
                              "worker_b43", proc, Semaphore(1)) is True
    assert proc.calls == [(queue.plan, unit)]
    assert queue.db.execute("SELECT task_state FROM chunk_tasks WHERE task_id=?",
                            (lease.task_id,)).fetchone()[0] == "RESULT_STAGED"
    assert queue.db.execute("SELECT raw_response,execution_id FROM chunk_result_receipts "
                            "WHERE task_id=?", (lease.task_id,)).fetchone() == (raw, lease.execution_id)
    assert len(parse_chunk_response(queue.plan, unit.chunk_id, raw).members) == 2
    assert queue.db.execute("SELECT COUNT(*) FROM chunk_tasks WHERE task_state='COMPLETED'").fetchone()[0] == 0


def test_preserve_unit_bypasses_provider_and_stages_null(queue):
    unit = next(u for u in queue.plan.units if u.chunk_type == TranslationTaskType.PRESERVE)
    lease = _get_lease(queue, unit)
    proc = _Processor("must not be used")
    assert stage_claimed_unit(queue.repo, queue.plan, queue.ast, unit, lease,
                              "worker_b43", proc, Semaphore(1))
    assert proc.calls == []
    assert queue.db.execute("SELECT raw_response,response_sha256 FROM chunk_result_receipts "
                            "WHERE task_id=?", (lease.task_id,)).fetchone() == (None, None)


def test_preserve_unit_accepts_no_processor(queue):
    unit = next(u for u in queue.plan.units if u.chunk_type == TranslationTaskType.PRESERVE)
    lease = _get_lease(queue, unit)
    assert stage_claimed_unit(queue.repo, queue.plan, queue.ast, unit, lease,
                              "worker_b43", None, Semaphore(1))
    assert queue.db.execute("SELECT raw_response,response_sha256 FROM chunk_result_receipts "
                            "WHERE task_id=?", (lease.task_id,)).fetchone() == (None, None)


def test_translation_unit_rejects_missing_processor_before_staging(queue):
    unit = next(u for u in queue.plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    lease = _get_lease(queue, unit)
    with pytest.raises(ValueError, match="G3_B4_3A_PROVIDER_REQUIRED"):
        stage_claimed_unit(queue.repo, queue.plan, queue.ast, unit, lease,
                           "worker_b43", None, Semaphore(1))
    assert queue.db.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0
    assert queue.db.execute("SELECT task_state FROM chunk_tasks WHERE task_id=?",
                            (lease.task_id,)).fetchone()[0] == "PROCESSING"


def test_malformed_response_never_stages_or_completes(queue):
    unit = next(u for u in queue.plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    lease = _get_lease(queue, unit)
    proc = _Processor(_response(queue.plan, unit, bad_hash=True))
    with pytest.raises(ValueError, match="G3_B3_RESPONSE_BINDING_MISMATCH"):
        stage_claimed_unit(queue.repo, queue.plan, queue.ast, unit, lease,
                           "worker_b43", proc, Semaphore(1))
    assert queue.db.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0
    assert queue.db.execute("SELECT task_state FROM chunk_tasks WHERE task_id=?",
                            (lease.task_id,)).fetchone()[0] == "PROCESSING"


@pytest.mark.parametrize("mutation", ["wrong_chunk", "wrong_task", "expired"])
def test_bad_lease_rejected_before_provider(queue, mutation):
    from dataclasses import replace
    unit = next(u for u in queue.plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    lease = _get_lease(queue, unit)
    if mutation == "wrong_chunk":
        lease = replace(lease, node_id="other_chunk")
    elif mutation == "wrong_task":
        lease = replace(lease, task_id="other_task")
    else:
        lease = replace(lease, lease_expires_at=time.time() - 1)
    proc = _Processor(_response(queue.plan, unit))
    with pytest.raises(ValueError, match="G3_B4_3A_"):
        stage_claimed_unit(queue.repo, queue.plan, queue.ast, unit, lease,
                           "worker_b43", proc, Semaphore(1))
    assert proc.calls == []


def test_database_fence_remains_authoritative_after_provider(queue):
    unit = next(u for u in queue.plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    lease = _get_lease(queue, unit)
    class _ExpireDuringInference(_Processor):
        def execute_chunk(self, plan, unit):
            queue.db.execute("UPDATE chunk_tasks SET lease_expires_at=? WHERE task_id=?",
                             (time.time() - 2, lease.task_id))
            queue.db.commit()
            return super().execute_chunk(plan, unit)
    proc = _ExpireDuringInference(_response(queue.plan, unit))
    with pytest.raises(ValueError, match="G3_B3_2_LEASE_FENCE_REJECTED"):
        stage_claimed_unit(queue.repo, queue.plan, queue.ast, unit, lease,
                           "worker_b43", proc, Semaphore(1))
    assert queue.db.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0


class _FakeBuilder:
    model_name = "fake"
    prompt_version = "test"

    def __init__(self):
        self.seen = []

    def build(self, unit, resolved_context, target_lang_expansion=1.2):
        self.seen.append((unit, resolved_context, target_lang_expansion))
        envelope = SimpleNamespace(chunk_id=unit.chunk_id,
                                   schema=SimpleNamespace(payload=SimpleNamespace(content=unit.target_payload)))
        return SimpleNamespace(status="success", envelope=envelope)


class _FakeProvider:
    def __init__(self, content, *, drift=False):
        self.content = content
        self.drift = drift
        self.seen = []

    async def translate(self, envelope):
        self.seen.append(envelope)
        return SimpleNamespace(chunk_id="wrong" if self.drift else envelope.chunk_id,
                               content=self.content)


def _bridge(provider: _FakeProvider, builder: _FakeBuilder) -> SyncProviderBridge:
    # The focused fakes expose only the seam exercised by these tests.
    return SyncProviderBridge(cast(LLMProvider, provider), cast(PromptBuilder, builder))


def test_bridge_prompt_contains_manifest_binding_and_all_member_sources():
    nodes, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    builder = _FakeBuilder()
    provider = _FakeProvider(_response(plan, unit))
    bridge = _bridge(provider, builder)
    try:
        assert bridge.execute_chunk(plan, unit) == provider.content
    finally:
        bridge.shutdown()
    assert len(provider.seen) == 1
    prompted, context, expansion = builder.seen[0]
    body = json.loads(prompted.target_payload)
    assert body["response_binding"] == {
        "schema_version": 1, "document_id": plan.document_id, "ast_hash": plan.ast_hash,
        "manifest_sha256": plan.digest, "chunk_id": unit.chunk_id,
    }
    assert [m["source_text"] for m in body["members"]] == [m.source_text for m in unit.members]
    assert prompted.payload_sha256 == sha256(prompted.target_payload.encode("utf8")).hexdigest()
    assert prompted.chunk_id == unit.chunk_id
    assert prompted.target_payload != unit.target_payload
    assert unit.target_payload == "Alpha.\n\n Beta."
    assert expansion == 2.0


@pytest.mark.parametrize("mutation", ["plain_text", "wrong_chunk", "bad_response"])
def test_bridge_rejects_unbound_provider_output(mutation):
    nodes, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    content = "traduccion libre" if mutation == "plain_text" else _response(plan, unit, bad_hash=mutation == "bad_response")
    bridge = _bridge(_FakeProvider(content, drift=mutation == "wrong_chunk"), _FakeBuilder())
    try:
        with pytest.raises(ValueError):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()


def test_bridge_preserve_unit_is_never_sent():
    nodes, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.PRESERVE)
    provider = _FakeProvider("unused")
    bridge = _bridge(provider, _FakeBuilder())
    try:
        with pytest.raises(ValueError, match="G3_B4_3A_PRESERVE_PROVIDER_FORBIDDEN"):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()
    assert provider.seen == []


def _fixture_with_inline_math():
    nodes = [
        ASTNode(node_id="formula_a", sequence_id=1, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Energy $E=mc^2$ remains.")),
        ASTNode(node_id="formula_b", sequence_id=2, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content=" And $x\\alpha$ varies.")),
    ]
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0),
    ).chunk_group(SemanticGroup(structural_path=(), context_id="math", nodes=nodes), 1)
    plan = ChunkPlan.build("doc_math", "ast_math", nodes, units)
    assert len(plan.units) == 1 and len(plan.units[0].members) == 2
    return plan, plan.units[0]


def test_bridge_masks_and_restores_exact_inline_math_in_each_member():
    plan, unit = _fixture_with_inline_math()
    builder = _FakeBuilder()
    member_response = json.loads(_response(plan, unit))
    member_response["members"][0]["translated_text"] = "Energia __MATH_0__ se mantiene."
    member_response["members"][1]["translated_text"] = "Y __MATH_1__ varia."
    provider = _FakeProvider(json.dumps(member_response, ensure_ascii=False))
    bridge = _bridge(provider, builder)
    try:
        restored = bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()
    prompt = json.loads(builder.seen[0][0].target_payload)
    assert prompt["members"][0]["source_text"] == "Energy __MATH_0__ remains."
    assert prompt["members"][1]["source_text"] == " And __MATH_1__ varies."
    assert prompt["transport"]["root_key"] == "content"
    values = [m.translated_text for m in parse_chunk_response(plan, unit.chunk_id, restored).members]
    assert values == ["Energia $E=mc^2$ se mantiene.", "Y $x\\alpha$ varia."]


@pytest.mark.parametrize("mutation", ["dropped", "duplicated", "changed_case"])
def test_bridge_rejects_lost_or_modified_math_token(mutation):
    plan, unit = _fixture_with_inline_math()
    raw = json.loads(_response(plan, unit))
    value = {"dropped": "Formula perdida", "duplicated": "__MATH_0__ y __MATH_0__",
             "changed_case": "__math_0__"}[mutation]
    raw["members"][0]["translated_text"] = value
    raw["members"][1]["translated_text"] = "Y __MATH_1__ varia"
    provider = _FakeProvider(json.dumps(raw))
    bridge = _bridge(provider, _FakeBuilder())
    try:
        with pytest.raises(ValueError, match="G3_B4_3A_MATH_TOKEN_LOST_OR_DUPLICATED"):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()


def test_openai_dialect_unwraps_content_json_string_for_g3():
    # Checks actual renderer and network dialect; no HTTP or SDK calls.
    from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
    from core.prompting.renderer import PromptRenderer
    from core.prompting.models import PromptSchema, PromptContext, PromptPayload
    from core.prompting.intent_mapper import PromptIntentMapper
    from core.prompting.constraint_factory import ConstraintFactory

    nodes, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    schema = PromptSchema(
        intent=PromptIntentMapper.map_from_task(unit.chunk_type),
        context=PromptContext(chunk_index=unit.chunk_index, depth=0, breadcrumbs=[], is_pruned=False),
        constraints=ConstraintFactory.create_for_task(unit.chunk_type),
        payload=PromptPayload(content="G3 transport test"),
    )
    rendered = PromptRenderer.render(schema)
    dialect = OpenAICompatibleDialect()
    assert rendered.expected_output_key == "content"
    assert dialect.build_request_kwargs(rendered)["response_format"]["type"] == "json_object"
    inner = _response(plan, unit)
    raw_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({"content": inner})),
                                 finish_reason="stop")],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20),
    )
    parsed = dialect.parse_response(raw_response, unit.chunk_id, 10.0, rendered.expected_output_key)
    assert parsed.content == inner
    assert len(parse_chunk_response(plan, unit.chunk_id, parsed.content).members) == 2


def test_openai_dialect_plain_inner_object_is_rejected_by_g3_parser():
    from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
    nodes, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=_response(plan, unit)),
                                 finish_reason="stop")], usage=None,
    )
    from core.execution.exceptions import DialectParsingError
    with pytest.raises(DialectParsingError):
        OpenAICompatibleDialect().parse_response(response, unit.chunk_id, 1.0, "content")


@pytest.mark.parametrize('source, error', [
    ('Broken $E=mc^2', 'G3_B4_3A_UNBALANCED_INLINE_MATH'),
    ('Literal __MATH_0__ plus $x$', 'G3_B4_3A_MATH_TOKEN_COLLISION'),
])
def test_math_source_uncertain_fails_before_provider(source, error):
    ast = [ASTNode(node_id='unsafe', sequence_id=1,
                   node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content=source))]
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0),
    ).chunk_group(SemanticGroup(structural_path=(), context_id='ctx', nodes=ast), 1)
    plan = ChunkPlan.build('doc_uncertain', 'ast_uncertain', ast, units)
    provider = _FakeProvider('should not be used')
    bridge = _bridge(provider, _FakeBuilder())
    try:
        with pytest.raises(ValueError, match=error):
            bridge.execute_chunk(plan, plan.units[0])
    finally:
        bridge.shutdown()
    assert provider.seen == []


def test_math_token_cannot_move_between_two_members():
    plan, unit = _fixture_with_inline_math()
    raw = json.loads(_response(plan, unit))
    # Both members have one formula. Reusing local __MATH_0__ silently hid
    # this displacement in R2; G3 now requires unit-global tokens.
    raw["members"][0]["translated_text"] = "Wrong __MATH_1__"
    raw["members"][1]["translated_text"] = "Wrong __MATH_0__"
    provider = _FakeProvider(json.dumps(raw))
    bridge = _bridge(provider, _FakeBuilder())
    try:
        with pytest.raises(ValueError, match="G3_B4_3A_MATH_TOKEN_LOST_OR_DUPLICATED"):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()


def test_math_token_injection_is_rejected_even_when_expected_tokens_survive():
    plan, unit = _fixture_with_inline_math()
    raw = json.loads(_response(plan, unit))
    raw["members"][0]["translated_text"] = "OK __MATH_0__ EXTRA __MATH_999__"
    raw["members"][1]["translated_text"] = "OK __MATH_1__"
    bridge = _bridge(_FakeProvider(json.dumps(raw)), _FakeBuilder())
    try:
        with pytest.raises(ValueError, match="G3_B4_3A_MATH_TOKEN_LOST_OR_DUPLICATED"):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()


def test_hallucinated_math_token_rejected_in_no_math_unit():
    _nodes, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    raw = json.loads(_response(plan, unit))
    raw["members"][0]["translated_text"] = "Hallucinated __MATH_0__"
    bridge = _bridge(_FakeProvider(json.dumps(raw)), _FakeBuilder())
    try:
        with pytest.raises(ValueError, match="G3_B4_3A_MATH_TOKEN_LOST_OR_DUPLICATED"):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()
