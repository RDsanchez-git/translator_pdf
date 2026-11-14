"""G3-B4/9: legacy reconciliation isolation and fenced recovery, offline SQLite.

All writes use disposable SQLite; no network, paid provider, Docker or production DB.
"""
from pathlib import Path
import sqlite3
import time
from types import SimpleNamespace

import pytest

from apps.daemons.reconciler import ReconcilerDaemon
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, MathPayload
from core.ast.grouper import SemanticGroup
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from core.execution.handlers import ReconciliationCommandHandler
from core.metrics.metrics import Metrics
from core.execution.state import RematerializeTaskCommand, RecoverZombieTaskCommand
from infra.db.control_repo import ControlPlaneRepository

ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return len(text.split())


@pytest.fixture
def state():
    q = sqlite3.connect(':memory:')
    q.executescript((ROOT / 'infra/db/schema_queue.sql').read_text(encoding='utf-8'))
    q.execute('CREATE TABLE processed_reconciliation_commands '
              '(reconciliation_id TEXT PRIMARY KEY, processed_at REAL NOT NULL)')
    q.execute("ATTACH DATABASE ':memory:' AS fsm_db")
    q.execute('CREATE TABLE fsm_db.document_fsm '
              '(document_id TEXT, ast_hash TEXT, current_state TEXT, '
              'state_version INTEGER NOT NULL DEFAULT 0, '
              'is_terminal INTEGER NOT NULL DEFAULT 0)')
    ast = [ASTNode(node_id='math_g3b49', sequence_id=1,
                   node_type=ContentNodeType.DISPLAY_EQUATION,
                   strategy=TranslationStrategy.PASSTHROUGH,
                   payload=MathPayload(content='E=mc^2'))]
    units = TokenBudgetChunker(_Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0)).chunk_group(
        SemanticGroup(structural_path=(), context_id='ctx', nodes=ast), 1)
    plan = ChunkPlan.build('doc_g3b49', 'ast_g3b49', ast, units)
    repo = ControlPlaneRepository(q)
    repo.enqueue_chunk_plan(plan, ast)
    lease = repo.pick_task('worker_old', plan.document_id, plan.ast_hash)
    assert lease and repo.is_g3_chunk_task(lease.task_id)
    q.execute('INSERT INTO fsm_db.document_fsm '
              '(document_id,ast_hash,current_state) VALUES (?,?,?)',
              (plan.document_id, plan.ast_hash, 'PROCESSING'))
    now = time.time()
    q.execute('UPDATE system_leases SET owner_id=?,lease_version=?,lease_expires_at=? '
              "WHERE lease_name='global_reconciler'", ('recon_a', 7, now + 120))
    q.execute('UPDATE chunk_tasks SET lease_expires_at=?,updated_at=? WHERE task_id=?',
              (now - 400, now - 500, lease.task_id))
    q.commit()
    try:
        yield SimpleNamespace(q=q, repo=repo, plan=plan, ast=ast, lease=lease)
    finally:
        q.close()


def _row(s):
    return s.q.execute('SELECT task_state,lease_owner,execution_id,lease_expires_at,'
                       'updated_at,state_version,retry_count FROM chunk_tasks WHERE task_id=?',
                       (s.lease.task_id,)).fetchone()


def _attempt(s, *, epoch=7, owner='recon_a', snapshot=None):
    row = snapshot or _row(s)
    return s.repo.recover_expired_g3_task(
        task_id=s.lease.task_id, document_id=s.plan.document_id,
        ast_hash=s.plan.ast_hash, chunk_id=s.lease.node_id,
        expected_owner=row[1], expected_execution_id=row[2],
        expected_expiry=row[3], expected_updated_at=row[4], expected_version=row[5],
        reconciler_owner=owner, reconciler_epoch=epoch,
        stale_before=time.time() - 180,
    )


def test_fenced_expired_g3_requeued_only_once_and_reclaimed(state):
    old = _row(state)
    assert _attempt(state, snapshot=old) is True
    assert _attempt(state, snapshot=old) is False
    new = _row(state)
    assert new[0] == 'PENDING' and new[1] is None and new[2] is None
    assert new[5] == old[5] + 1 and new[6] == old[6] + 1
    lease = state.repo.pick_task('worker_new', state.plan.document_id, state.plan.ast_hash)
    assert lease and lease.execution_id != state.lease.execution_id


def test_stale_lease_cannot_stage_after_fenced_reclaim(state):
    assert _attempt(state)
    newlease = state.repo.pick_task('worker_new', state.plan.document_id, state.plan.ast_hash)
    assert newlease
    with pytest.raises(ValueError, match='LEASE_FENCE_REJECTED'):
        state.repo.stage_chunk_result(state.plan, state.ast,
             chunk_id=state.lease.node_id, task_id=state.lease.task_id,
             worker_id='worker_old', execution_id=state.lease.execution_id,
             raw_response=None)
    assert state.repo.stage_chunk_result(state.plan, state.ast,
         chunk_id=newlease.node_id, task_id=newlease.task_id,
         worker_id='worker_new', execution_id=newlease.execution_id,
         raw_response=None)


@pytest.mark.parametrize('mutation', ['wrong_epoch', 'wrong_owner', 'renewed_lease', 'fsm_cancelled'])
def test_fenced_recovery_rejects_stale_authority(state, mutation):
    snapshot = _row(state)
    if mutation == 'wrong_epoch':
        ok = _attempt(state, epoch=6, snapshot=snapshot)
    elif mutation == 'wrong_owner':
        ok = _attempt(state, owner='other', snapshot=snapshot)
    elif mutation == 'renewed_lease':
        state.q.execute('UPDATE chunk_tasks SET lease_expires_at=?,updated_at=? WHERE task_id=?',
                        (time.time()+500, time.time(), state.lease.task_id))
        state.q.commit()
        ok = _attempt(state, snapshot=snapshot)
    else:
        state.q.execute("UPDATE fsm_db.document_fsm SET current_state='CANCELLED'")
        state.q.commit()
        ok = _attempt(state, snapshot=snapshot)
    assert ok is False
    assert _row(state)[0] == 'PROCESSING'


def test_g3_staged_receipt_cannot_be_rewound_or_completed_by_legacy(state):
    state.q.execute('UPDATE chunk_tasks SET lease_expires_at=? WHERE task_id=?',
                    (time.time()+500, state.lease.task_id))
    state.q.commit()
    assert state.repo.stage_chunk_result(state.plan, state.ast,
           chunk_id=state.lease.node_id, task_id=state.lease.task_id,
           worker_id='worker_old', execution_id=state.lease.execution_id,
           raw_response=None)
    before = _row(state)
    assert state.repo.mark_zombie_recovered(state.lease.task_id, 'stale_legacy') is False
    assert state.repo.mark_cqrs_reconciled(state.lease.task_id, 'stale_cqrs') is False
    assert _row(state) == before
    assert state.q.execute('SELECT COUNT(*) FROM chunk_result_receipts').fetchone()[0] == 1
    assert state.q.execute('SELECT COUNT(*) FROM processed_reconciliation_commands').fetchone()[0] == 0
    assert _attempt(state) is False


def test_g3_no_receipt_never_cqrs_completes(state):
    before = _row(state)
    assert state.repo.mark_cqrs_reconciled(state.lease.task_id, 'no_receipt') is False
    assert state.repo.mark_zombie_recovered(state.lease.task_id, 'legacy_requeue') is False
    assert _row(state) == before
    assert state.q.execute('SELECT COUNT(*) FROM processed_reconciliation_commands').fetchone()[0] == 0


def test_legacy_reconciliation_without_g3_manifest_preserved(state):
    state.q.execute('INSERT INTO chunk_tasks (task_id,document_id,ast_hash,node_id,task_state,'
                    'lease_owner,lease_expires_at,created_at,updated_at) '
                    "VALUES ('legacy_task','legacy_doc','legacy_ast','legacy_node','PROCESSING',"
                    "'old',1,1,1)")
    state.q.commit()
    assert state.repo.is_g3_chunk_task('legacy_task') is False
    assert state.repo.mark_zombie_recovered('legacy_task', 'legacy_zombie') is True
    assert state.q.execute("SELECT task_state FROM chunk_tasks WHERE task_id='legacy_task'").fetchone() == ('PENDING',)
    assert state.repo.mark_cqrs_reconciled('legacy_task', 'legacy_cqrs') is True
    assert state.q.execute("SELECT task_state FROM chunk_tasks WHERE task_id='legacy_task'").fetchone() == ('COMPLETED',)


def test_reconciler_routes_g3_without_legacy_event_or_handler(state):
    def forbidden(*args, **kwargs):
        pytest.fail('G3 must not call legacy event/handler')
    event = SimpleNamespace(get_latest_event=forbidden)
    handler = SimpleNamespace(handle=forbidden)
    reconciler = ReconcilerDaemon(None, state.repo, event, handler, None)
    reconciler.is_leader = True
    reconciler.node_id = 'recon_a'
    reconciler.current_epoch = 7
    reconciler._sweep_tasks(time.time()-180)
    assert _row(state)[0] == 'PENDING'


def test_handler_direct_g3_rematerialization_has_no_materialized_side_effect(state):
    def forbidden(*args, **kwargs):
        pytest.fail('G3 legacy rematerialization read/write attempted')
    handler = ReconciliationCommandHandler(
        system_repo=SimpleNamespace(get_current_epoch=lambda _: 7),
        task_repo=state.repo,
        event_repo=SimpleNamespace(get_latest_event=forbidden),
        mat_repo=SimpleNamespace(upsert_projection=forbidden),
        metrics=Metrics(),
    )
    cmd = RematerializeTaskCommand(reconciliation_id='stale_g3', reconciler_epoch=7,
                                   task_id=state.lease.task_id, document_id=state.plan.document_id,
                                   ast_hash=state.plan.ast_hash, node_id=state.lease.node_id,
                                   content_hash='x')
    assert handler.handle_rematerialize(cmd) is None
    cmd2 = RecoverZombieTaskCommand(reconciliation_id='stale_g3z', reconciler_epoch=7,
                                     task_id=state.lease.task_id, document_id=state.plan.document_id)
    assert handler.handle_recover_zombie(cmd2) is None
    assert _row(state)[0] == 'PROCESSING'


def test_reconciler_heartbeat_sqlite_connection_is_owned_by_heartbeat_thread():
    import threading

    main_thread = threading.get_ident()
    observed = []

    class _SingleBeat(threading.Event):
        calls = 0

        def wait(self, timeout: float | None = None) -> bool:
            self.calls += 1
            return self.calls > 1

    class _System:
        def __init__(self, conn):
            self.conn = conn

        def renew_leadership(self, name, node, ttl):
            self.conn.execute('SELECT 1').fetchone()  # check_same_thread=True
            observed.append((threading.get_ident(), name, node, ttl))
            return True

    def factory():
        conn = sqlite3.connect(':memory:')  # created inside worker thread
        return _System(conn), conn

    reconciler = ReconcilerDaemon(None, None, None, None, None,
                                   heartbeat_system_factory=factory)
    reconciler.stop_event = _SingleBeat()
    reconciler.is_leader = True
    thread = threading.Thread(target=reconciler._leadership_heartbeat)
    thread.start()
    thread.join(timeout=10)
    assert not thread.is_alive()
    assert len(observed) == 1
    assert observed[0][0] != main_thread
    assert observed[0][1:] == ('global_reconciler', reconciler.node_id, 120)
    assert reconciler.is_leader is True


def test_g3_assembler_trigger_is_never_requeued_by_legacy_handler(state):
    assert state.repo.enqueue_assembler_task('assembly_trigger_b49',
                                              state.plan.document_id, state.plan.ast_hash)
    now = time.time()
    state.q.execute("UPDATE chunk_tasks SET task_state='PROCESSING',lease_owner='old_assembler',"
                    "execution_id='exec_old_assembler',lease_expires_at=?,updated_at=? "
                    "WHERE task_id='assembly_trigger_b49'", (now - 400, now - 500))
    state.q.commit()
    assert state.repo.is_g3_chunk_task('assembly_trigger_b49')
    assert state.repo.mark_zombie_recovered('assembly_trigger_b49', 'legacy_assembly') is False
    assert state.q.execute("SELECT task_state FROM chunk_tasks WHERE task_id='assembly_trigger_b49'").fetchone() == ('PROCESSING',)
    def forbidden(*args, **kwargs):
        pytest.fail('G3 ASSEMBLER cannot use legacy reconciliation')
    recon = ReconcilerDaemon(None, state.repo,
                             SimpleNamespace(get_latest_event=forbidden),
                             SimpleNamespace(handle=forbidden), None)
    recon.is_leader = True
    recon.node_id = 'recon_a'
    recon.current_epoch = 7
    recon._sweep_tasks(time.time() - 180)
    assert state.q.execute("SELECT task_state FROM chunk_tasks WHERE task_id='assembly_trigger_b49'").fetchone() == ('PROCESSING',)
    assert _row(state)[0] == 'PENDING'


def test_g3_recovery_creates_receipt_table_if_old_queue_has_no_receipts(state):
    state.q.execute('DROP TABLE chunk_result_receipts')
    state.q.commit()
    assert _attempt(state) is True
    assert state.q.execute("SELECT name FROM sqlite_master WHERE name='chunk_result_receipts'").fetchone() == ('chunk_result_receipts',)
