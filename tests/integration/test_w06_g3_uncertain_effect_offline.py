"""W-06: three G3 effect-certainty witnesses with *only* disposable SQLite and fakes.

No Docker, real API keys, network, production databases, or historical volumes.
The contract oracle must PASS: UNKNOWN effects never retry automatically.
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
from core.chunking.contextual_plan import prepare_contextual_plan
from infra.db.context_snapshot_repo import DurableContextPlanRepository
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
    prepared = prepare_contextual_plan(
        document_id="doc_w06", raw_ast=ast, estimator=_Estimator(),
    )
    ast = list(prepared.ast)
    plan = prepared.plan
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
    DurableContextPlanRepository(repo).enqueue_verified(plan, ast)

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
    snapshots = DurableContextPlanRepository(subject.repo).load_verified(
        subject.plan.document_id, subject.plan.ast_hash, subject.ast,
    )[1]
    bridge = SyncProviderBridge(
        fake, _Builder(), timeout_sec=1.0, context_snapshots=snapshots,
    )
    monkeypatch.setattr(
        subject.engine, "_create_chunk_processor",
        lambda _contexts: (bridge, SimpleNamespace(close=lambda: None)),
    )
    result = subject.engine.run_pipeline(subject.plan.document_id, subject.plan.ast_hash)
    return fake, result


def test_w06_lost_reply_is_quarantined_without_second_provider_call(subject, monkeypatch):
    """A provider-accepted first call has no second automatic effect."""
    fake, result = _run_post_send_loss(subject, monkeypatch)
    assert len(fake.accepted_calls) == 1
    assert _row(subject) == ("G3_EXTERNAL_UNKNOWN", 0)
    assert subject.queue.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0
    row = subject.queue.execute(
        "SELECT execution_id,error_log FROM chunk_tasks WHERE worker_type='LLM'"
    ).fetchone()
    audit = json.loads(row[1])
    assert audit["execution_id"] == row[0]
    assert audit["first_detected_at"] > 0
    assert audit["code"] == "G3_W06_EXTERNAL_UNKNOWN"
    assert result["status"] == "staging_incomplete"
    assert subject.repo.pick_task("w06_retry", subject.plan.document_id, subject.plan.ast_hash) is None


def test_w06_contract_oracle_never_automatically_repeats_unknown_effect(subject, monkeypatch):
    """The former strict XFAIL is an actual PASS only after W06-R1."""
    fake, _result = _run_post_send_loss(subject, monkeypatch)
    assert len(fake.accepted_calls) == 1, (
        "W06_UNSAFE_RETRY: provider accepted first call, reply was lost, "
        "but Engine made another call without an authorized UNKNOWN disposition"
    )


def test_w06_restart_never_reinitializes_provider_for_unknown(subject, monkeypatch):
    fake, _ = _run_post_send_loss(subject, monkeypatch)
    initial = subject.queue.execute(
        "SELECT task_state,execution_id,error_log FROM chunk_tasks"
    ).fetchone()
    assert len(fake.accepted_calls) == 1
    monkeypatch.setattr(subject.engine, "_create_chunk_processor",
                        lambda _contexts: pytest.fail("UNKNOWN initiated paid inference"))
    result = subject.engine.run_pipeline(subject.plan.document_id, subject.plan.ast_hash)
    assert result["status"] == "staging_incomplete"
    assert subject.queue.execute(
        "SELECT task_state,execution_id,error_log FROM chunk_tasks"
    ).fetchone() == initial
    assert len(fake.accepted_calls) == 1


def _set_reconciler_expiry(subject, *, worker="w06_worker"):
    """Establish a real lease, expired snapshot, and independent FSM attachment."""
    import time
    lease = subject.repo.pick_task(worker, subject.plan.document_id, subject.plan.ast_hash)
    assert lease is not None
    now = time.time()
    subject.queue.execute(
        "UPDATE system_leases SET owner_id='recon_w06',lease_version=7,"
        "lease_expires_at=?,updated_at=? WHERE lease_name='global_reconciler'",
        (now + 300, now),
    )
    subject.queue.execute(
        "UPDATE chunk_tasks SET lease_expires_at=?,updated_at=? WHERE task_id=?",
        (now - 500, now - 500, lease.task_id),
    )
    dbfile = subject.fsm.execute("PRAGMA database_list").fetchone()[2]
    subject.queue.execute("ATTACH DATABASE ? AS fsm_db", (dbfile,))
    subject.queue.commit()
    return lease


def test_w06_reconciler_quarantines_expired_translate_without_receipt(subject):
    """A crashed TRANSLATE may have called provider; missing receipt proves nothing."""
    from apps.daemons.reconciler import ReconcilerDaemon
    import time

    lease = _set_reconciler_expiry(subject)
    before = subject.queue.execute(
        "SELECT execution_id FROM chunk_tasks WHERE task_id=?", (lease.task_id,)
    ).fetchone()[0]
    recon = ReconcilerDaemon(None, subject.repo, None, None, None)
    recon.is_leader = True
    recon.node_id = "recon_w06"
    recon.current_epoch = 7
    recon._sweep_tasks(time.time() - 180)
    row = subject.queue.execute(
        "SELECT task_state,execution_id,error_log FROM chunk_tasks "
        "WHERE task_id=?", (lease.task_id,)
    ).fetchone()
    assert row[0] == "G3_EXTERNAL_UNKNOWN"
    assert row[1] == before
    audit = json.loads(row[2])
    assert audit["first_detected_at"] > 0
    assert audit["execution_id"] == lease.execution_id
    assert audit["cause"] == "LEASE_EXPIRED_WITHOUT_RECEIPT"
    assert subject.repo.pick_task("replay_worker", subject.plan.document_id, subject.plan.ast_hash) is None
    previous = row
    recon._sweep_tasks(time.time() - 180)
    assert subject.queue.execute(
        "SELECT task_state,execution_id,error_log FROM chunk_tasks "
        "WHERE task_id=?", (lease.task_id,)
    ).fetchone() == previous


def test_w06_unknown_survives_new_sqlite_connection(subject, monkeypatch):
    """Quarantine and provenance survive connection close/reopen, not only memory."""
    fake, _ = _run_post_send_loss(subject, monkeypatch)
    assert len(fake.accepted_calls) == 1
    path = subject.queue.execute("PRAGMA database_list").fetchone()[2]
    with sqlite3.connect(path) as conn:
        row = conn.execute("SELECT task_state,execution_id,error_log FROM chunk_tasks").fetchone()
        assert row[0] == "G3_EXTERNAL_UNKNOWN"
        assert json.loads(row[2])["execution_id"] == row[1]
        repo = ControlPlaneRepository(conn)
        assert repo.pick_task("restarted", subject.plan.document_id, subject.plan.ast_hash) is None
