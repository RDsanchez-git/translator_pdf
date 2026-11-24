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
