"""G3-B4/3b: integration with real disposable SQLite DBs, no network/Groq/PDF.

Exercises durable crash boundaries, scheduler and reconciler gate. No daemon loops.
"""
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, MathPayload, ParagraphPayload, TranslationTaskType
from core.ast.grouper import SemanticGroup
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from core.chunking.publication_pipeline import advance_staged_document
from infra.db.control_repo import ControlPlaneRepository
from infra.db.fsm_repository import FSMRepository
from infra.db.staged_publication import publish_staged_plan, finalize_published_plan

ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text):
        return len(text.split())


def _plan():
    ast = [
        ASTNode(node_id="eq", sequence_id=1, node_type=ContentNodeType.DISPLAY_EQUATION,
                strategy=TranslationStrategy.PASSTHROUGH,
                payload=MathPayload(content="E=mc^2")),
        ASTNode(node_id="a", sequence_id=2, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Alpha.")),
        ASTNode(node_id="b", sequence_id=3, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content=" Beta.")),
    ]
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0),
    ).chunk_group(SemanticGroup(structural_path=(), context_id="ctx", nodes=ast), 1)
    return ast, ChunkPlan.build("doc_b43b", "ast_b43b", ast, units)


def _source_result(plan, unit):
    return json.dumps({
        "schema_version": 1, "document_id": plan.document_id,
        "ast_hash": plan.ast_hash, "manifest_sha256": plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [{
            "node_id": m.node_id, "segment_index": m.segment_index,
            "source_sha256": sha256(m.source_text.encode("utf8")).hexdigest(),
            "translated_text": f"Traduccion-{index}",
        } for index, m in enumerate(unit.members)],
    }, ensure_ascii=False)


def _create_fsm(conn, plan):
    conn.execute("""CREATE TABLE document_fsm (
        document_id TEXT NOT NULL, ast_hash TEXT NOT NULL,
        current_state TEXT NOT NULL, state_version INTEGER NOT NULL,
        is_terminal INTEGER NOT NULL DEFAULT 0, entered_state_at REAL NOT NULL,
        updated_at REAL NOT NULL, failure_reason TEXT,
        suspended_state TEXT, PRIMARY KEY(document_id, ast_hash)
    )""")
    conn.execute(
        "INSERT INTO document_fsm "
        "(document_id, ast_hash, current_state, state_version, entered_state_at, updated_at) "
        "VALUES (?,?, 'PROCESSING', 1, 1.0, 1.0)",
        (plan.document_id, plan.ast_hash),
    )
    conn.commit()


@pytest.fixture
def dbs(tmp_path):
    ast, plan = _plan()
    qc = sqlite3.connect(tmp_path / "queue.db")
    mc = sqlite3.connect(tmp_path / "materialized.db")
    fc = sqlite3.connect(tmp_path / "fsm.db")
    qc.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf8"))
    mc.executescript((ROOT / "infra/db/schema_materialized.sql").read_text(encoding="utf8"))
    _create_fsm(fc, plan)
    repo = ControlPlaneRepository(qc)
    repo.enqueue_chunk_plan(plan, ast)
    data = SimpleNamespace(ast=ast, plan=plan, q=qc, m=mc, f=fc,
                           repo=repo, fsm=FSMRepository(fc), root=tmp_path)
    try:
        yield data
    finally:
        fc.close()
        mc.close()
        qc.close()


def _stage(d):
    for _ in d.plan.units:
        lease = d.repo.pick_task("worker", d.plan.document_id, d.plan.ast_hash)
        assert lease is not None
        unit = next(u for u in d.plan.units if u.chunk_id == lease.node_id)
        response = None if unit.chunk_type == TranslationTaskType.PRESERVE else _source_result(d.plan, unit)
        d.repo.stage_chunk_result(d.plan, d.ast, chunk_id=unit.chunk_id,
                                  task_id=lease.task_id, worker_id="worker",
                                  execution_id=lease.execution_id, raw_response=response)


def _fsm_state(d):
    return d.fsm.get_status(d.plan.document_id, d.plan.ast_hash).current_state


def _states(d):
    return {row[0] for row in d.q.execute("SELECT task_state FROM chunk_tasks WHERE worker_type='LLM'")}


def _advance(d):
    return advance_staged_document(d.repo, d.m, d.fsm, d.plan, d.ast, "engine")


def test_staged_to_publication_to_completion_and_ready(dbs):
    _stage(dbs)
    assert _advance(dbs)
    assert _states(dbs) == {"COMPLETED"}
    assert _fsm_state(dbs) == "READY_FOR_ASSEMBLY"
    assert dbs.m.execute("SELECT COUNT(*) FROM g3_plan_publications").fetchone()[0] == 1
    assert dbs.m.execute("SELECT COUNT(*) FROM valid_chunks_cache").fetchone()[0] == 3
    assert dbs.q.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == len(dbs.plan.units)


def test_incomplete_tasks_do_not_publish_or_advance(dbs):
    with pytest.raises(ValueError, match="G3_B4_3B_INCOMPLETE_OR_MIXED_PLAN"):
        _advance(dbs)
    assert _fsm_state(dbs) == "PROCESSING"
    assert dbs.m.execute("SELECT COUNT(*) FROM valid_chunks_cache").fetchone()[0] == 0


def test_crash_after_publication_replays_without_reinference(dbs):
    _stage(dbs)
    with patch("core.chunking.publication_pipeline.finalize_published_plan", side_effect=RuntimeError("crash")):
        with pytest.raises(RuntimeError, match="crash"):
            _advance(dbs)
    assert _states(dbs) == {"RESULT_STAGED"}
    assert _fsm_state(dbs) == "PROCESSING"
    timestamp = dbs.m.execute("SELECT last_updated FROM valid_chunks_cache LIMIT 1").fetchone()[0]
    assert _advance(dbs)
    assert dbs.m.execute("SELECT last_updated FROM valid_chunks_cache LIMIT 1").fetchone()[0] == timestamp
    assert _states(dbs) == {"COMPLETED"}
    assert _fsm_state(dbs) == "READY_FOR_ASSEMBLY"


def test_crash_after_queue_completion_replays_to_fsm(dbs):
    _stage(dbs)
    with patch("core.chunking.publication_pipeline.DocumentCommandHandler.handle", side_effect=RuntimeError("fsm crash")):
        with pytest.raises(RuntimeError, match="fsm crash"):
            _advance(dbs)
    assert _states(dbs) == {"COMPLETED"}
    assert _fsm_state(dbs) == "PROCESSING"
    assert _advance(dbs)
    assert _fsm_state(dbs) == "READY_FOR_ASSEMBLY"


def test_completed_with_no_publication_fails_closed(dbs):
    _stage(dbs)
    publish_staged_plan(dbs.repo, dbs.m, dbs.plan, dbs.ast)
    finalize_published_plan(dbs.repo, dbs.m, dbs.plan, dbs.ast)
    dbs.m.execute("DELETE FROM g3_plan_publications")
    dbs.m.commit()
    with pytest.raises(ValueError, match="PUBLICATION_CONFLICT_OR_MISSING"):
        _advance(dbs)
    assert _fsm_state(dbs) == "PROCESSING"


def test_corrupt_projection_never_advances_fsm(dbs):
    _stage(dbs)
    publish_staged_plan(dbs.repo, dbs.m, dbs.plan, dbs.ast)
    dbs.m.execute("UPDATE valid_chunks_cache SET normalized_response='tampered'")
    dbs.m.commit()
    with pytest.raises(ValueError, match="PROJECTION_DRIFT"):
        _advance(dbs)
    assert _states(dbs) == {"RESULT_STAGED"}
    assert _fsm_state(dbs) == "PROCESSING"


def test_completed_without_receipt_never_advances_fsm(dbs):
    _stage(dbs)
    publish_staged_plan(dbs.repo, dbs.m, dbs.plan, dbs.ast)
    finalize_published_plan(dbs.repo, dbs.m, dbs.plan, dbs.ast)
    dbs.q.execute("DELETE FROM chunk_result_receipts WHERE chunk_id=?", (dbs.plan.units[0].chunk_id,))
    dbs.q.commit()
    with pytest.raises(ValueError, match="INCOMPLETE_STAGED_PLAN"):
        _advance(dbs)
    assert _fsm_state(dbs) == "PROCESSING"


def test_completed_mixed_with_staged_is_rejected(dbs):
    _stage(dbs)
    dbs.q.execute("UPDATE chunk_tasks SET task_state='COMPLETED' WHERE node_id=?",
                  (dbs.plan.units[0].chunk_id,))
    dbs.q.commit()
    with pytest.raises(ValueError, match="G3_B4_3B_INCOMPLETE_OR_MIXED_PLAN"):
        _advance(dbs)
    assert _fsm_state(dbs) == "PROCESSING"


def test_fsm_cas_cannot_retransition_out_of_processing(dbs):
    _stage(dbs)
    dbs.f.execute("UPDATE document_fsm SET current_state='CANCELLED' WHERE document_id=?",
                  (dbs.plan.document_id,))
    dbs.f.commit()
    with pytest.raises(ValueError, match="G3_B4_3B_DOCUMENT_NOT_PROCESSING"):
        _advance(dbs)
    assert _states(dbs) == {"RESULT_STAGED"}


@pytest.mark.parametrize("state", ["RESULT_STAGED", "COMPLETED"])
def test_g3_recovery_selector_handles_both_homogeneous_states(dbs, monkeypatch, state):
    _stage(dbs)
    if state == "COMPLETED":
        publish_staged_plan(dbs.repo, dbs.m, dbs.plan, dbs.ast)
        finalize_published_plan(dbs.repo, dbs.m, dbs.plan, dbs.ast)
    dbs.q.execute("ATTACH DATABASE ? AS fsm_db", (str(dbs.root / "fsm.db"),))
    dbs.q.commit()
    monkeypatch.setattr("infra.db.control_repo.ensure_fsm_database_attached", lambda conn: None)
    assert dbs.repo.find_documents_ready_for_g3_recovery() == [(dbs.plan.document_id, dbs.plan.ast_hash)]
    if state == "RESULT_STAGED":
        assert dbs.repo.find_documents_with_pending_chunks() == []


def test_g3_recovery_selector_excludes_incomplete_and_finished_fsm(dbs, monkeypatch):
    dbs.q.execute("ATTACH DATABASE ? AS fsm_db", (str(dbs.root / "fsm.db"),))
    dbs.q.commit()
    monkeypatch.setattr("infra.db.control_repo.ensure_fsm_database_attached", lambda conn: None)
    assert dbs.repo.find_documents_ready_for_g3_recovery() == []
    _stage(dbs)
    dbs.f.execute("UPDATE document_fsm SET current_state='READY_FOR_ASSEMBLY'")
    dbs.f.commit()
    assert dbs.repo.find_documents_ready_for_g3_recovery() == []


def test_failed_plus_staged_plan_is_selected_for_fatal_handling(dbs, monkeypatch):
    _stage(dbs)
    dbs.q.execute("UPDATE chunk_tasks SET task_state='FAILED' WHERE node_id=?",
                  (dbs.plan.units[0].chunk_id,))
    dbs.q.commit()
    dbs.q.execute("ATTACH DATABASE ? AS fsm_db", (str(dbs.root / "fsm.db"),))
    dbs.q.commit()
    monkeypatch.setattr("infra.db.control_repo.ensure_fsm_database_attached", lambda conn: None)
    assert dbs.repo.find_documents_ready_for_g3_recovery() == [(dbs.plan.document_id, dbs.plan.ast_hash)]


def test_g3_recovery_selector_rejects_invalid_limit(dbs):
    with pytest.raises(ValueError, match="G3_B4_3B_INVALID_SAMPLE_SIZE"):
        dbs.repo.find_documents_ready_for_g3_recovery(0)


def test_reconciler_does_not_bypass_g3_publication_barrier(dbs):
    from apps.daemons.reconciler import ReconcilerDaemon
    _stage(dbs)
    dbs.q.execute("UPDATE chunk_tasks SET task_state='COMPLETED'")
    dbs.q.commit()
    dbs.q.execute("ATTACH DATABASE ? AS fsm_db", (str(dbs.root / "fsm.db"),))
    dbs.q.commit()
    handler = SimpleNamespace(handle=lambda command: pytest.fail("unverified G3 barrier bypass"))
    recon = ReconcilerDaemon(None, dbs.repo, None, None, handler)
    recon.is_leader = True
    recon._sweep_fsm_stalls(200.0)
    assert _fsm_state(dbs) == "PROCESSING"


def test_engine_recovery_never_initializes_provider(dbs, monkeypatch):
    import runtime.engine as engine
    _stage(dbs)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(engine, "ASTRegistry", lambda: SimpleNamespace(
        get_document_ast=lambda document_id, ast_hash: dbs.ast,
    ))
    monkeypatch.setattr(engine, "compute_ast_hash", lambda ast: dbs.plan.ast_hash)
    monkeypatch.setattr(engine, "_create_chunk_processor", lambda: pytest.fail("paid provider initialized"))
    def _conn(path, timeout=30):
        return sqlite3.connect(dbs.root / Path(path).name)
    monkeypatch.setattr(engine, "get_connection", _conn)
    result = engine.run_pipeline(dbs.plan.document_id, dbs.plan.ast_hash)
    assert result["status"] == "ready_for_assembly"
    assert _states(dbs) == {"COMPLETED"}
    assert _fsm_state(dbs) == "READY_FOR_ASSEMBLY"
