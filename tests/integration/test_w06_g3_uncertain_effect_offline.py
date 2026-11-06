"""W-06: three G3 effect-certainty witnesses with *only* disposable SQLite and fakes.

No Docker, real API keys, network, production databases, or historical volumes.
The contract oracle is STRICT XFAIL until recovery differentiates UNKNOWN effects.
"""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from threading import Semaphore
from types import SimpleNamespace

import pytest

from apps.llm_workers.sync_bridge import SyncProviderBridge
from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, ParagraphPayload, TranslationTaskType
from core.ast.grouper import SemanticGroup
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from infra.db.control_repo import ControlPlaneRepository
from runtime.chunk_staging import stage_claimed_unit

ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text):
        return len(text.split())


def _response(plan, unit):
    return json.dumps({
        "schema_version": 1,
        "document_id": plan.document_id,
        "ast_hash": plan.ast_hash,
        "manifest_sha256": plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [{
            "node_id": m.node_id,
            "segment_index": m.segment_index,
            "source_sha256": sha256(m.source_text.encode("utf-8")).hexdigest(),
            "translated_text": "Traduccion simulada.",
        } for m in unit.members],
    }, ensure_ascii=False)


@pytest.fixture
def subject(tmp_path, monkeypatch):
    """One real G3 ChunkPlan; real disposable queue/FSM/materialized SQLite."""
    ast = [ASTNode(node_id="body_w06", sequence_id=1,
                   node_type=ContentNodeType.PARAGRAPH,
                   payload=ParagraphPayload(content="Observe carefully."))]
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0),
    ).chunk_group(SemanticGroup(structural_path=(), context_id="ctx_w06", nodes=ast), 1)
    plan = ChunkPlan.build("doc_w06", "ast_w06", ast, units)
    assert len(plan.units) == 1
    assert plan.units[0].chunk_type == TranslationTaskType.TRANSLATE

    q = sqlite3.connect(tmp_path / "queue.db")
    f = sqlite3.connect(tmp_path / "fsm.db")
    m = sqlite3.connect(tmp_path / "materialized.db")
    q.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    m.executescript((ROOT / "infra/db/schema_materialized.sql").read_text(encoding="utf-8"))
    f.executescript("""CREATE TABLE document_fsm (
        document_id TEXT NOT NULL, ast_hash TEXT NOT NULL,
        current_state TEXT NOT NULL, state_version INTEGER NOT NULL,
        is_terminal INTEGER NOT NULL DEFAULT 0,
        entered_state_at REAL NOT NULL, updated_at REAL NOT NULL,
        failure_reason TEXT, suspended_state TEXT,
        PRIMARY KEY(document_id, ast_hash)
    );""")
    f.execute("INSERT INTO document_fsm "
              "(document_id, ast_hash, current_state, state_version, entered_state_at, updated_at) "
              "VALUES (?, ?, 'PROCESSING', 1, 1.0, 1.0)", (plan.document_id, plan.ast_hash))
    f.commit()
    repo = ControlPlaneRepository(q)
    repo.enqueue_chunk_plan(plan, ast)

    import runtime.engine as engine
    monkeypatch.setenv("MAX_CONCURRENT_CHUNKS", "1")
    monkeypatch.setenv("IS_BENCHMARK", "0")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(engine, "ASTRegistry", lambda: SimpleNamespace(
        get_document_ast=lambda doc, ast_id: ast))
    monkeypatch.setattr(engine, "compute_ast_hash", lambda nodes: plan.ast_hash)
    monkeypatch.setattr(engine, "get_connection",
                        lambda path, timeout=30:
                        sqlite3.connect(tmp_path / Path(path).name, timeout=timeout))
    try:
        yield SimpleNamespace(repo=repo, queue=q, fsm=f, materialized=m,
                              plan=plan, ast=ast, engine=engine)
    finally:
        m.close()
        f.close()
        q.close()


def _row(subject):
    return subject.queue.execute(
        "SELECT task_state,retry_count FROM chunk_tasks "
        "WHERE document_id=? AND ast_hash=?",
        (subject.plan.document_id, subject.plan.ast_hash),
    ).fetchone()


def test_w06_not_started_expired_lease_blocks_fake_before_io(subject):
    """A local invalid pre-I/O lease cannot reach a fake provider."""
    unit = subject.plan.units[0]
    lease = subject.repo.pick_task("w06_worker", subject.plan.document_id, subject.plan.ast_hash)
    assert lease is not None
    fake_calls = []
    fake = SimpleNamespace(execute_chunk=lambda *args: fake_calls.append(args))
    with pytest.raises(ValueError, match="G3_B4_3A_EXPIRED_LEASE"):
        stage_claimed_unit(
            subject.repo, subject.plan, subject.ast, unit,
            replace(lease, lease_expires_at=0.0), "w06_worker", fake, Semaphore(1))
    assert fake_calls == []
    assert _row(subject)[0] == "PROCESSING"
    assert subject.queue.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0


def test_w06_confirmed_response_durable_receipt_no_second_claim(subject):
    """A validated response is bound to the attempt and not made runnable."""
    unit = subject.plan.units[0]
    lease = subject.repo.pick_task("w06_worker", subject.plan.document_id, subject.plan.ast_hash)
    assert lease is not None
    fake_calls = []
    response = _response(subject.plan, unit)

    def accepted(*args):
        fake_calls.append(args)
        return response

    assert stage_claimed_unit(
        subject.repo, subject.plan, subject.ast, unit, lease,
        "w06_worker", SimpleNamespace(execute_chunk=accepted), Semaphore(1))
    assert len(fake_calls) == 1
    assert _row(subject) == ("RESULT_STAGED", 0)
    # Verify bytes survive independent SQLite connection (not just a Python object).
    from contextlib import closing
    with closing(sqlite3.connect(subject.queue.execute("PRAGMA database_list").fetchone()[2])) as reopened:
        receipt = reopened.execute(
            "SELECT execution_id,raw_response,response_sha256 FROM chunk_result_receipts"
        ).fetchone()
        assert receipt == (lease.execution_id, response, sha256(response.encode("utf-8")).hexdigest())
    assert subject.repo.pick_task("w06_other", subject.plan.document_id, subject.plan.ast_hash) is None


class _Builder:
    model_name = "w06-offline"
    prompt_version = "w06"

    def build(self, unit, resolved_context, target_lang_expansion=1.2):
        return SimpleNamespace(status="success", envelope=SimpleNamespace(chunk_id=unit.chunk_id))


class _AcceptedThenResponseLost:
    """Fake receives an effect, but the *first* response is lost.

    This is a provider-interface simulation, NOT an actual HTTP/billing test.
    """
    def __init__(self, response):
        self.response = response
        self.accepted_calls = []

    async def translate(self, envelope):
        self.accepted_calls.append(envelope.chunk_id)
        if len(self.accepted_calls) == 1:
            raise TimeoutError("W06_FAKE_ACCEPTED_BUT_RESPONSE_LOST")
        return SimpleNamespace(chunk_id=envelope.chunk_id, content=self.response)


def _run_post_send_loss(subject, monkeypatch):
    unit = subject.plan.units[0]
    fake = _AcceptedThenResponseLost(_response(subject.plan, unit))
    bridge = SyncProviderBridge(fake, _Builder(), timeout_sec=1.0)
    monkeypatch.setattr(
        subject.engine, "_create_chunk_processor",
        lambda: (bridge, SimpleNamespace(close=lambda: None)),
    )
    result = subject.engine.run_pipeline(subject.plan.document_id, subject.plan.ast_hash)
    return fake, result


def test_w06_observed_uncertain_effect_gets_replayed_in_same_engine_run(subject, monkeypatch):
    """Characterization of current behavior; NOT an assertion of safety."""
    fake, result = _run_post_send_loss(subject, monkeypatch)
    # One accepted-but-unconfirmed fake effect plus a second accepted effect.
    assert len(fake.accepted_calls) == 2, (
        "W-06 behavior changed: review the strict contract oracle below")
    assert fake.accepted_calls[0] == fake.accepted_calls[1] == subject.plan.units[0].chunk_id
    assert _row(subject) == ("COMPLETED", 1)
    assert subject.queue.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 1
    assert result["status"] == "ready_for_assembly"


@pytest.mark.xfail(
    strict=True,
    reason="W-06 pending: an UNKNOWN provider effect must not be retried without disposition",
)
def test_w06_contract_oracle_never_automatically_repeats_unknown_effect(subject, monkeypatch):
    """Normative oracle intentionally XFAILs on the currently inspected code."""
    fake, _result = _run_post_send_loss(subject, monkeypatch)
    assert len(fake.accepted_calls) == 1, (
        "W06_UNSAFE_RETRY: provider accepted first call, reply was lost, "
        "but Engine made another call without an authorized UNKNOWN disposition"
    )
