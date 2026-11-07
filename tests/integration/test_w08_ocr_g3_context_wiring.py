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
            envelope=SimpleNamespace(chunk_id=unit.chunk_id),
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
        inference = [u for u in prepared.plan.units if u.chunk_type != TranslationTaskType.PRESERVE]
        assert len(inference) == 2
        assert inference[0].context_id != inference[1].context_id
        assert all(u.context_id.startswith("CTX_") and u.context_depth == 1 for u in inference)
        assert all(u.context_id != "GLOBAL_ROOT" for u in prepared.plan.units)


def test_w08_new_connection_delivers_effective_section_context_to_fake(tmp_path):
    prepared, conn = _setup(tmp_path)
    conn.close()
    with closing(sqlite3.connect(tmp_path / "queue.db")) as reopened:
        plan, snapshots = DurableContextPlanRepository(
            ControlPlaneRepository(reopened),
        ).load_verified(prepared.plan.document_id, prepared.plan.ast_hash, prepared.ast)
    units = [u for u in plan.units if u.chunk_type == TranslationTaskType.TRANSLATE]
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


def test_w08_ocr_contextual_ast_hash_matches_raw_semantic_identity():
    from core.ast.hashing import compute_ast_hash
    raw = _raw_ast()
    prepared = prepare_contextual_plan(
        document_id="doc", raw_ast=raw, estimator=cast(TokenEstimatorProtocol, _Estimator()),
    )
    assert prepared.plan.ast_hash == compute_ast_hash(raw)
    assert prepared.plan.ast_hash == compute_ast_hash(prepared.ast)
