"""G3-B4/7b regression: durable quota SQLite stays in its owning thread.

Uses a real sqlite3 database, real QuotaManager and actual SyncProviderBridge
loop, without network, a paid provider, OCR, Docker, or a historic database.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import sqlite3
from types import SimpleNamespace

import pytest

from apps.llm_workers.rate_limiter import QuotaManager
from apps.llm_workers.sync_bridge import SyncProviderBridge
from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, ParagraphPayload
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from infra.resilience.thread_owned_sqlite_rate_limit_store import ThreadOwnedSQLiteRateLimitStore
from infra.resilience.sqlite_rate_limit_store import SQLiteRateLimitStore


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)


class _Builder:
    prompt_version = "v1.0"
    model_name = "fake-local-only"

    def build(self, unit, *, resolved_context, target_lang_expansion):
        return SimpleNamespace(status="success", envelope=object(), message="")


def _one_member_plan():
    ast = [ASTNode(
        node_id="quota_n1", sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        payload=ParagraphPayload(content="Hello world."),
    )]
    units, _ = build_semantic_chunks_as_units(ast, _Estimator())
    plan = ChunkPlan.build("quota_doc", "quota_ast_hash", ast, units)
    assert len(plan.units) == 1 and len(plan.units[0].members) == 1
    return plan, plan.units[0]


class _QuotaFakeProvider:
    def __init__(self, manager, plan, unit):
        self.manager = manager
        self.plan = plan
        self.unit = unit

    async def translate(self, envelope):
        await self.manager.reserve(estimated_tokens=2)
        p, u = self.plan, self.unit
        response = {
            "schema_version": 1,
            "document_id": p.document_id,
            "ast_hash": p.ast_hash,
            "manifest_sha256": p.digest,
            "chunk_id": u.chunk_id,
            "members": [{
                "node_id": m.node_id,
                "segment_index": m.segment_index,
                "source_sha256": sha256(m.source_text.encode("utf-8")).hexdigest(),
                "translated_text": "Texto traducido.",
            } for m in u.members],
        }
        return SimpleNamespace(chunk_id=u.chunk_id, content=json.dumps(response))


def test_bridge_worker_threads_persist_quota_on_single_owner(tmp_path):
    db = tmp_path / "rate_limits.db"
    store = ThreadOwnedSQLiteRateLimitStore(str(db))
    bridge = None
    try:
        manager = QuotaManager(rpm_limit=30, tpm_limit=6000, store=store)
        plan, unit = _one_member_plan()
        bridge = SyncProviderBridge(_QuotaFakeProvider(manager, plan, unit), _Builder())
        # Actual Engine shape: multiple sync worker threads submit to one bridge loop.
        with ThreadPoolExecutor(max_workers=2) as workers:
            results = list(workers.map(lambda _: bridge.execute_chunk(plan, unit), range(2)))
        assert len(results) == 2
        assert all(json.loads(item)["chunk_id"] == unit.chunk_id for item in results)
        assert store.load("rpm") is not None
        assert store.load("tpm") is not None
    finally:
        if bridge is not None:
            bridge.shutdown()
        store.close()

    # Durability across connection/thread lifetimes, without touching production DB.
    check = sqlite3.connect(db)
    try:
        saved = dict(check.execute("SELECT bucket_id, tokens FROM rate_limit_buckets"))
    finally:
        check.close()
    assert set(saved) == {"rpm", "tpm"}
    assert saved["rpm"] < 30
    assert saved["tpm"] < 6000

    reopened = ThreadOwnedSQLiteRateLimitStore(str(db))
    try:
        assert reopened.load("rpm") is not None
        assert reopened.load("tpm") is not None
        restored = QuotaManager(rpm_limit=30, tpm_limit=6000, store=reopened)
        assert 0 <= restored.rpm_bucket.tokens <= 30
        assert 0 <= restored.tpm_bucket.tokens <= 6000
    finally:
        reopened.close()


def test_old_direct_connection_reproduces_thread_affinity_error(tmp_path):
    # Documents the original failure signature using the unchanged adapter.
    connection = sqlite3.connect(tmp_path / "old_rate_limits.db")
    try:
        original = SQLiteRateLimitStore(connection)
        with ThreadPoolExecutor(max_workers=1) as workers:
            future = workers.submit(original.load, "rpm")
            with pytest.raises(sqlite3.ProgrammingError, match="same thread"):
                future.result()
    finally:
        connection.close()


def test_store_close_is_idempotent_and_rejects_late_writes(tmp_path):
    store = ThreadOwnedSQLiteRateLimitStore(str(tmp_path / "quotas.db"))
    store.close()
    store.close()
    with pytest.raises(RuntimeError, match="G3_B4_7B_RATE_LIMIT_STORE_CLOSED"):
        store.load("rpm")
