"""W08-2c: end-to-end, synthetic context witnesses for OCR and G3.

Real disposable SQLite and AST; fake builder/provider; no Docker, PDF corpus,
paid inference, external networking or production state.
"""
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace
from typing import cast

import pytest

from apps.llm_workers.sync_bridge import SyncProviderBridge
from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.routing import LLMProvider
from core.ast.enums import ContentNodeType, HeadingLevel
from core.ast.models import ASTNode, HeadingPayload, ParagraphPayload, TranslationTaskType
from core.chunking.contextual_plan import prepare_contextual_plan
from core.chunking.result_contract import materialize_node_results
from core.context.snapshot_contract import ContextSnapshotV1
from core.validation.protocols import TokenEstimatorProtocol
from infra.db.context_snapshot_repo import DurableContextPlanRepository
from infra.db.control_repo import ControlPlaneRepository


ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 5)


class _CaptureBuilder:
    prompt_version = "test"
    model_name = "fake"

    def __init__(self) -> None:
        self.seen = []

    def build(self, unit, resolved_context, target_lang_expansion=1.2):
        self.seen.append(resolved_context)
        return SimpleNamespace(
            status="success",
            envelope=SimpleNamespace(chunk_id=unit.chunk_id, target_provider="primary"),
        )


class _FakeProvider:
    def __init__(self, response: str) -> None:
        self.calls = 0
        self.response = response

    async def translate(self, envelope):
        self.calls += 1
        return SimpleNamespace(chunk_id=envelope.chunk_id, content=self.response)


def _raw_ast():
    return [
        ASTNode(node_id="h1", sequence_id=1, node_type=ContentNodeType.HEADING,
                payload=HeadingPayload(content="Methods", heading_level=HeadingLevel.H1)),
        ASTNode(node_id="p1", sequence_id=2, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Alpha.")),
        ASTNode(node_id="h2", sequence_id=3, node_type=ContentNodeType.HEADING,
                payload=HeadingPayload(content="Results", heading_level=HeadingLevel.H1)),
        ASTNode(node_id="p2", sequence_id=4, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Beta.")),
    ]


def _setup(tmp_path):
    prepared = prepare_contextual_plan(
        document_id="doc_w08_2c", raw_ast=_raw_ast(),
        estimator=cast(TokenEstimatorProtocol, _Estimator()),
    )
    conn = sqlite3.connect(tmp_path / "queue.db")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    repo = DurableContextPlanRepository(ControlPlaneRepository(conn))
    repo.enqueue_verified(prepared.plan, prepared.ast)
    return prepared, conn


def _response(plan, unit):
    return json.dumps({
        "schema_version": 1, "document_id": plan.document_id,
        "ast_hash": plan.ast_hash, "manifest_sha256": plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [{
            "node_id": member.node_id,
            "segment_index": member.segment_index,
            "source_sha256": sha256(member.source_text.encode()).hexdigest(),
            "translated_text": "Traduccion.",
        } for member in unit.members],
    })


def test_w08_ocr_produces_distinct_contexts_without_global_root(tmp_path):
    prepared, conn = _setup(tmp_path)
    with closing(conn):
        assert len(prepared.plan.units) == 4
        inference = [
            u for u in prepared.plan.units
            if u.chunk_type == TranslationTaskType.TRANSLATE
        ]
        assert len(inference) == 4
        headings = [
            u for u in inference
            if u.members[0].node_type == ContentNodeType.HEADING.value
        ]
        paragraphs = [
            u for u in inference
            if u.members[0].node_type == ContentNodeType.PARAGRAPH.value
        ]
        assert len(headings) == len(paragraphs) == 2
        assert headings[0].context_id == headings[1].context_id
        assert paragraphs[0].context_id != paragraphs[1].context_id
        assert all(u.context_id.startswith("CTX_") and u.context_depth == 1 for u in inference)
        assert all(u.context_id != "GLOBAL_ROOT" for u in prepared.plan.units)


def test_w08_new_connection_delivers_effective_section_context_to_fake(tmp_path):
    prepared, conn = _setup(tmp_path)
    conn.close()
    with closing(sqlite3.connect(tmp_path / "queue.db")) as reopened:
        plan, snapshots = DurableContextPlanRepository(
            ControlPlaneRepository(reopened),
        ).load_verified(prepared.plan.document_id, prepared.plan.ast_hash, prepared.ast)
    units = [
        u for u in plan.units
        if u.chunk_type == TranslationTaskType.TRANSLATE
        and u.members[0].node_type == ContentNodeType.PARAGRAPH.value
    ]
    for expected_title, unit in zip(("Methods", "Results"), units, strict=True):
        builder = _CaptureBuilder()
        provider = _FakeProvider(_response(plan, unit))
        bridge = SyncProviderBridge(
            cast(LLMProvider, provider), cast(PromptBuilder, builder),
            context_snapshots=snapshots,
        )
        try:
            assert bridge.execute_chunk(plan, unit) == provider.response
        finally:
            bridge.shutdown()
        assert provider.calls == 1
        assert builder.seen[0].breadcrumbs == (f"H1: {expected_title}",)


def test_w08_missing_context_fails_before_fake_provider(tmp_path):
    prepared, conn = _setup(tmp_path)
    with closing(conn):
        unit = next(u for u in prepared.plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
        provider = _FakeProvider(_response(prepared.plan, unit))
        builder = _CaptureBuilder()
        bridge = SyncProviderBridge(
            cast(LLMProvider, provider), cast(PromptBuilder, builder),
            context_snapshots={},
        )
        try:
            with pytest.raises(ValueError, match="W08_G3_UNVERIFIED_CONTEXT_BEFORE_PROVIDER"):
                bridge.execute_chunk(prepared.plan, unit)
        finally:
            bridge.shutdown()
        assert provider.calls == 0
        assert builder.seen == []


def test_w08_context_from_other_generation_fails_before_fake(tmp_path):
    prepared, conn = _setup(tmp_path)
    with closing(conn):
        unit = next(u for u in prepared.plan.units if u.chunk_type == TranslationTaskType.TRANSLATE)
        snapshots = DurableContextPlanRepository(ControlPlaneRepository(conn)).load_verified(
            prepared.plan.document_id, prepared.plan.ast_hash, prepared.ast,
        )[1]
        chosen = snapshots[unit.context_id]
        forged = ContextSnapshotV1(
            document_id=chosen.document_id,
            ast_hash="other-generation",
            context_id=chosen.context_id,
            breadcrumbs=chosen.breadcrumbs,
        )
        provider = _FakeProvider(_response(prepared.plan, unit))
        bridge = SyncProviderBridge(
            cast(LLMProvider, provider), cast(PromptBuilder, _CaptureBuilder()),
            context_snapshots={unit.context_id: forged},
        )
        try:
            with pytest.raises(ValueError, match="W08_G3_UNVERIFIED_CONTEXT_BEFORE_PROVIDER"):
                bridge.execute_chunk(prepared.plan, unit)
        finally:
            bridge.shutdown()
        assert provider.calls == 0


def test_w08_ast_cache_and_sqlite_rehydrate_across_fresh_instances(tmp_path):
    from core.ast.hashing import compute_ast_hash
    from core.ast.registry import ASTRegistry

    prepared, conn = _setup(tmp_path)
    with closing(conn):
        registry = ASTRegistry(workspace_dir=str(tmp_path))
        registry.register_ast(
            prepared.plan.document_id, prepared.plan.ast_hash,
            list(prepared.ast),
        )

    # New ASTRegistry and SQLite connection: no shared in-process cache.
    fresh = ASTRegistry(workspace_dir=str(tmp_path)).get_document_ast(
        prepared.plan.document_id, prepared.plan.ast_hash,
    )
    assert len(fresh) == len(prepared.ast)
    assert compute_ast_hash(fresh) == prepared.plan.ast_hash
    assert [node.control_plane for node in fresh] == [
        node.control_plane for node in prepared.ast
    ]
    with closing(sqlite3.connect(tmp_path / "queue.db")) as reopened:
        plan, snapshots = DurableContextPlanRepository(
            ControlPlaneRepository(reopened),
        ).load_verified(
            prepared.plan.document_id, prepared.plan.ast_hash, fresh,
        )
    assert plan == prepared.plan
    assert {u.context_id for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE} == set(snapshots)


def test_w08_ocr_contextual_ast_hash_matches_raw_semantic_identity():
    from core.ast.hashing import compute_ast_hash
    raw = _raw_ast()
    prepared = prepare_contextual_plan(
        document_id="doc", raw_ast=raw, estimator=cast(TokenEstimatorProtocol, _Estimator()),
    )
    assert prepared.plan.ast_hash == compute_ast_hash(raw)
    assert prepared.plan.ast_hash == compute_ast_hash(prepared.ast)


@pytest.mark.integration
def test_w42_selected_heading_materializes_fake_es_from_reopened_sqlite(tmp_path):
    """Heading G3 fake -> durable snapshots -> translated materialization."""
    prepared, conn = _setup(tmp_path)
    conn.close()
    with closing(sqlite3.connect(tmp_path / "queue.db")) as reopened:
        plan, snapshots = DurableContextPlanRepository(
            ControlPlaneRepository(reopened),
        ).load_verified(prepared.plan.document_id, prepared.plan.ast_hash, prepared.ast)
        assert plan == prepared.plan
        assert len(snapshots) == 3

    selected = {"h1": "Métodos", "p1": "Alfa.", "h2": "Resultados", "p2": "Beta."}
    responses = {}
    for unit in plan.units:
        assert unit.chunk_type == TranslationTaskType.TRANSLATE
        member = unit.members[0]
        raw = json.dumps({
            "schema_version": 1, "document_id": plan.document_id,
            "ast_hash": plan.ast_hash, "manifest_sha256": plan.digest,
            "chunk_id": unit.chunk_id,
            "members": [{
                "node_id": member.node_id,
                "segment_index": member.segment_index,
                "source_sha256": sha256(member.source_text.encode()).hexdigest(),
                "translated_text": selected[member.node_id],
            }],
        })
        provider = _FakeProvider(raw)
        builder = _CaptureBuilder()
        bridge = SyncProviderBridge(
            cast(LLMProvider, provider), cast(PromptBuilder, builder),
            context_snapshots=snapshots,
        )
        try:
            responses[unit.chunk_id] = bridge.execute_chunk(plan, unit)
        finally:
            bridge.shutdown()
        assert provider.calls == 1
        if member.node_type == ContentNodeType.HEADING.value:
            # The verified root snapshot is level 0, but its prompt-facing
            # title is intentionally unprefixed by SyncProviderBridge.
            root_snapshot = snapshots[unit.context_id]
            assert len(root_snapshot.breadcrumbs) == 1
            assert root_snapshot.breadcrumbs[0].level == 0
            assert root_snapshot.breadcrumbs[0].title == "[ROOT_DOCUMENT_CONTEXT]"
            assert builder.seen[0].context_id == unit.context_id
            assert builder.seen[0].breadcrumbs == (
                "[ROOT_DOCUMENT_CONTEXT]",
            )
    actual = materialize_node_results(plan, responses)
    assert {x.node_id: x.text for x in actual} == selected
    assert {x.node_id: x.text_sha256 for x in actual} == {
        k: sha256(v.encode()).hexdigest() for k, v in selected.items()
    }


@pytest.mark.integration
def test_w42_old_preserved_heading_manifest_cannot_replay_as_translate(tmp_path):
    from dataclasses import replace
    from core.chunking.manifest_contract import ChunkPlan

    prepared, conn = _setup(tmp_path)
    with closing(conn):
        heading = next(
            u for u in prepared.plan.units
            if u.members[0].node_type == ContentNodeType.HEADING.value
        )
        forged = replace(heading, chunk_type=TranslationTaskType.PRESERVE)
        units = [
            forged if u.chunk_id == heading.chunk_id else u
            for u in prepared.plan.units
        ]
        with pytest.raises(ValueError, match="G3_TASK_POLICY_MISMATCH"):
            ChunkPlan.build(
                prepared.plan.document_id, prepared.plan.ast_hash,
                prepared.ast, units,
            )


@pytest.mark.integration
def test_w42_unknown_heading_remains_preserve_and_does_not_invent_h1():
    from core.ast.hashing import compute_ast_hash

    source = _raw_ast()
    source[0] = source[0].model_copy(update={
        "payload": HeadingPayload(
            content="Unknown Methods", heading_level=HeadingLevel.UNKNOWN,
        ),
    })
    prepared = prepare_contextual_plan(
        document_id="doc_unknown", raw_ast=source,
        estimator=cast(TokenEstimatorProtocol, _Estimator()),
    )
    assert prepared.plan.ast_hash == compute_ast_hash(source)
    unit = next(u for u in prepared.plan.units if u.members[0].node_id == "h1")
    assert unit.chunk_type == TranslationTaskType.PRESERVE
    assert unit.context_id == "PRESERVE_HEADING_NO_INFERENCE"
    assert unit.target_payload == "Unknown Methods"
