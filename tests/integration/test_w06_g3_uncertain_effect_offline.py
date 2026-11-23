"""W-06: three G3 effect-certainty witnesses with *only* disposable SQLite and fakes.

No Docker, real API keys, network, production databases, or historical volumes.
The contract oracle must PASS: UNKNOWN effects never retry automatically.
"""
import asyncio
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import time
from threading import Semaphore
from types import SimpleNamespace
from typing import cast

import pytest

from apps.llm_workers.sync_bridge import SyncProviderBridge
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManagerProtocol, QuotaReservation, QuotaRejectionReason
from core.execution.exceptions import PermanentQuotaRejection, QuotaTimeoutError
from apps.llm_workers.prompt_builder import PromptBuilder, PromptEnvelope
from core.prompting.inference_result import InferenceResult
from tests.integration._reconciler_test_factory import make_reconciler_with_test_doubles
from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, ParagraphPayload, TranslationTaskType, TranslationUnit
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


class _RecordingChunkProcessor:
    """A structural ChunkProcessor fake: no provider, only observable calls."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[tuple[ChunkPlan, TranslationUnit]] = []

    def execute_chunk(self, plan: ChunkPlan, unit: TranslationUnit) -> str:
        self.calls.append((plan, unit))
        return self.response


def test_w06_not_started_expired_lease_blocks_fake_before_io(subject):
    """A local invalid pre-I/O lease cannot reach a fake provider."""
    unit = subject.plan.units[0]
    lease = subject.repo.pick_task("w06_worker", subject.plan.document_id, subject.plan.ast_hash)
    assert lease is not None
    processor = _RecordingChunkProcessor("")
    with pytest.raises(ValueError, match="G3_B4_3A_EXPIRED_LEASE"):
        stage_claimed_unit(
            subject.repo, subject.plan, subject.ast, unit,
            replace(lease, lease_expires_at=0.0), "w06_worker", processor, Semaphore(1))
    assert processor.calls == []
    assert _row(subject)[0] == "PROCESSING"
    assert subject.queue.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0


def test_w06_confirmed_response_durable_receipt_no_second_claim(subject):
    """A validated response is bound to the attempt and not made runnable."""
    unit = subject.plan.units[0]
    lease = subject.repo.pick_task("w06_worker", subject.plan.document_id, subject.plan.ast_hash)
    assert lease is not None
    response = _response(subject.plan, unit)
    processor = _RecordingChunkProcessor(response)

    assert stage_claimed_unit(
        subject.repo, subject.plan, subject.ast, unit, lease,
        "w06_worker", processor, Semaphore(1))
    assert len(processor.calls) == 1
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
        self.accepted_calls: list[str] = []

    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        self.accepted_calls.append(envelope.chunk_id)
        if len(self.accepted_calls) == 1:
            raise TimeoutError("W06_FAKE_ACCEPTED_BUT_RESPONSE_LOST")
        # A forbidden second call remains a valid provider result so the
        # test oracle, not a malformed fake, detects any unsafe automatic retry.
        return InferenceResult(
            chunk_id=envelope.chunk_id, content=self.response,
            input_tokens=0, output_tokens=0, latency_ms=0.0,
            finish_reason="stop",
        )


def _run_post_send_loss(subject, monkeypatch):
    unit = subject.plan.units[0]
    fake = _AcceptedThenResponseLost(_response(subject.plan, unit))
    snapshots = DurableContextPlanRepository(subject.repo).load_verified(
        subject.plan.document_id, subject.plan.ast_hash, subject.ast,
    )[1]
    # The minimal builder stands in only for this offline UNKNOWN-effect
    # witness; it intentionally does not initialize production budget services.
    bridge = SyncProviderBridge(
        fake, cast(PromptBuilder, _Builder()),
        timeout_sec=1.0, context_snapshots=snapshots,
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
    assert len(fake.accepted_calls) == 1, (
        "W06_UNSAFE_RETRY: provider was called again after an uncertain effect"
    )
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
    import time

    lease = _set_reconciler_expiry(subject)
    before = subject.queue.execute(
        "SELECT execution_id FROM chunk_tasks WHERE task_id=?", (lease.task_id,)
    ).fetchone()[0]
    recon = make_reconciler_with_test_doubles(None, subject.repo, None, None, None)
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


# PPPR Gate 3 Wave 3.1: authority and uncertain effects, offline only.

def test_pppr_g3_owner_drift_while_waiting_for_semaphore_blocks_provider(subject):
    from core.execution.exceptions import G3ExternalEffectNotStartedError
    unit = subject.plan.units[0]
    lease = subject.repo.pick_task("w31", subject.plan.document_id, subject.plan.ast_hash)
    assert lease is not None
    processor = _RecordingChunkProcessor(_response(subject.plan, unit))

    class _StolenDuringWait:
        def __enter__(self):
            subject.queue.execute(
                "UPDATE chunk_tasks SET lease_owner='other',state_version=state_version+1 "
                "WHERE task_id=?", (lease.task_id,))
            subject.queue.commit()
        def __exit__(self, *args):
            return False

    with pytest.raises(G3ExternalEffectNotStartedError,
                       match="PPPR_G3_EFFECT_AUTHORITY_NOT_CURRENT"):
        stage_claimed_unit(subject.repo, subject.plan, subject.ast, unit,
                           lease, "w31", processor,
                           cast(Semaphore, _StolenDuringWait()))
    assert not processor.calls
    assert subject.queue.execute(
        "SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0
    assert not subject.repo.mark_g3_proven_no_start(
        task_id=lease.task_id, worker_id="w31", execution_id=lease.execution_id,
        cause="FENCED")


def test_pppr_g3_expired_during_wait_is_proven_no_start_and_cas_requeue(subject):
    from core.execution.exceptions import G3ExternalEffectNotStartedError
    unit = subject.plan.units[0]
    lease = subject.repo.pick_task("w31", subject.plan.document_id, subject.plan.ast_hash)
    assert lease is not None
    processor = _RecordingChunkProcessor(_response(subject.plan, unit))

    class _ExpiredDuringWait:
        def __enter__(self):
            subject.queue.execute(
                "UPDATE chunk_tasks SET lease_expires_at=1.0 WHERE task_id=?",
                (lease.task_id,))
            subject.queue.commit()
        def __exit__(self, *args):
            return False

    with pytest.raises(G3ExternalEffectNotStartedError,
                       match="PPPR_G3_EFFECT_AUTHORITY_NOT_CURRENT"):
        stage_claimed_unit(subject.repo, subject.plan, subject.ast, unit,
                           lease, "w31", processor,
                           cast(Semaphore, _ExpiredDuringWait()))
    assert not processor.calls
    assert subject.repo.mark_g3_proven_no_start(
        task_id=lease.task_id, worker_id="w31", execution_id=lease.execution_id,
        cause="PRE_EFFECT_AUTHORITY_EXPIRED")
    row = subject.queue.execute(
        "SELECT task_state,retry_count,execution_id,error_log FROM chunk_tasks "
        "WHERE task_id=?", (lease.task_id,)).fetchone()
    assert row[0:3] == ("RETRYABLE_ERROR", 1, lease.execution_id)
    assert json.loads(row[3])["code"] == "PPPR_G3_EFFECT_NOT_STARTED"
    assert not subject.repo.mark_g3_proven_no_start(
        task_id=lease.task_id, worker_id="w31", execution_id=lease.execution_id,
        cause="DUPLICATE")
    next_lease = subject.repo.pick_task(
        "w31_next", subject.plan.document_id, subject.plan.ast_hash)
    assert next_lease and next_lease.execution_id != lease.execution_id


def test_pppr_g3_no_start_requeue_respects_retry_budget(subject):
    lease = subject.repo.pick_task("w31", subject.plan.document_id, subject.plan.ast_hash)
    assert lease is not None
    subject.queue.execute(
        "UPDATE chunk_tasks SET max_retries=1 WHERE task_id=?", (lease.task_id,))
    subject.queue.commit()
    assert subject.repo.mark_g3_proven_no_start(
        task_id=lease.task_id, worker_id="w31", execution_id=lease.execution_id,
        cause="PROVIDER_MISSING_BEFORE_CALL")
    assert _row(subject) == ("FAILED", 1)
    assert subject.repo.pick_task(
        "w31_after_failure", subject.plan.document_id, subject.plan.ast_hash) is None


def test_pppr_g3_unknown_alarm_ttl_reopen_and_corrupt_record(subject, monkeypatch):
    fake, _ = _run_post_send_loss(subject, monkeypatch)
    assert len(fake.accepted_calls) == 1
    audit = json.loads(subject.queue.execute(
        "SELECT error_log FROM chunk_tasks WHERE worker_type='LLM'"
    ).fetchone()[0])
    first = audit["first_detected_at"]
    assert subject.repo.list_due_g3_unknown(30, now=first + 1) == []
    due = subject.repo.list_due_g3_unknown(30, now=first + 31)
    assert len(due) == 1 and due[0].audit_valid
    assert due[0].first_detected_at == first
    assert due[0].execution_id == audit["execution_id"]
    path = subject.queue.execute("PRAGMA database_list").fetchone()[2]
    with sqlite3.connect(path) as reopened:
        assert ControlPlaneRepository(reopened).list_due_g3_unknown(
            30, now=first + 31) == due
    subject.queue.execute(
        "UPDATE chunk_tasks SET error_log='not-json' "
        "WHERE task_state='G3_EXTERNAL_UNKNOWN'")
    subject.queue.commit()
    corrupt = subject.repo.list_due_g3_unknown(10000)
    assert len(corrupt) == 1 and not corrupt[0].audit_valid
    assert _row(subject) == ("G3_EXTERNAL_UNKNOWN", 0)
    assert subject.repo.pick_task(
        "w31_forbidden", subject.plan.document_id, subject.plan.ast_hash) is None


def test_pppr_g3_reconciler_emits_alarm_without_requeuing(subject, monkeypatch, caplog):
    fake, _ = _run_post_send_loss(subject, monkeypatch)
    assert len(fake.accepted_calls) == 1
    audit = json.loads(subject.queue.execute(
        "SELECT error_log FROM chunk_tasks WHERE worker_type='LLM'"
    ).fetchone()[0])
    audit["first_detected_at"] -= 120
    subject.queue.execute(
        "UPDATE chunk_tasks SET error_log=? WHERE worker_type='LLM'",
        (json.dumps(audit),))
    subject.queue.commit()
    before = subject.queue.execute(
        "SELECT task_state,execution_id,error_log FROM chunk_tasks "
        "WHERE worker_type='LLM'").fetchone()
    recon = make_reconciler_with_test_doubles(None, subject.repo, None, None, None)
    recon.is_leader = True
    recon.unknown_escalation_sec = 30
    with caplog.at_level("ERROR"):
        recon._escalate_g3_unknown()
    assert "PPPR_G3_UNKNOWN_OPERATOR_ESCALATION" in caplog.text
    # F18-05 R1/R2/R13: derive audit identity from durable control-plane rows
    # and keep attempt identity distinct from stable logical identifiers.
    matching = [r for r in caplog.records
                if r.getMessage() == "PPPR_G3_UNKNOWN_OPERATOR_ESCALATION"]
    assert len(matching) == 1
    entry = matching[0].extra_data
    assert entry["document_id"] == subject.plan.document_id
    assert entry["ast_hash"] == subject.plan.ast_hash
    assert entry["chunk_id"] == subject.plan.units[0].chunk_id
    assert entry["execution_id"] == before[1]
    assert entry["audit_valid"] is True
    assert entry["first_detected_at"] == audit["first_detected_at"]
    assert entry["disposition"] == "MANUAL_REVIEW_ONLY_NO_AUTO_RETRY"
    assert subject.queue.execute(
        "SELECT task_state,execution_id,error_log FROM chunk_tasks "
        "WHERE worker_type='LLM'").fetchone() == before
    assert subject.repo.pick_task(
        "w31_retry", subject.plan.document_id, subject.plan.ast_hash) is None



def test_pppr_g3_missing_unknown_audit_is_reported_not_zeroed(subject, monkeypatch, caplog):
    """F18-05 R10/R15: no audit metadata is a visible anomaly, not zero.

    In-memory alarm suppression may be lost on restart; the original durable
    UNKNOWN identity must still be discoverable and alertable. No exceptional
    retry decision is created or claimed by this test.
    """
    _run_post_send_loss(subject, monkeypatch)
    prior = subject.queue.execute(
        "SELECT task_id,document_id,ast_hash,node_id,execution_id,task_state "
        "FROM chunk_tasks WHERE worker_type='LLM'"
    ).fetchone()
    assert prior is not None and prior[5] == "G3_EXTERNAL_UNKNOWN"
    subject.queue.execute(
        "UPDATE chunk_tasks SET error_log=NULL WHERE task_id=?", (prior[0],)
    )
    subject.queue.commit()
    due = subject.repo.list_due_g3_unknown(3600)
    assert len(due) == 1 and due[0].task_id == prior[0]
    assert due[0].execution_id == prior[4]
    assert due[0].first_detected_at is None and not due[0].audit_valid

    def leader():
        daemon = make_reconciler_with_test_doubles(
            None, subject.repo, None, None, None
        )
        daemon.is_leader = True
        daemon.unknown_escalation_sec = 3600
        return daemon

    first = leader()
    with caplog.at_level("ERROR"):
        first._escalate_g3_unknown()
        first._escalate_g3_unknown()  # In-memory duplicate suppressed
        leader()._escalate_g3_unknown()  # Restart: durable UNKNOWN resurfaces

    alarms = [record for record in caplog.records
              if record.getMessage() ==
              "PPPR_G3_UNKNOWN_AUDIT_CORRUPT_REQUIRES_OPERATOR"]
    assert len(alarms) == 2
    for alarm in alarms:
        fields = alarm.extra_data
        assert fields["task_id"] == prior[0]
        assert fields["document_id"] == prior[1]
        assert fields["ast_hash"] == prior[2]
        assert fields["chunk_id"] == prior[3]
        assert fields["execution_id"] == prior[4]
        assert fields["audit_valid"] is False
        assert fields["first_detected_at"] is None
    assert subject.queue.execute(
        "SELECT task_id,document_id,ast_hash,node_id,execution_id,task_state "
        "FROM chunk_tasks WHERE worker_type='LLM'"
    ).fetchone() == prior
    assert subject.repo.pick_task(
        "w31_not_allowed", subject.plan.document_id, subject.plan.ast_hash
    ) is None


@pytest.mark.parametrize("bad_ttl", [0, -1, float("inf"), float("nan"), True])
def test_pppr_g3_invalid_unknown_escalation_ttl_rejected(subject, bad_ttl):
    with pytest.raises(ValueError, match="PPPR_G3_UNKNOWN_ESCALATION_INVALID_TTL"):
        subject.repo.list_due_g3_unknown(bad_ttl)


def test_pppr_g3_legacy_queue_plan_without_receipts_bootstraps_before_provider(subject):
    """G3 legacy queues must create receipt schema before authority SELECT.

    The old database has a valid persisted plan, but no receipt table until
    the first staging operation. No false UNKNOWN, no skip of authority checks.
    """
    subject.queue.execute("DROP TABLE chunk_result_receipts")
    subject.queue.commit()
    unit = subject.plan.units[0]
    lease = subject.repo.pick_task("w31_legacy", subject.plan.document_id,
                                   subject.plan.ast_hash)
    assert lease is not None
    processor = _RecordingChunkProcessor(_response(subject.plan, unit))
    assert stage_claimed_unit(subject.repo, subject.plan, subject.ast, unit,
                              lease, "w31_legacy", processor, Semaphore(1))
    assert len(processor.calls) == 1
    assert subject.queue.execute(
        "SELECT task_state FROM chunk_tasks WHERE task_id=?", (lease.task_id,)
    ).fetchone() == ("RESULT_STAGED",)
    assert subject.queue.execute(
        "SELECT execution_id FROM chunk_result_receipts WHERE task_id=?",
        (lease.task_id,)
    ).fetchone() == (lease.execution_id,)


def test_pppr_g3_quota_wait_expiry_blocks_external_provider(subject):
    """Real SyncProviderBridge + RateLimitedProvider, fake quota and provider.

    The first quota reservation waits and changes the *durable* lease. This
    exercises both the asyncio thread boundary and the post-quota authority
    guard: the external provider must observe zero calls.
    """
    from core.execution.exceptions import G3ExternalEffectNotStartedError

    unit = subject.plan.units[0]
    lease = subject.repo.pick_task(
        "w31_quota_wait", subject.plan.document_id, subject.plan.ast_hash
    )
    assert lease is not None
    snapshots = DurableContextPlanRepository(subject.repo).load_verified(
        subject.plan.document_id, subject.plan.ast_hash, subject.ast
    )[1]
    queue_path = subject.queue.execute("PRAGMA database_list").fetchone()[2]

    class _Quota:
        attempts = 0

        async def reserve(self, estimated_tokens: int, estimated_requests: int = 1):
            self.attempts += 1
            if self.attempts == 1:
                # The quota layer is on the bridge's asyncio thread. The
                # SQLite connection must therefore be opened in that thread.
                with sqlite3.connect(queue_path) as conn:
                    conn.execute(
                        "UPDATE chunk_tasks SET lease_expires_at=1.0 "
                        "WHERE task_id=?", (lease.task_id,)
                    )
                await asyncio.sleep(0)
                return QuotaReservation.create_rejected(
                    QuotaRejectionReason.INSUFFICIENT_RPM, 0, 0, 0
                )
            return QuotaReservation.create_granted(1, 1, 0, 10, 10)

    class _FakeProvider:
        calls = 0

        async def translate(self, envelope):
            self.calls += 1
            raise AssertionError("Provider I/O after expired quota wait")

    class _BudgetBuilder:
        model_name = "offline"
        prompt_version = "w31"

        def build(self, unit, resolved_context, target_lang_expansion=1.2):
            return SimpleNamespace(
                status="success",
                envelope=SimpleNamespace(
                    chunk_id=unit.chunk_id, estimated_tokens=1, telemetry={}
                ),
            )

    quota = _Quota()
    external = _FakeProvider()
    bridge = SyncProviderBridge(
        RateLimitedProvider(external, cast(QuotaManagerProtocol, quota), min_jitter=0,
                            max_jitter=0, max_wait_seconds=1),
        cast(PromptBuilder, _BudgetBuilder()),
        timeout_sec=5.0,
        context_snapshots=snapshots,
    )
    try:
        with pytest.raises(
            G3ExternalEffectNotStartedError,
            match="PPPR_G3_EFFECT_AUTHORITY_NOT_CURRENT",
        ):
            stage_claimed_unit(
                subject.repo, subject.plan, subject.ast, unit, lease,
                "w31_quota_wait", bridge, Semaphore(1),
            )
        assert quota.attempts == 2
        assert external.calls == 0
        assert subject.queue.execute(
            "SELECT COUNT(*) FROM chunk_result_receipts"
        ).fetchone()[0] == 0
    finally:
        bridge.shutdown()


@pytest.mark.parametrize(
    ("quota_reason", "expected_state", "expected_retries"),
    [
        (QuotaRejectionReason.CONFIGURATION_ERROR, "FAILED", 1),
        (QuotaRejectionReason.INSUFFICIENT_RPM, "FAILED", 3),
    ],
)
def test_pppr_g3_quota_rejections_never_become_external_unknown(
    subject, monkeypatch, quota_reason, expected_state, expected_retries,
):
    """Real engine, bridge and limiter; zero external calls on either quota path."""
    unit = subject.plan.units[0]
    external_calls: list[str] = []

    class _NoProvider:
        async def translate(self, envelope):
            external_calls.append(envelope.chunk_id)
            raise AssertionError("No provider dispatch permitted")

    class _Quota:
        async def reserve(self, estimated_tokens: int, estimated_requests: int = 1):
            return QuotaReservation.create_rejected(quota_reason, 1e9, 0, 0)

    class _Builder:
        model_name = "offline"
        prompt_version = "w31"

        def build(self, unit, resolved_context, target_lang_expansion=1.2):
            return SimpleNamespace(
                status="success",
                envelope=SimpleNamespace(chunk_id=unit.chunk_id, estimated_tokens=1, telemetry={}),
            )

    bridge = SyncProviderBridge(
        RateLimitedProvider(_NoProvider(), cast(QuotaManagerProtocol, _Quota()),
                            max_wait_seconds=0.01, min_jitter=0, max_jitter=0),
        cast(PromptBuilder, _Builder()), timeout_sec=5.0,
        context_snapshots=DurableContextPlanRepository(subject.repo).load_verified(
            subject.plan.document_id, subject.plan.ast_hash, subject.ast,
        )[1],
    )
    monkeypatch.setattr(
        subject.engine, "_create_chunk_processor",
        lambda contexts: (bridge, SimpleNamespace(close=lambda: None)),
    )
    result = subject.engine.run_pipeline(subject.plan.document_id, subject.plan.ast_hash)
    row = subject.queue.execute(
        "SELECT task_state,retry_count,error_log FROM chunk_tasks WHERE worker_type='LLM'"
    ).fetchone()
    assert external_calls == []
    assert row[0] == expected_state
    assert row[1] == expected_retries
    assert json.loads(row[2])["code"] == "PPPR_G3_EFFECT_NOT_STARTED"
    assert subject.queue.execute(
        "SELECT COUNT(*) FROM chunk_tasks WHERE task_state='G3_EXTERNAL_UNKNOWN'"
    ).fetchone()[0] == 0
    assert result["final_state"] != "READY_FOR_ASSEMBLY"


def test_pppr_g3_prior_sweep_failure_does_not_suppress_unknown_escalation(
    subject, monkeypatch, caplog,
):
    _run_post_send_loss(subject, monkeypatch)
    raw = subject.queue.execute(
        "SELECT error_log FROM chunk_tasks WHERE task_state='G3_EXTERNAL_UNKNOWN'"
    ).fetchone()[0]
    audit = json.loads(raw)
    audit["first_detected_at"] -= 100
    subject.queue.execute(
        "UPDATE chunk_tasks SET error_log=? WHERE task_state='G3_EXTERNAL_UNKNOWN'",
        (json.dumps(audit),),
    )
    subject.queue.commit()
    reconciler = make_reconciler_with_test_doubles(None, subject.repo, None, None, None)
    reconciler.is_leader = True
    reconciler.unknown_escalation_sec = 5

    def fail_previous_sweep(_):
        raise RuntimeError("offline injected sweep failure")

    monkeypatch.setattr(reconciler, "_sweep_tasks", fail_previous_sweep)
    monkeypatch.setattr(reconciler, "_sweep_fsm_stalls", lambda _: None)
    with caplog.at_level("ERROR"):
        reconciler._run_sweep_cycle(time.time() - 180)
        reconciler._run_sweep_cycle(time.time() - 180)
    assert "RECONCILER_tasks_SWEEP_FAILED" in caplog.text
    assert caplog.text.count("PPPR_G3_UNKNOWN_OPERATOR_ESCALATION") == 1
    assert subject.queue.execute(
        "SELECT task_state,retry_count FROM chunk_tasks WHERE worker_type='LLM'"
    ).fetchone() == ("G3_EXTERNAL_UNKNOWN", 0)
