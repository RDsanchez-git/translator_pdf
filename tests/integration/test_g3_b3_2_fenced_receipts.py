"""G3-B3/2: fenced durable staging in queue.db, without provider or daemon.

Uses disposable SQLite files and actual ControlPlaneRepository + B1/B2/B3 contracts.
"""
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import time

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload, MathPayload
from core.ast.grouper import SemanticGroup
from core.chunking.semantic_chunking import TokenBudgetChunker, ChunkPolicy
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.result_contract import materialize_node_results
from infra.db.control_repo import ControlPlaneRepository


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return len(text.split())


def _node(node_id, seq, text, *, preserve=False):
    return ASTNode(node_id=node_id, sequence_id=seq,
                   node_type=ContentNodeType.DISPLAY_EQUATION if preserve else ContentNodeType.PARAGRAPH,
                   strategy=TranslationStrategy.PASSTHROUGH if preserve else TranslationStrategy.TRANSLATE,
                   payload=MathPayload(content=text) if preserve else ParagraphPayload(content=text))


def _plan(*, mixed=False):
    nodes = ([_node("math", 1, "E=mc^2", preserve=True), _node("txt", 2, "Alpha beta.")]
             if mixed else [_node("a", 1, "Alpha."), _node("b", 2, " Beta.")])
    units = TokenBudgetChunker(_Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0)).chunk_group(
        SemanticGroup(structural_path=(), context_id="ctx", nodes=nodes), 1)
    return nodes, ChunkPlan.build("doc_b3_2", "ast_b3_2", nodes, units)


def _db(path):
    conn = sqlite3.connect(path)
    conn.executescript((Path(__file__).resolve().parents[2] / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    return conn


def _response(plan, unit, label="Traducido."):
    return json.dumps({
        "schema_version": 1,
        "document_id": plan.document_id,
        "ast_hash": plan.ast_hash,
        "manifest_sha256": plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [
            {"node_id": m.node_id, "segment_index": m.segment_index,
             "source_sha256": sha256(m.source_text.encode("utf-8")).hexdigest(),
             "translated_text": f"{label}{i}"}
            for i, m in enumerate(unit.members)
        ],
    }, ensure_ascii=False, separators=(",", ":"))


def _lease(repo, plan):
    lease = repo.pick_task("worker_1", plan.document_id, plan.ast_hash)
    assert lease is not None
    return lease


def _stage(repo, plan, nodes, lease, response, worker="worker_1", exec_id=None):
    return repo.stage_chunk_result(plan, nodes, chunk_id=lease.node_id,
                                   task_id=lease.task_id, worker_id=worker,
                                   execution_id=exec_id or lease.execution_id,
                                   raw_response=response)


def test_stage_reopen_replay_and_recompose_two_nodes(tmp_path):
    path = tmp_path / "queue.db"
    nodes, plan = _plan()
    with closing(_db(path)) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        raw = _response(plan, plan.units[0])
        assert _stage(repo, plan, nodes, lease, raw) is True
        assert conn.execute("SELECT task_state FROM chunk_tasks").fetchone()[0] == "RESULT_STAGED"
        assert conn.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 1
    with closing(sqlite3.connect(path)) as conn:
        repo = ControlPlaneRepository(conn)
        replayed = repo.load_staged_chunk_responses(plan, nodes)
        assert replayed == {plan.units[0].chunk_id: raw}
        materialized = materialize_node_results(plan, replayed)
        assert [m.node_id for m in materialized] == ["a", "b"]
        assert [m.text for m in materialized] == ["Traducido.0", " Traducido.1"]


def test_preserve_bypass_recovered_with_translation(tmp_path):
    nodes, plan = _plan(mixed=True)
    assert len(plan.units) == 2
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        staged = {}
        for _ in plan.units:
            lease = _lease(repo, plan)
            unit = next(u for u in plan.units if u.chunk_id == lease.node_id)
            raw = None if unit.chunk_type.value == "preserve" else _response(plan, unit, "Traducción")
            assert _stage(repo, plan, nodes, lease, raw)
            if raw is not None:
                staged[unit.chunk_id] = raw
        assert repo.load_staged_chunk_responses(plan, nodes) == staged
        materialized = materialize_node_results(plan, staged)
        assert [(m.node_id, m.text) for m in materialized] == [("math", "E=mc^2"), ("txt", "Traducción0")]


def test_incomplete_staged_plan_is_not_materializable(tmp_path):
    nodes, plan = _plan(mixed=True)
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        unit = next(u for u in plan.units if u.chunk_id == lease.node_id)
        raw = None if unit.chunk_type.value == "preserve" else _response(plan, unit)
        _stage(repo, plan, nodes, lease, raw)
        with pytest.raises(ValueError, match="G3_B3_2_INCOMPLETE_STAGED_PLAN"):
            repo.load_staged_chunk_responses(plan, nodes)


@pytest.mark.parametrize("mutation", ["other_worker", "other_execution", "expired", "pending"])
def test_bad_or_expired_lease_rejects_without_receipts(tmp_path, mutation):
    nodes, plan = _plan()
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        if mutation == "expired":
            conn.execute("UPDATE chunk_tasks SET lease_expires_at=?", (time.time() - 3,))
            conn.commit()
        if mutation == "pending":
            conn.execute("UPDATE chunk_tasks SET task_state='PENDING'")
            conn.commit()
        with pytest.raises(ValueError, match="LEASE_FENCE_REJECTED"):
            _stage(repo, plan, nodes, lease, _response(plan, plan.units[0]),
                   worker="wrong" if mutation == "other_worker" else "worker_1",
                   exec_id="wrong" if mutation == "other_execution" else None)
        assert conn.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0
        assert conn.execute("SELECT task_state FROM chunk_tasks").fetchone()[0] != "RESULT_STAGED"


def test_bad_response_rejected_before_sqlite_mutation(tmp_path):
    nodes, plan = _plan()
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        with pytest.raises(ValueError, match="G3_B3_RESPONSE_BINDING_MISMATCH"):
            _stage(repo, plan, nodes, lease, _response(plan, plan.units[0]).replace(plan.digest, "0" * 64))
        assert conn.execute("SELECT name FROM sqlite_master WHERE name='chunk_result_receipts'").fetchone() is not None
        assert conn.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0
        assert conn.execute("SELECT task_state FROM chunk_tasks").fetchone()[0] == "PROCESSING"


def test_identical_retry_is_no_op_and_conflicting_retry_is_rejected(tmp_path):
    nodes, plan = _plan()
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        raw = _response(plan, plan.units[0])
        assert _stage(repo, plan, nodes, lease, raw) is True
        state_version = conn.execute("SELECT state_version FROM chunk_tasks").fetchone()[0]
        assert _stage(repo, plan, nodes, lease, raw) is False
        assert conn.execute("SELECT state_version FROM chunk_tasks").fetchone()[0] == state_version
        with pytest.raises(ValueError, match="STAGED_RECEIPT_CONFLICT"):
            _stage(repo, plan, nodes, lease, _response(plan, plan.units[0], "Otra"))
        assert repo.load_staged_chunk_responses(plan, nodes) == {plan.units[0].chunk_id: raw}


def test_preserve_chunk_rejects_provider_result(tmp_path):
    nodes, plan = _plan(mixed=True)
    preserve = next(u for u in plan.units if u.chunk_type.value == "preserve")
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        leases = [_lease(repo, plan) for _ in plan.units]
        lease = next(item for item in leases if item.node_id == preserve.chunk_id)
        with pytest.raises(ValueError, match="PRESERVE_MUST_BYPASS_PROVIDER"):
            _stage(repo, plan, nodes, lease, "{}")
        assert conn.execute("SELECT task_state FROM chunk_tasks WHERE task_id=?", (lease.task_id,)).fetchone()[0] == "PROCESSING"


def test_injected_update_failure_rolls_back_receipt_and_state(tmp_path):
    nodes, plan = _plan()
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        conn.execute("""CREATE TRIGGER fail_staging BEFORE UPDATE ON chunk_tasks
                        WHEN NEW.task_state='RESULT_STAGED'
                        BEGIN SELECT RAISE(ABORT, 'synthetic staging failure'); END""")
        conn.commit()
        with pytest.raises(sqlite3.IntegrityError, match="synthetic staging failure"):
            _stage(repo, plan, nodes, lease, _response(plan, plan.units[0]))
        assert conn.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0
        assert conn.execute("SELECT task_state FROM chunk_tasks").fetchone()[0] == "PROCESSING"


def test_nested_transaction_owned_by_caller_is_not_committed(tmp_path):
    path = tmp_path / "queue.db"
    nodes, plan = _plan()
    with closing(_db(path)) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        conn.execute("BEGIN")
        _stage(repo, plan, nodes, lease, _response(plan, plan.units[0]))
        assert conn.in_transaction
        conn.rollback()
    with closing(sqlite3.connect(path)) as conn:
        assert conn.execute("SELECT task_state FROM chunk_tasks").fetchone()[0] == "PROCESSING"
        assert conn.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 0


def test_corrupt_receipt_checksum_rejected_for_replay(tmp_path):
    nodes, plan = _plan()
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        _stage(repo, plan, nodes, lease, _response(plan, plan.units[0]))
        conn.execute("UPDATE chunk_result_receipts SET response_sha256=?", ("0" * 64,))
        conn.commit()
        with pytest.raises(ValueError, match="RECEIPT_CHECKSUM_MISMATCH"):
            repo.load_staged_chunk_responses(plan, nodes)


@pytest.mark.parametrize("field", ["task_state", "execution_id"])
def test_drift_between_receipts_and_queue_blocks_replay(tmp_path, field):
    nodes, plan = _plan()
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        _stage(repo, plan, nodes, lease, _response(plan, plan.units[0]))
        if field == "task_state":
            conn.execute("UPDATE chunk_tasks SET task_state='PENDING'")
        else:
            conn.execute("UPDATE chunk_tasks SET execution_id='other'")
        conn.commit()
        with pytest.raises(ValueError, match="RECEIPT_QUEUE_DRIFT"):
            repo.load_staged_chunk_responses(plan, nodes)


def test_old_queue_schema_without_receipts_upgrades_on_first_stage(tmp_path):
    nodes, plan = _plan()
    with closing(_db(tmp_path / "queue.db")) as conn:
        conn.execute("DROP TABLE chunk_result_receipts")
        conn.commit()
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, nodes)
        lease = _lease(repo, plan)
        assert _stage(repo, plan, nodes, lease, _response(plan, plan.units[0])) is True
        assert conn.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == 1
