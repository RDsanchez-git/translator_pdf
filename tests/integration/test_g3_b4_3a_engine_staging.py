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
from apps.llm_workers.g3_admission import G3PreEffectAdmission, build_groq_request_kwargs
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, MathPayload, ParagraphPayload, TranslationTaskType
from core.ast.grouper import SemanticGroup
from core.context.snapshot_contract import ContextSnapshotV1, ContextBreadcrumbV1
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
    ).chunk_group(SemanticGroup(structural_path=("root",), context_id="CTX_AABBCCDDEEFF", nodes=nodes), 1)
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
        envelope = SimpleNamespace(
            chunk_id=unit.chunk_id, target_provider="primary",
            schema=SimpleNamespace(payload=SimpleNamespace(content=unit.target_payload)),
        )
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


def _bridge(
    provider: _FakeProvider, builder: PromptBuilder, plan: ChunkPlan,
    *, source_language: str = "en", target_language: str = "es",
    effective_config_sha256: str | None = None,
    pre_effect_admission: object | None = None,
) -> SyncProviderBridge:
    # These existing tests exercise transport/placeholder semantics. They
    # inject explicit synthetic snapshots; real producer verification is
    # exercised independently in test_w08_ocr_g3_context_wiring.py.
    snapshots = {
        unit.context_id: ContextSnapshotV1(
            document_id=plan.document_id, ast_hash=plan.ast_hash,
            context_id=unit.context_id,
            breadcrumbs=(ContextBreadcrumbV1(0, "[ROOT_DOCUMENT_CONTEXT]"),),
        )
        for unit in plan.units if unit.chunk_type != TranslationTaskType.PRESERVE
    }
    return SyncProviderBridge(
        cast(LLMProvider, provider), cast(PromptBuilder, builder),
        context_snapshots=snapshots,
        source_language=source_language, target_language=target_language,
        effective_config_sha256=effective_config_sha256,
        pre_effect_admission=cast("G3PreEffectAdmission | None", pre_effect_admission),
    )


def test_bridge_prompt_contains_manifest_binding_and_all_member_sources():
    nodes, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    builder = _FakeBuilder()
    provider = _FakeProvider(_response(plan, unit))
    bridge = _bridge(provider, builder, plan)
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
    bridge = _bridge(_FakeProvider(content, drift=mutation == "wrong_chunk"), _FakeBuilder(), plan)
    expected_error = {
        "plain_text": "G3_B3_INVALID_RESPONSE_JSON",
        "wrong_chunk": "G3_B4_3A_PROVIDER_CHUNK_DRIFT",
        "bad_response": "G3_B3_RESPONSE_BINDING_MISMATCH",
    }[mutation]
    try:
        with pytest.raises(ValueError, match=expected_error):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()


def test_bridge_preserve_unit_is_never_sent():
    nodes, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.PRESERVE)
    provider = _FakeProvider("unused")
    bridge = _bridge(provider, _FakeBuilder(), plan)
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
    ).chunk_group(SemanticGroup(structural_path=("root",), context_id="CTX_001122334455", nodes=nodes), 1)
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
    bridge = _bridge(provider, builder, plan)
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
    bridge = _bridge(provider, _FakeBuilder(), plan)
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
    # B02.4 rejects malformed delimiters inside InlineMathProtector.mask first.
    ('Broken $E=mc^2', 'B024_UNCLOSED_MATH'),
    ('Literal __MATH_0__ plus $x$', 'G3_B4_3A_MATH_TOKEN_COLLISION'),
])
def test_math_source_uncertain_fails_before_provider(source, error):
    ast = [ASTNode(node_id='unsafe', sequence_id=1,
                   node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content=source))]
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0),
    ).chunk_group(SemanticGroup(structural_path=("root",), context_id="CTX_AABBCCDDEEFF", nodes=ast), 1)
    plan = ChunkPlan.build('doc_uncertain', 'ast_uncertain', ast, units)
    provider = _FakeProvider('should not be used')
    bridge = _bridge(provider, _FakeBuilder(), plan)
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
    bridge = _bridge(provider, _FakeBuilder(), plan)
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
    bridge = _bridge(_FakeProvider(json.dumps(raw)), _FakeBuilder(), plan)
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
    bridge = _bridge(_FakeProvider(json.dumps(raw)), _FakeBuilder(), plan)
    try:
        with pytest.raises(ValueError, match="G3_B4_3A_MATH_TOKEN_LOST_OR_DUPLICATED"):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()


def test_pppr_w32_wire_request_contains_explicit_en_es_generation_intent():
    """R1/R2: inspect the real renderer + dialect, not a provider mock string."""
    from core.finops.measurement import InferenceMeasurementService
    from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
    from core.prompting.renderer import PromptRenderer
    from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect

    _ast, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    provider = _FakeProvider(_response(plan, unit))
    builder = PromptBuilder(
        model_name="offline-only", prompt_version="wave-3.2",
        measurement_service=InferenceMeasurementService(_Estimator()),
        budget_calculator=PromptBudgetCalculator(),
        compression_policy=StandardCompressionPolicy(),
    )
    snapshots = {
        unit.context_id: ContextSnapshotV1(
            document_id=plan.document_id, ast_hash=plan.ast_hash,
            context_id=unit.context_id,
            breadcrumbs=(ContextBreadcrumbV1(0, "[ROOT_DOCUMENT_CONTEXT]"),),
        ),
    }
    bridge = SyncProviderBridge(
        cast(LLMProvider, provider), builder, context_snapshots=snapshots,
        source_language="en", target_language="es",
    )
    try:
        assert bridge.execute_chunk(plan, unit) == provider.content
    finally:
        bridge.shutdown()

    assert len(provider.seen) == 1
    wire = OpenAICompatibleDialect().build_request_kwargs(
        PromptRenderer.render(provider.seen[0].schema)
    )
    assert len(wire["messages"]) == 2
    body = json.loads(wire["messages"][1]["content"])
    assert body["language_intent"] == {
        "source_language": "en", "target_language": "es",
    }
    assert "English (en) into Spanish (es)" in body["instructions"]
    assert wire["response_format"] == {"type": "json_object"}
    assert body["response_binding"]["ast_hash"] == plan.ast_hash
    assert body["response_binding"]["chunk_id"] == unit.chunk_id


@pytest.mark.parametrize(
    ("source", "target"),
    [("", "es"), ("en", ""), ("fr", "es"), ("en", "fr"), ("ES", "en")],
)
def test_pppr_w32_invalid_language_intent_never_calls_provider(source, target):
    from core.execution.exceptions import G3ExternalEffectNotStartedError

    _ast, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    provider = _FakeProvider(_response(plan, unit))
    bridge = _bridge(
        provider, _FakeBuilder(), plan,
        source_language=source, target_language=target,
    )
    try:
        with pytest.raises(
            G3ExternalEffectNotStartedError,
            match="PPPR_G3_LANGUAGE_INTENT_REQUIRED_EN_ES",
        ):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()
    assert provider.seen == []


def test_pppr_w32_real_budget_switch_model_is_rejected_before_provider():
    """R4: a real SWITCH_MODEL is not physical fallback admission."""
    from core.finops.measurement import InferenceMeasurementService
    from core.validation.budget import (
        PromptBudgetCalculator, StandardCompressionPolicy,
    )
    from core.execution.exceptions import G3ExternalEffectNotStartedError

    _ast, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    builder = PromptBuilder(
        model_name="primary-offline", prompt_version="wave32",
        measurement_service=InferenceMeasurementService(_Estimator()),
        budget_calculator=PromptBudgetCalculator(
            primary_window_limit=1, fallback_window_limit=8192,
            min_output_reserve=256, max_output_reserve=4096,
        ),
        compression_policy=StandardCompressionPolicy(),
    )
    provider = _FakeProvider(_response(plan, unit))
    bridge = _bridge(provider, builder, plan)
    try:
        with pytest.raises(
            G3ExternalEffectNotStartedError,
            match="PPPR_G3_FALLBACK_BACKEND_NOT_ACCREDITED",
        ):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()
    assert provider.seen == []


def test_pppr_w32_retired_product_model_cannot_call_provider():
    """R3: documentation says Groq retired llama3-70b-8192 2025-08-30."""
    from core.finops.measurement import InferenceMeasurementService
    from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
    from core.execution.exceptions import G3ExternalEffectNotStartedError

    _ast, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    provider = _FakeProvider(_response(plan, unit))
    builder = PromptBuilder(
        model_name="llama3-70b-8192", prompt_version="v1.0",
        measurement_service=InferenceMeasurementService(_Estimator()),
        budget_calculator=PromptBudgetCalculator(),
        compression_policy=StandardCompressionPolicy(),
    )
    bridge = _bridge(
        provider, builder, plan, effective_config_sha256="a" * 64,
    )
    try:
        with pytest.raises(
            G3ExternalEffectNotStartedError,
            match="PPPR_G3_PRIMARY_MODEL_DEPRECATED",
        ):
            bridge.execute_chunk(plan, unit)
    finally:
        bridge.shutdown()
    assert provider.seen == []

 

class _CharBoundEstimator:
    """Synthetic upper bound in the fake one-character-per-token model."""
    def estimate_tokens(self, text: str) -> int:
        return len(text)


def _w32_fake_admission(**changes: object) -> G3PreEffectAdmission:
    from dataclasses import replace
    from decimal import Decimal

    policy = G3PreEffectAdmission(
        provider_id="groq", model_name="offline-synthetic",
        root_config_sha256="a" * 64,
        input_limit=50000, output_limit=4096, context_window=60000,
        input_estimator=_CharBoundEstimator(),
        estimator_evidence_ref="FAKE_OFFLINE_CHAR_ESTIMATOR",
        egress_authorization_ref="FAKE_OFFLINE_EGRESS", data_scope_ref="FAKE_DATA",
        purpose_ref="FAKE_EN_ES", retention_ref="FAKE_RETENTION",
        training_use_ref="FAKE_TRAINING",
        budget_authorization_ref="FAKE_OFFLINE_BUDGET",
        price_evidence_ref="FAKE_NO_COMMERCIAL_PRICES",
        input_price_per_token=Decimal("0"), output_price_per_token=Decimal("0"),
        authorized_max_cost=Decimal("0"),
    )
    return replace(policy, **changes)


def _w32_product_bridge(policy: G3PreEffectAdmission | None):
    from core.finops.measurement import InferenceMeasurementService
    from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy

    _ast, plan = _fixture()
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    provider = _FakeProvider(_response(plan, unit))
    builder = PromptBuilder(
        model_name="offline-synthetic", prompt_version="w32",
        measurement_service=InferenceMeasurementService(_Estimator()),
        budget_calculator=PromptBudgetCalculator(),
        compression_policy=StandardCompressionPolicy(),
    )
    bridge = _bridge(
        provider, builder, plan, effective_config_sha256="a" * 64,
        pre_effect_admission=policy,
    )
    return bridge, provider, plan, unit


def test_pppr_w32_real_request_admission_bound_to_generation_and_output_cap():
    """Synthetic approval exercises real renderer, dialect, and bridge, no SDK."""
    from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect

    from core.execution.effect_guard import g3_admission_audit_writer

    attestations: list[tuple[str, str]] = []
    bridge, provider, plan, unit = _w32_product_bridge(_w32_fake_admission())
    token = g3_admission_audit_writer.set(
        lambda generation, audit: attestations.append((generation, audit))
    )
    try:
        response, generation_sha = bridge.execute_chunk_with_generation(plan, unit)
    finally:
        g3_admission_audit_writer.reset(token)
        bridge.shutdown()
    assert len(attestations) == 1
    assert attestations[0][0] == generation_sha
    decision = json.loads(attestations[0][1])
    assert decision["contract"] == "PPPR_G3_ADMISSION_V1"
    assert decision["egress_authorization_ref"] == "FAKE_OFFLINE_EGRESS"
    assert decision["estimator_evidence_ref"] == "FAKE_OFFLINE_CHAR_ESTIMATOR"
    assert decision["budget_authorization_ref"] == "FAKE_OFFLINE_BUDGET"
    assert decision["input_tokens"] <= decision["input_limit"]
    assert decision["upper_bound_cost"] == "0"
    assert "Alpha." not in attestations[0][1]
    assert response == provider.content
    assert len(provider.seen) == 1 and len(generation_sha) == 64
    kwargs, _ = build_groq_request_kwargs(
        provider.seen[0], OpenAICompatibleDialect(),
    )
    assert kwargs["model"] == "offline-synthetic"
    assert kwargs["max_completion_tokens"] == provider.seen[0].budget_stats.reserved_tokens
    assert kwargs["messages"][1]["content"].find('"language_intent"') >= 0


@pytest.mark.parametrize(
    ("override", "expected"),
    [
        ({"input_limit": 1}, "PPPR_G3_INPUT_LIMIT_EXCEEDED"),
        ({"output_limit": 1}, "PPPR_G3_OUTPUT_LIMIT_EXCEEDED"),
        ({"context_window": 256}, "PPPR_G3_CONTEXT_WINDOW_EXCEEDED"),
        ({"estimator_evidence_ref": ""}, "PPPR_G3_ESTIMATOR_NOT_ACCREDITED"),
        ({"egress_authorization_ref": ""}, "PPPR_G3_EGRESS_NOT_AUTHORIZED"),
        ({"data_scope_ref": ""}, "PPPR_G3_EGRESS_NOT_AUTHORIZED"),
        ({"retention_ref": ""}, "PPPR_G3_EGRESS_NOT_AUTHORIZED"),
        ({"training_use_ref": ""}, "PPPR_G3_EGRESS_NOT_AUTHORIZED"),
        ({"budget_authorization_ref": ""}, "PPPR_G3_BUDGET_NOT_AUTHORIZED"),
        ({"price_evidence_ref": ""}, "PPPR_G3_BUDGET_NOT_AUTHORIZED"),
        ({"model_name": "another-model"}, "PPPR_G3_ADMISSION_SELECTION_DRIFT"),
        ({"provider_id": "different-provider"}, "PPPR_G3_ADMISSION_SELECTION_DRIFT"),
        ({"root_config_sha256": "b"*64}, "PPPR_G3_ADMISSION_SELECTION_DRIFT"),
    ],
)
def test_pppr_w32_independent_limits_and_authorities_fail_pre_effect(
    override, expected,
):
    from core.execution.exceptions import G3ExternalEffectNotStartedError

    bridge, provider, plan, unit = _w32_product_bridge(
        _w32_fake_admission(**override),
    )
    try:
        with pytest.raises(G3ExternalEffectNotStartedError, match=expected):
            bridge.execute_chunk_with_generation(plan, unit)
    finally:
        bridge.shutdown()
    assert provider.seen == []


def test_pppr_w32_budget_ceiling_is_not_rpm_tpm_quota():
    from decimal import Decimal
    from core.execution.exceptions import G3ExternalEffectNotStartedError

    bridge, provider, plan, unit = _w32_product_bridge(_w32_fake_admission(
        input_price_per_token=Decimal("1"),
        authorized_max_cost=Decimal("0.1"),
    ))
    try:
        with pytest.raises(G3ExternalEffectNotStartedError, match="PPPR_G3_BUDGET_CAP_EXCEEDED"):
            bridge.execute_chunk_with_generation(plan, unit)
    finally:
        bridge.shutdown()
    assert provider.seen == []


def test_pppr_w32_product_default_missing_authorizations_blocks_provider():
    from core.execution.exceptions import G3ExternalEffectNotStartedError

    bridge, provider, plan, unit = _w32_product_bridge(None)
    try:
        with pytest.raises(
            G3ExternalEffectNotStartedError,
            match="PPPR_G3_ADMISSION_EVIDENCE_MISSING",
        ):
            bridge.execute_chunk_with_generation(plan, unit)
    finally:
        bridge.shutdown()
    assert provider.seen == []


def test_pppr_w32_admission_refs_not_conflated_with_scientific_identity():
    """Same wire request, different authority reference => different audit."""
    from dataclasses import replace
    from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect

    policy = _w32_fake_admission()
    bridge, provider, plan, unit = _w32_product_bridge(policy)
    from core.execution.effect_guard import g3_admission_audit_writer
    token = g3_admission_audit_writer.set(lambda generation, audit: None)
    try:
        bridge.execute_chunk_with_generation(plan, unit)
    finally:
        g3_admission_audit_writer.reset(token)
        bridge.shutdown()
    envelope = provider.seen[0]
    original = policy.verify(
        provider_id="groq", root_config_sha256="a"*64, envelope=envelope,
    )
    alternative = replace(policy, egress_authorization_ref="FAKE_OTHER_EGRESS").verify(
        provider_id="groq", root_config_sha256="a"*64, envelope=envelope,
    )
    assert original.request_sha256 == alternative.request_sha256
    assert original.audit_json != alternative.audit_json


def test_pppr_w32_durable_admission_joins_attempt_generation_and_receipt(queue):
    """Actual local control SQLite persists evidence before fake provider effect."""
    import sqlite3
    from threading import Semaphore

    policy = _w32_fake_admission()
    bridge, provider, plan, unit = _w32_product_bridge(policy)
    lease = queue.repo.pick_task("w32_audit", plan.document_id, plan.ast_hash)
    assert lease is not None
    if lease.node_id != unit.chunk_id:
        preserve = next(u for u in plan.units if u.chunk_id == lease.node_id)
        assert preserve.chunk_type == TranslationTaskType.PRESERVE
        assert stage_claimed_unit(
            queue.repo, plan, queue.ast, preserve, lease,
            "w32_audit", None, Semaphore(1),
        )
        lease = queue.repo.pick_task("w32_audit", plan.document_id, plan.ast_hash)
    assert lease is not None and lease.node_id == unit.chunk_id
    try:
        assert stage_claimed_unit(
            queue.repo, plan, queue.ast, unit, lease,
            "w32_audit", bridge, Semaphore(1),
        )
    finally:
        bridge.shutdown()
    assert len(provider.seen) == 1
    row = queue.db.execute(
        "SELECT execution_id,generation_sha256,decision_json,decision_sha256 "
        "FROM g3_admission_decisions WHERE task_id=?", (lease.task_id,),
    ).fetchone()
    assert row is not None
    execution_id, generation, audit_json, audit_sha = row
    assert execution_id == lease.execution_id and len(generation) == 64
    audit = json.loads(audit_json)
    assert audit["contract"] == "PPPR_G3_ADMISSION_V1"
    assert audit["budget_authorization_ref"] == "FAKE_OFFLINE_BUDGET"
    assert audit["input_limit"] == 50000
    assert audit_sha == sha256((generation + audit_json).encode()).hexdigest()
    assert queue.db.execute(
        "SELECT generation_sha256 FROM chunk_result_receipts WHERE task_id=?",
        (lease.task_id,),
    ).fetchone() == (generation,)
    assert "Alpha." not in audit_json
    # Evidence survives a fresh SQLite connection, not just a process buffer.
    path = queue.db.execute("PRAGMA database_list").fetchone()[2]
    with sqlite3.connect(path) as reopened:
        assert reopened.execute(
            "SELECT decision_sha256 FROM g3_admission_decisions "
            "WHERE task_id=? AND execution_id=?",
            (lease.task_id, execution_id),
        ).fetchone() == (audit_sha,)


@pytest.mark.parametrize(
    "invalid_amount",
    ["Infinity", "-Infinity", "NaN", "sNaN"],
)
@pytest.mark.parametrize(
    "field",
    ["input_price_per_token", "output_price_per_token", "authorized_max_cost"],
)
def test_pppr_w32_nonfinite_budget_denied_without_provider(field, invalid_amount):
    from decimal import Decimal
    from core.execution.exceptions import G3ExternalEffectNotStartedError

    bridge, provider, plan, unit = _w32_product_bridge(
        _w32_fake_admission(**{field: Decimal(invalid_amount)}),
    )
    try:
        with pytest.raises(
            G3ExternalEffectNotStartedError, match="PPPR_G3_BUDGET_NOT_AUTHORIZED",
        ) as error:
            bridge.execute_chunk_with_generation(plan, unit)
        assert error.value.permanent
    finally:
        bridge.shutdown()
    assert provider.seen == []


def test_pppr_w32_missing_audit_writer_fails_before_provider():
    from core.execution.exceptions import G3ExternalEffectNotStartedError
    bridge, provider, plan, unit = _w32_product_bridge(_w32_fake_admission())
    try:
        with pytest.raises(
            G3ExternalEffectNotStartedError,
            match="PPPR_G3_ADMISSION_AUDIT_WRITER_REQUIRED",
        ):
            bridge.execute_chunk_with_generation(plan, unit)
    finally:
        bridge.shutdown()
    assert provider.seen == []


@pytest.mark.integration
@pytest.mark.parametrize("scenario", ["approved", "missing_admission", "retired_model"])
def test_pppr_g5_real_bridge_http_fake_and_durable_admission(tmp_path, monkeypatch, scenario):
    """Real Groq SDK loopback, quota fence, bridge and durable receipt.

    Only the provider is a synthetic echo; no commercial authorization,
    production composition root, PDF compilation or recovery claim.
    """
    import asyncio
    from contextlib import closing
    import threading

    from apps.lab.g3_fake import DUMMY_KEY, FAKE_MODEL, FakeServer
    from apps.llm_workers.adapters import GroqProvider
    from apps.llm_workers.rate_limiter import QuotaManager, RateLimitedProvider
    from core.ast.hashing import compute_ast_hash
    from core.execution.exceptions import G3ExternalEffectNotStartedError
    from core.finops.measurement import InferenceMeasurementService
    from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
    from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy

    nodes, original = _fixture()
    plan = ChunkPlan.build(
        sha256(b"pppr-g5-synthetic-http-fixture").hexdigest(),
        compute_ast_hash(nodes), nodes, original.units,
    )
    db_path = tmp_path / "queue.db"
    root_config = sha256(b"PPPR_G5_HTTP_TEST_ONLY_OFFLINE_CONFIG").hexdigest()
    model = "llama3-70b-8192" if scenario == "retired_model" else FAKE_MODEL
    policy = None if scenario == "missing_admission" else _w32_fake_admission(
        provider_id="offline-test", model_name=FAKE_MODEL,
        root_config_sha256=root_config,
    )
    builder = PromptBuilder(
        model_name=model, prompt_version="pppr-g5-http-test",
        measurement_service=InferenceMeasurementService(_Estimator()),
        budget_calculator=PromptBudgetCalculator(),
        compression_policy=StandardCompressionPolicy(),
    )
    snapshots = {
        unit.context_id: ContextSnapshotV1(
            document_id=plan.document_id, ast_hash=plan.ast_hash,
            context_id=unit.context_id,
            breadcrumbs=(ContextBreadcrumbV1(0, "[ROOT_DOCUMENT_CONTEXT]"),),
        )
        for unit in plan.units if unit.chunk_type != TranslationTaskType.PRESERVE
    }

    with closing(sqlite3.connect(db_path)) as db:
        db.execute("PRAGMA foreign_keys=ON")
        db.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
        repo = ControlPlaneRepository(db)
        repo.enqueue_chunk_plan(plan, nodes)
        with FakeServer(("127.0.0.1", 0), db_path, max_requests=4) as server:
            port = server.server_address[1]
            # No environment-derived proxies; SDK destination must be loopback.
            for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                         "http_proxy", "https_proxy", "all_proxy"):
                monkeypatch.delenv(name, raising=False)
            monkeypatch.setenv("NO_PROXY", "127.0.0.1")
            monkeypatch.setenv("no_proxy", "127.0.0.1")
            monkeypatch.setenv("GROQ_BASE_URL", f"http://127.0.0.1:{port}")
            adapter = GroqProvider(DUMMY_KEY, OpenAICompatibleDialect())
            assert adapter._client.base_url.host == "127.0.0.1"
            assert adapter._client.base_url.port == port
            assert adapter._client.base_url.scheme == "http"
            provider = RateLimitedProvider(adapter, QuotaManager(1000, 200000))
            bridge = SyncProviderBridge(
                provider, builder, timeout_sec=15, context_snapshots=snapshots,
                effective_config_sha256=root_config, provider_id="offline-test",
                pre_effect_admission=policy,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                # Stage PRESERVE through the same adapter, with no HTTP effect.
                leases = [repo.pick_task("g5_http", plan.document_id, plan.ast_hash)
                          for _ in plan.units]
                assert all(leases)
                by_chunk = {lease.node_id: lease for lease in leases}
                preserve = next(u for u in plan.units if u.chunk_type == TranslationTaskType.PRESERVE)
                preserve_lease = by_chunk[preserve.chunk_id]
                assert stage_claimed_unit(
                    repo, plan, nodes, preserve, preserve_lease,
                    "g5_http", bridge, Semaphore(1),
                )
                assert server.requests == 0
                unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
                lease = by_chunk[unit.chunk_id]
                if scenario == "approved":
                    assert stage_claimed_unit(
                        repo, plan, nodes, unit, lease, "g5_http", bridge, Semaphore(1),
                    )
                    assert server.requests == 1
                else:
                    reason = ("PPPR_G3_ADMISSION_EVIDENCE_MISSING"
                              if scenario == "missing_admission"
                              else "PPPR_G3_PRIMARY_MODEL_DEPRECATED")
                    with pytest.raises(G3ExternalEffectNotStartedError, match=reason):
                        stage_claimed_unit(
                            repo, plan, nodes, unit, lease, "g5_http", bridge, Semaphore(1),
                        )
                    assert server.requests == 0
            finally:
                try:
                    asyncio.run_coroutine_threadsafe(
                        adapter._client.close(), bridge._loop,
                    ).result(timeout=5)
                finally:
                    bridge.shutdown()
                    server.shutdown()
                    thread.join(timeout=5)

        # Reopen independent connection; compare the attempt, admission and receipt.
        with closing(sqlite3.connect(db_path)) as reopened:
            assert reopened.execute(
                "SELECT raw_response,generation_sha256 FROM chunk_result_receipts WHERE task_id=?",
                (preserve_lease.task_id,),
            ).fetchone() == (None, None)
            assert reopened.execute(
                "SELECT COUNT(*) FROM g3_admission_decisions WHERE task_id=?",
                (preserve_lease.task_id,),
            ).fetchone() == (0,)
            row = reopened.execute(
                "SELECT execution_id,generation_sha256,decision_json,decision_sha256 "
                "FROM g3_admission_decisions WHERE task_id=?", (lease.task_id,),
            ).fetchone()
            receipt = reopened.execute(
                "SELECT execution_id,generation_sha256,root_config_sha256,raw_response,"
                "generation_binding_sha256 FROM chunk_result_receipts WHERE task_id=?",
                (lease.task_id,),
            ).fetchone()
            if scenario != "approved":
                assert row is None and receipt is None
                return
            assert row is not None and receipt is not None
            execution, generation, audit_json, audit_sha = row
            assert execution == lease.execution_id
            assert receipt[:3] == (execution, generation, root_config)
            assert len(generation) == len(receipt[4]) == 64
            assert audit_sha == sha256((generation + audit_json).encode()).hexdigest()
            audit = json.loads(audit_json)
            assert audit["provider_id"] == "offline-test"
            assert audit["model_name"] == FAKE_MODEL
            assert audit["root_config_sha256"] == root_config
            assert audit["source_language"] == "en" and audit["target_language"] == "es"
            assert audit["upper_bound_cost"] == "0"
            assert len(audit["request_sha256"]) == 64
            parsed = parse_chunk_response(plan, unit.chunk_id, receipt[3])
            assert [m.translated_text for m in parsed.members] == [
                m.source_text.strip() for m in unit.members
            ]
            assert reopened.execute(
                "SELECT task_state FROM chunk_tasks WHERE task_id=?", (lease.task_id,),
            ).fetchone() == ("RESULT_STAGED",)


@pytest.mark.integration
def test_pppr_g5_offline_composition_root_real_loopback(tmp_path, monkeypatch):
    """Exercise actual factory, quota store, admission, HTTP and durable receipt.
    Only container isolation and tokenizer are substituted in this CI witness.
    """
    from contextlib import closing
    import threading
    from apps.lab import pppr_offline_scope as lab
    from apps.lab.g3_fake import FakeServer
    from core.ast.hashing import compute_ast_hash
    from core.validation import estimators
    from infra.db import connection
    from runtime import engine

    nodes, original = _fixture()
    plan = ChunkPlan.build(
        sha256(b"pppr-g5-root-witness").hexdigest(),
        compute_ast_hash(nodes), nodes, original.units,
    )
    state = tmp_path / "infra" / "db"
    state.mkdir(parents=True)
    monkeypatch.setattr(connection, "BASE_DIR", tmp_path)
    monkeypatch.delenv("SQLITE_STATE_DIR", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", lab.DUMMY_KEY)
    monkeypatch.setattr(lab, "require_isolated_environment", lambda: None)
    monkeypatch.setattr(estimators, "ExactBPEEstimator", _Estimator)
    db_path = state / "queue.db"
    with closing(sqlite3.connect(db_path)) as db:
        db.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
        repo = ControlPlaneRepository(db)
        repo.enqueue_chunk_plan(plan, nodes)
        snapshots = {
            unit.context_id: ContextSnapshotV1(
                document_id=plan.document_id, ast_hash=plan.ast_hash,
                context_id=unit.context_id,
                breadcrumbs=(ContextBreadcrumbV1(0, "[ROOT_DOCUMENT_CONTEXT]"),),
            )
            for unit in plan.units if unit.chunk_type != TranslationTaskType.PRESERVE
        }
        with FakeServer(("127.0.0.1", 0), db_path, max_requests=4) as server:
            monkeypatch.setattr(lab, "ENDPOINT", f"http://127.0.0.1:{server.server_address[1]}")
            scope = lab.OfflineLabScope(plan.document_id)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                bridge, store = engine._create_chunk_processor(snapshots, offline_scope=scope)
                try:
                    assert bridge.generation_root_config_sha256 == scope.root_config_sha256
                    assert scope.root_config_sha256 != engine._product_effective_config_sha256()
                    for _ in plan.units:
                        lease = repo.pick_task("g5_root", plan.document_id, plan.ast_hash)
                        assert lease is not None
                        unit = next(u for u in plan.units if u.chunk_id == lease.node_id)
                        assert stage_claimed_unit(repo, plan, nodes, unit, lease, "g5_root",
                                                  bridge, Semaphore(1))
                    assert server.requests == 1
                finally:
                    bridge.shutdown()
                    store.close()
            finally:
                server.shutdown()
                thread.join(timeout=5)
    with closing(sqlite3.connect(db_path)) as db:
        rows = db.execute("SELECT root_config_sha256, raw_response FROM chunk_result_receipts").fetchall()
        assert len(rows) == 2
        assert sum(root == scope.root_config_sha256 and raw is not None for root, raw in rows) == 1
        assert (None, None) in rows
        audit = db.execute("SELECT decision_json FROM g3_admission_decisions").fetchall()
        assert len(audit) == 1
        decision = json.loads(audit[0][0])
        assert decision["provider_id"] == lab.PROVIDER_ID
        assert decision["model_name"] == lab.FAKE_MODEL
        assert decision["root_config_sha256"] == scope.root_config_sha256
        assert decision["upper_bound_cost"] == "0"


def test_pppr_g5_free_witness_reservation_is_durable_and_single_use(queue):
    """No new journal: even identical admission replay cannot authorize another effect."""
    from core.execution.exceptions import G3ExternalEffectNotStartedError

    lease = queue.repo.pick_task("free-witness", queue.plan.document_id, queue.plan.ast_hash)
    assert lease is not None
    if next(u for u in queue.plan.units if u.chunk_id == lease.node_id).chunk_type == TranslationTaskType.PRESERVE:
        preserve = next(u for u in queue.plan.units if u.chunk_id == lease.node_id)
        assert stage_claimed_unit(queue.repo, queue.plan, queue.ast, preserve, lease,
                                  "free-witness", None, Semaphore(1))
        lease = queue.repo.pick_task("free-witness", queue.plan.document_id, queue.plan.ast_hash)
    assert lease is not None
    # Synthetic audit tests only the persistence boundary, not the upstream
    # account attestation. The policy producer is covered separately.
    audit = json.dumps({
        "contract": "PPPR_G3_ADMISSION_V1", "request_sha256": "a"*64,
        "upper_bound_cost": "0", "free_tier_witness": {
            "witness_id": "synthetic-reservation", "reserved_requests": 1,
            "valid_until_ns": time.time_ns()+60_000_000_000,
        },
    }, sort_keys=True, separators=(",", ":"))
    kwargs = dict(task_id=lease.task_id, worker_id="free-witness",
                  execution_id=lease.execution_id, generation_sha256="b"*64, audit_json=audit)
    queue.repo.record_g3_admission_decision(**kwargs)
    path = queue.db.execute("PRAGMA database_list").fetchone()[2]
    with sqlite3.connect(path) as reopened:
        repo = ControlPlaneRepository(reopened)
        with pytest.raises(G3ExternalEffectNotStartedError, match="ALREADY_RESERVED"):
            repo.record_g3_admission_decision(**kwargs)
        assert reopened.execute("SELECT COUNT(*) FROM g3_admission_decisions").fetchone() == (1,)


@pytest.mark.integration
@pytest.mark.parametrize("status", [200, 429])
def test_pppr_g5_free_dispatch_bound_to_durable_admission_and_quota(queue, status, tmp_path, monkeypatch):
    """Actual SDK serialization/response, bridge, quota and SQLite; no sockets."""
    import asyncio
    from contextlib import closing
    from decimal import Decimal
    import httpx
    from apps.bootstrap.provider_stack_factory import build_groq_free_witness_stack
    from apps.llm_workers.circuit_breaker_provider import CircuitBreakerProvider
    from infra.resilience.thread_owned_sqlite_rate_limit_store import ThreadOwnedSQLiteRateLimitStore
    from apps.llm_workers.g3_admission import GPT_OSS_120B, GroqFreeTierWitness
    from apps.llm_workers.rate_limiter import QuotaManager
    from core.execution.exceptions import TransientAPIError
    from core.execution.effect_guard import g3_free_dispatch_permit
    from core.finops.measurement import InferenceMeasurementService
    from core.utils.telemetry import ctx_task_id, ctx_execution_id
    from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy

    unit = next(u for u in queue.plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    lease = queue.repo.pick_task("free-dispatch", queue.plan.document_id, queue.plan.ast_hash)
    assert lease is not None
    if lease.node_id != unit.chunk_id:
        preserve = next(u for u in queue.plan.units if u.chunk_id == lease.node_id)
        assert stage_claimed_unit(queue.repo, queue.plan, queue.ast, preserve, lease,
                                  "free-dispatch", None, Semaphore(1))
        lease = queue.repo.pick_task("free-dispatch", queue.plan.document_id, queue.plan.ast_hash)
    assert lease is not None and lease.node_id == unit.chunk_id
    now = time.time_ns()
    policy = _w32_fake_admission(
        model_name=GPT_OSS_120B, input_limit=8000, context_window=131072,
        input_price_per_token=Decimal("0.00000015"), output_price_per_token=Decimal("0.00000060"),
        free_tier_witness=GroqFreeTierWitness(
            "synthetic-dispatch", "synthetic-account", "synthetic-quota", "synthetic-entitlement",
            now-1_000_000, now+60_000_000_000, 30, 1000, 8000, 200000,
            "FREE", True, True, True,
        ),
    )
    builder = PromptBuilder(
        model_name=GPT_OSS_120B, prompt_version="synthetic-free-test",
        measurement_service=InferenceMeasurementService(_Estimator()),
        budget_calculator=PromptBudgetCalculator(),
        compression_policy=StandardCompressionPolicy(),
    )
    db_path = queue.db.execute("PRAGMA database_list").fetchone()[2]
    requests = []

    reservations = []
    original_reserve = QuotaManager.reserve

    async def recording_reserve(self, estimated_tokens, estimated_requests=1):
        permit = g3_free_dispatch_permit.get()
        assert permit is not None
        assert estimated_tokens == permit.reserved_tokens
        reservations.append((estimated_tokens, estimated_requests))
        return await original_reserve(self, estimated_tokens, estimated_requests)

    monkeypatch.setattr(QuotaManager, "reserve", recording_reserve)

    def transport(request):
        requests.append(request)
        assert request.method == "POST"
        assert str(request.url) == "https://api.groq.com/openai/v1/chat/completions"
        body = json.loads(request.content)
        with closing(sqlite3.connect(db_path)) as fresh:
            row = fresh.execute(
                "SELECT decision_json FROM g3_admission_decisions WHERE task_id=? AND execution_id=?",
                (lease.task_id, lease.execution_id),
            ).fetchone()
        assert row is not None  # committed before physical SDK transport
        audit = json.loads(row[0])
        assert audit["request_sha256"] == sha256(json.dumps(
            body, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        ).encode()).hexdigest()
        assert audit["free_tier_witness"]["reserved_tokens"] == audit["input_tokens"] + audit["reserved_output_tokens"]
        if status == 429:
            return httpx.Response(429, json={"error": {"message": "synthetic quota exhausted"}})
        return httpx.Response(200, json={
            "id": "synthetic-attributed-id", "object": "chat.completion", "created": 0,
            "model": GPT_OSS_120B,
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": json.dumps({"content": _response(queue.plan, unit)})}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        })

    quota_path = tmp_path / "witness_rate_limits.db"
    store = ThreadOwnedSQLiteRateLimitStore(str(quota_path))
    bridge = None
    transport_instances = []

    class RecordingTransport(httpx.MockTransport):
        async def aclose(self):
            transport_instances.append("closed")
            await super().aclose()

    def transport_factory():
        transport_instances.append("created")
        return RecordingTransport(transport)

    try:
        provider = asyncio.run(build_groq_free_witness_stack(
            api_key="synthetic-no-network", transport_factory=transport_factory,
            rate_limit_store=store,
        ))
        assert isinstance(provider, CircuitBreakerProvider)
        assert transport_instances == []
        bridge = _bridge(provider, builder, queue.plan, effective_config_sha256="a"*64,
                         pre_effect_admission=policy)
    except BaseException:
        store.close()
        raise
    task_token = ctx_task_id.set(lease.task_id)
    execution_token = ctx_execution_id.set(lease.execution_id)
    try:
        if status == 200:
            assert stage_claimed_unit(queue.repo, queue.plan, queue.ast, unit, lease,
                                      "free-dispatch", bridge, Semaphore(1))
        else:
            with pytest.raises(TransientAPIError, match="429"):
                stage_claimed_unit(queue.repo, queue.plan, queue.ast, unit, lease,
                                   "free-dispatch", bridge, Semaphore(1))
        assert len(requests) == 1
        assert transport_instances == ["created", "closed"]
        assert len(reservations) == 1 and reservations[0][1] == 1
        assert g3_free_dispatch_permit.get() is None
        with closing(sqlite3.connect(quota_path)) as quota:
            balances = dict(quota.execute("SELECT bucket_id, tokens FROM rate_limit_buckets"))
        assert set(balances) == {"rpm", "tpm"}
        assert balances["rpm"] == pytest.approx(29)
        assert balances["tpm"] == pytest.approx(8000 - reservations[0][0])
        assert queue.db.execute(
            "SELECT COUNT(*) FROM chunk_result_receipts WHERE raw_response IS NOT NULL"
        ).fetchone() == (int(status == 200),)
    finally:
        ctx_execution_id.reset(execution_token)
        ctx_task_id.reset(task_token)
        bridge.shutdown()
        store.close()


@pytest.mark.integration
@pytest.mark.parametrize("case", ["ok", "budget", "document", "expired", "replay", "overlap", "drift", "structured_budget"])
def test_pppr_g6_document_free_admission(tmp_path, monkeypatch, case):
    """Real bridge, SDK serialization and durable journal; no live network."""
    from dataclasses import replace
    from decimal import Decimal
    import httpx
    from apps.bootstrap.provider_stack_factory import ProductGroqScope
    from apps.llm_workers.g3_admission import GPT_OSS_120B, GroqFreeTierWitness
    from core.execution.exceptions import G3ExternalEffectNotStartedError
    from core.utils.telemetry import ctx_task_id, ctx_execution_id
    from runtime import engine
    from infra.db import connection

    ast, old_plan = _fixture()
    document_id = "d" * 64
    plan = ChunkPlan.build(document_id, old_plan.ast_hash, ast, old_plan.units)
    unit = next(u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
    db = sqlite3.connect(tmp_path / "queue.db")
    db.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    repo = ControlPlaneRepository(db)
    repo.enqueue_chunk_plan(plan, ast)
    monkeypatch.setattr(connection, "BASE_DIR", tmp_path)
    monkeypatch.setenv("SQLITE_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("GROQ_API_KEY", "synthetic-no-network")
    monkeypatch.delenv("TPDF_OFFLINE_LAB", raising=False)
    now = time.time_ns()
    witness = GroqFreeTierWitness(
        "g6-synthetic", "synthetic-account", "synthetic-quota", "synthetic-free",
        now - 1_000_000, now + 60_000_000_000, 30, 1000, 8000, 200000,
        "FREE", True, True, True, document_id=document_id, max_requests=2,
    )
    if case == "expired":
        witness = replace(witness, observed_at_ns=now-2_000_000, valid_until_ns=now-1_000_000)
    if case == "document":
        witness = replace(witness, document_id="e"*64)
    policy = _w32_fake_admission(
        model_name=GPT_OSS_120B, root_config_sha256=engine._product_effective_config_sha256(),
        input_limit=8000, output_limit=4096, context_window=131072,
        input_price_per_token=Decimal("0.00000015"), output_price_per_token=Decimal("0.00000060"),
        free_tier_witness=witness,
    )
    requests = []

    def transport(request):
        requests.append(request)
        body = json.loads(request.content)
        with sqlite3.connect(tmp_path / "queue.db") as probe:
            rows = probe.execute("SELECT decision_json FROM g3_admission_decisions").fetchall()
        assert len(rows) == 1
        assert json.loads(rows[0][0])["request_sha256"] == sha256(json.dumps(
            body, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        ).encode()).hexdigest()
        return httpx.Response(200, json={
            "id": "synthetic-g6", "object": "chat.completion", "created": 0,
            "model": GPT_OSS_120B,
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": json.dumps({"content": _response(plan, unit)})}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        })

    prompt_estimator = _CharBoundEstimator() if case == "structured_budget" else _Estimator()
    scope = ProductGroqScope(policy, prompt_estimator, lambda: httpx.MockTransport(transport))
    snapshots = {unit.context_id: ContextSnapshotV1(
        document_id=plan.document_id, ast_hash=plan.ast_hash, context_id=unit.context_id,
        breadcrumbs=(ContextBreadcrumbV1(0, "[ROOT_DOCUMENT_CONTEXT]"),),
    )}
    bridge = store = None
    try:
        if case in ("expired", "document"):
            with pytest.raises(G3ExternalEffectNotStartedError):
                engine._create_chunk_processor(snapshots, product_scope=scope)
            assert requests == []
            return
        bridge, store = engine._create_chunk_processor(snapshots, product_scope=scope)
        preview = bridge.inspect_chunk_admission(plan, unit)
        audit = json.loads(preview.audit_json)
        assert requests == []
        assert db.execute("SELECT COUNT(*) FROM g3_admission_decisions").fetchone() == (0,)
        if case == "structured_budget":
            # Independent response-shape oracle, not the production sampler.
            # This fixture has no masked inline formula.
            example = json.loads(_response(plan, unit))
            for member, source in zip(example["members"], unit.members):
                member["translated_text"] = source.source_text
            def serialize(value):
                return json.dumps({"content": json.dumps(value, ensure_ascii=False,
                    sort_keys=True, separators=(",", ":"))}, ensure_ascii=False,
                    sort_keys=True, separators=(",", ":"))
            populated = serialize(example)
            for member in example["members"]:
                member["translated_text"] = ""
            empty = serialize(example)
            expected = max(256, len(empty) + 2 * (len(populated) - len(empty)))
            assert audit["reserved_output_tokens"] == expected
            assert audit["free_tier_witness"]["reserved_tokens"] == audit["input_tokens"] + expected
            assert audit["input_tokens"] > expected
        if case == "budget":
            with pytest.raises(G3ExternalEffectNotStartedError, match="EXHAUSTED"):
                repo.check_g3_document_free_batch(document_id, [preview.audit_json]*3)
            assert repo.fit_g3_document_free_batch(document_id, [preview.audit_json]*3) == 2
            assert db.execute("SELECT COUNT(*) FROM g3_admission_decisions").fetchone() == (0,)
            assert requests == []
            return
        repo.check_g3_document_free_batch(document_id, [preview.audit_json])
        lease = repo.pick_task("g6", plan.document_id, plan.ast_hash)
        assert lease is not None
        if lease.node_id != unit.chunk_id:
            preserve = next(u for u in plan.units if u.chunk_id == lease.node_id)
            assert stage_claimed_unit(repo, plan, ast, preserve, lease, "g6", None, Semaphore(1))
            lease = repo.pick_task("g6", plan.document_id, plan.ast_hash)
        assert lease is not None and lease.node_id == unit.chunk_id
        if case in ("replay", "overlap", "drift"):
            kwargs = dict(task_id=lease.task_id, worker_id="g6", execution_id=lease.execution_id,
                          generation_sha256="b"*64, audit_json=preview.audit_json)
            repo.record_g3_admission_decision(**kwargs)
            if case == "replay":
                with pytest.raises(G3ExternalEffectNotStartedError, match="ALREADY_RESERVED"):
                    repo.record_g3_admission_decision(**kwargs)
            else:
                key = "witness_id" if case == "overlap" else "quota_evidence_ref"
                audit["free_tier_witness"][key] = "different"
                with pytest.raises(G3ExternalEffectNotStartedError,
                                   match="OVERLAP" if case == "overlap" else "DRIFT"):
                    repo.check_g3_document_free_batch(document_id, [
                        json.dumps(audit, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                    ])
            assert requests == []
        else:
            # The real engine sets these correlation IDs at claim time.
            # Reproduce that boundary, not a permissive mock of the adapter.
            task_token = ctx_task_id.set(lease.task_id)
            execution_token = ctx_execution_id.set(lease.execution_id)
            try:
                assert stage_claimed_unit(repo, plan, ast, unit, lease, "g6", bridge, Semaphore(1))
            finally:
                ctx_execution_id.reset(execution_token)
                ctx_task_id.reset(task_token)
            assert len(requests) == 1
            assert db.execute("SELECT COUNT(*) FROM chunk_result_receipts WHERE raw_response IS NOT NULL").fetchone() == (1,)
    finally:
        if bridge is not None:
            bridge.shutdown()
        if store is not None:
            store.close()
        db.close()


@pytest.mark.integration
def test_pppr_free_window_scoped_claim_never_consumes_deferred_work(queue):
    preserve, translate = queue.plan.units
    assert queue.repo.pick_task(
        "window", queue.plan.document_id, queue.plan.ast_hash, allowed_chunk_ids=(),
    ) is None
    lease = queue.repo.pick_task(
        "window", queue.plan.document_id, queue.plan.ast_hash,
        allowed_chunk_ids=(translate.chunk_id,),
    )
    assert lease is not None and lease.node_id == translate.chunk_id
    assert queue.repo.pick_task(
        "window", queue.plan.document_id, queue.plan.ast_hash,
        allowed_chunk_ids=(translate.chunk_id,),
    ) is None
    assert queue.db.execute(
        "SELECT task_state FROM chunk_tasks WHERE node_id=?", (preserve.chunk_id,),
    ).fetchone() == ("PENDING",)
    assert queue.repo.pick_task("next", queue.plan.document_id, queue.plan.ast_hash).node_id == preserve.chunk_id


@pytest.mark.integration
def test_pppr_free_document_resumes_across_explicit_quota_windows(tmp_path, monkeypatch):
    """Canonical engine, real durable journal and SDK, no real provider I/O."""
    from decimal import Decimal
    import httpx
    from apps.bootstrap.provider_stack_factory import ProductGroqScope
    from apps.llm_workers.g3_admission import GPT_OSS_120B, GroqFreeTierWitness
    from core.chunking.contextual_plan import prepare_contextual_plan
    from infra.db import connection
    from runtime import engine
    from tests.integration.test_g3_b4_8_preserve_engine import _dbs

    document_id = "d" * 64
    prepared = prepare_contextual_plan(
        document_id=document_id,
        raw_ast=[
            ASTNode(node_id="a", sequence_id=1, node_type=ContentNodeType.PARAGRAPH,
                    payload=ParagraphPayload(content="First paragraph.")),
            ASTNode(node_id="math", sequence_id=2, node_type=ContentNodeType.DISPLAY_EQUATION,
                    strategy=TranslationStrategy.PASSTHROUGH, payload=MathPayload(content="E=mc^2")),
            ASTNode(node_id="b", sequence_id=3, node_type=ContentNodeType.PARAGRAPH,
                    payload=ParagraphPayload(content="Second paragraph.")),
        ],
        estimator=_Estimator(),
    )
    ast, plan = list(prepared.ast), prepared.plan
    units = [u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE]
    assert len(units) == 2 and len(plan.units) == 3
    dbs = _dbs(tmp_path, plan, ast)
    monkeypatch.setattr(connection, "BASE_DIR", tmp_path)
    monkeypatch.setenv("SQLITE_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("GROQ_API_KEY", "synthetic-no-network")
    monkeypatch.setenv("IS_BENCHMARK", "0")
    monkeypatch.delenv("TPDF_OFFLINE_LAB", raising=False)
    monkeypatch.setattr(engine, "ASTRegistry", lambda: SimpleNamespace(
        get_verified_document_ast=lambda doc, ast_hash: ast,
    ))
    monkeypatch.setattr(engine, "get_connection", lambda path, timeout=30:
                        sqlite3.connect(tmp_path / Path(path).name, timeout=timeout))

    clock = [time.time_ns()]
    monkeypatch.setattr(time, "time_ns", lambda: clock[0])
    calls = []

    def transport(request):
        unit = units[len(calls)]
        calls.append(unit.chunk_id)
        with sqlite3.connect(tmp_path / "queue.db") as probe:
            assert probe.execute("SELECT COUNT(*) FROM g3_admission_decisions").fetchone() == (len(calls),)
        return httpx.Response(200, json={
            "id": f"synthetic-window-{len(calls)}", "object": "chat.completion", "created": 0,
            "model": GPT_OSS_120B,
            "choices": [{"index": 0, "finish_reason": "stop", "message": {
                "role": "assistant", "content": json.dumps({"content": _response(plan, unit)}),
            }}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        })

    def scope(window):
        witness = GroqFreeTierWitness(
            f"synthetic-window-{window}", "synthetic-account", "synthetic-quota", "synthetic-free",
            clock[0] - 1_000_000, clock[0] + 60_000_000_000, 30, 1000, 8000, 200000,
            "FREE", True, True, True, document_id=document_id, max_requests=1,
        )
        policy = _w32_fake_admission(
            model_name=GPT_OSS_120B, root_config_sha256=engine._product_effective_config_sha256(),
            input_limit=8000, output_limit=4096, context_window=131072,
            input_price_per_token=Decimal("0.00000015"), output_price_per_token=Decimal("0.00000060"),
            free_tier_witness=witness,
        )
        return ProductGroqScope(policy, _Estimator(), lambda: httpx.MockTransport(transport))

    try:
        first = scope(1)
        result = engine.run_pipeline(document_id, plan.ast_hash, product_scope=first)
        assert result == {"status": "staging_incomplete", "final_state": "PROCESSING"}
        assert calls == [units[0].chunk_id]
        assert dbs.queue.execute(
            "SELECT task_state,retry_count FROM chunk_tasks WHERE node_id=?", (units[1].chunk_id,),
        ).fetchone() == ("PENDING", 0)
        assert dbs.queue.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone() == (2,)
        # The same consumed authorization grants no further claims or effects.
        assert engine.run_pipeline(document_id, plan.ast_hash, product_scope=first) == result
        assert calls == [units[0].chunk_id]
        assert dbs.queue.execute("SELECT COUNT(*) FROM g3_admission_decisions").fetchone() == (1,)
        # Only a distinct, nonoverlapping explicit witness can resume.
        clock[0] += 61_000_000_000
        result = engine.run_pipeline(document_id, plan.ast_hash, product_scope=scope(2))
        assert result == {"status": "ready_for_assembly", "final_state": "READY_FOR_ASSEMBLY"}
        assert calls == [u.chunk_id for u in units]
        assert dbs.queue.execute("SELECT COUNT(*) FROM g3_admission_decisions").fetchone() == (2,)
        assert dbs.queue.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone() == (3,)
        assert {row[0] for row in dbs.queue.execute(
            "SELECT task_state FROM chunk_tasks WHERE worker_type='LLM'",
        )} == {"COMPLETED"}
    finally:
        dbs.materialized.close()
        dbs.fsm.close()
        dbs.queue.close()


@pytest.mark.integration
@pytest.mark.parametrize("indivisible", [False, True])
def test_pppr_effective_budget_refines_new_manifest_without_provider(indivisible):
    from decimal import Decimal
    from apps.bootstrap.provider_stack_factory import (
        ProductGroqScope, refine_product_chunk_plan, build_product_prompt_builder,
    )
    from apps.llm_workers.g3_admission import GPT_OSS_120B
    from apps.llm_workers.sync_bridge import prepare_chunk_prompt
    from core.chunking.contextual_plan import prepare_contextual_plan
    from core.context.plan_context_contract import derive_verified_plan_contexts

    ast = [
        ASTNode(node_id=f"paragraph-{i}", sequence_id=i, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content=("word " * 110).strip()))
        for i in range(1, 5)
    ]
    ast.append(ASTNode(node_id="math", sequence_id=5, node_type=ContentNodeType.DISPLAY_EQUATION,
                       strategy=TranslationStrategy.PASSTHROUGH, payload=MathPayload(content="E=mc^2")))
    prepared = prepare_contextual_plan(document_id="d"*64, raw_ast=ast, estimator=_Estimator())
    plan = prepared.plan
    assert len(plan.units) == 2
    policy = _w32_fake_admission(
        model_name=GPT_OSS_120B,
        input_limit=100 if indivisible else 8000, output_limit=4096, context_window=131072,
        input_price_per_token=Decimal("0.00000015"), output_price_per_token=Decimal("0.00000060"),
    )
    # Character estimator is a deliberately synthetic sizing witness.
    # It makes the four-member request too large; each half fits.
    scope = ProductGroqScope(policy, _CharBoundEstimator(),
                             lambda: pytest.fail("planning instantiated a transport"))
    original = plan.to_json()
    if indivisible:
        with pytest.raises(ValueError, match="G3_EFFECTIVE_BUDGET_INDIVISIBLE_UNIT"):
            refine_product_chunk_plan(plan, prepared.ast, scope)
        assert plan.to_json() == original
        return
    refined = refine_product_chunk_plan(plan, prepared.ast, scope)
    assert len(refined.units) > len(plan.units)
    assert refined.ast_hash == plan.ast_hash and refined.digest != plan.digest
    assert [m for u in refined.units for m in u.members] == [m for u in plan.units for m in u.members]
    assert refined.units[-1].members == plan.units[-1].members
    assert refined.units[-1].chunk_type == TranslationTaskType.PRESERVE
    assert plan.to_json() == original
    assert refine_product_chunk_plan(refined, prepared.ast, scope) == refined
    assert [u.chunk_index for u in refined.units] == list(range(1, len(refined.units)+1))
    snapshots = derive_verified_plan_contexts(refined, prepared.ast)
    for unit in refined.units:
        if unit.chunk_type == TranslationTaskType.PRESERVE:
            continue
        built, _, _ = prepare_chunk_prompt(
            refined, unit, builder=build_product_prompt_builder(scope.prompt_estimator),
            context_snapshots=snapshots, structured_response=True,
        )
        _, count, reserve = policy.measure_request(built.envelope)
        assert count + reserve <= 8000


@pytest.mark.integration
def test_pppr_budget_preview_uses_real_request_without_admission(monkeypatch):
    from dataclasses import asdict
    from apps.lab.pppr_g6_budget_preview import preview_product_budget
    from core.chunking.contextual_plan import prepare_contextual_plan

    nodes = [
        ASTNode(node_id=f"preview-{i}", sequence_id=i, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content=("scientific text " * 45).strip()))
        for i in range(1, 5)
    ]
    nodes.append(ASTNode(node_id="math", sequence_id=5, node_type=ContentNodeType.DISPLAY_EQUATION,
                         strategy=TranslationStrategy.PASSTHROUGH, payload=MathPayload(content="E=mc^2")))
    estimator = _Estimator()
    prepared = prepare_contextual_plan(document_id="d"*64, raw_ast=nodes, estimator=estimator)
    plan = prepared.plan
    original = plan.to_json()
    monkeypatch.setattr(G3PreEffectAdmission, "verify",
                        lambda *a, **kw: pytest.fail("preview attempted admission"))
    baseline = preview_product_budget(plan, prepared.ast, estimator)
    assert baseline.status == "OFFLINE_CONDITIONAL_SIZING_ONLY"
    assert baseline.max_common_framing_tokens is not None
    assert baseline.max_common_framing_tokens > 0
    assert baseline.preserve_units == 1
    assert baseline.max_common_framing_tokens == min(
        8000 - row.message_bytes - row.reserved_output_tokens for row in baseline.requests
    )
    assert baseline.candidate_units == len(baseline.requests) + baseline.preserve_units
    # One token above the measured headroom forces further refinement.
    scenario = baseline.max_common_framing_tokens + 1
    refined = preview_product_budget(plan, prepared.ast, estimator, framing_scenario=scenario)
    assert refined.candidate_units > baseline.candidate_units
    assert refined.max_common_framing_tokens >= scenario
    assert refined.preserve_units == baseline.preserve_units
    assert plan.to_json() == original
    assert preview_product_budget(plan, prepared.ast, estimator, framing_scenario=scenario) == refined
    assert "scientific text" not in json.dumps(asdict(refined))
    assert "E=mc^2" not in json.dumps(asdict(refined))
    with pytest.raises(ValueError, match="G3_EFFECTIVE_BUDGET_INDIVISIBLE_UNIT"):
        preview_product_budget(plan, prepared.ast, estimator, framing_scenario=7999)
    assert plan.to_json() == original


@pytest.mark.integration
def test_pppr_budget_preview_preserve_only_has_no_framing_requirement():
    from apps.lab.pppr_g6_budget_preview import preview_product_budget
    from core.chunking.contextual_plan import prepare_contextual_plan

    ast = [ASTNode(node_id="math", sequence_id=1, node_type=ContentNodeType.DISPLAY_EQUATION,
                   strategy=TranslationStrategy.PASSTHROUGH, payload=MathPayload(content="E=mc^2"))]
    estimator = _Estimator()
    prepared = prepare_contextual_plan(document_id="d"*64, raw_ast=ast, estimator=estimator)
    observed = preview_product_budget(prepared.plan, prepared.ast, estimator)
    assert observed.requests == ()
    assert observed.max_common_framing_tokens is None
    assert observed.preserve_units == 1
    assert observed.original_manifest_sha256 == observed.candidate_manifest_sha256
    for invalid in (-1, True, 8000):
        with pytest.raises(ValueError, match="PREVIEW_SCENARIO_INVALID"):
            preview_product_budget(prepared.plan, prepared.ast, estimator, framing_scenario=invalid)
