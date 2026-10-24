"""G3-B3/3b: publication barrier, crash recovery and atomic queue confirmation.

All SQLite files are disposable. No provider, daemon, network or PDF renderer.
"""
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import time
from unittest.mock import patch

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload, MathPayload
from core.ast.grouper import SemanticGroup
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from core.chunking.manifest_contract import ChunkPlan
from infra.db.control_repo import ControlPlaneRepository
from infra.db.staged_publication import publish_staged_plan, finalize_published_plan


class _Estimator:
    def estimate_tokens(self, value):
        return len(value.split())


def _node(node_id, seq, text, preserve=False):
    return ASTNode(
        node_id=node_id, sequence_id=seq,
        node_type=ContentNodeType.DISPLAY_EQUATION if preserve else ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.PASSTHROUGH if preserve else TranslationStrategy.TRANSLATE,
        payload=MathPayload(content=text) if preserve else ParagraphPayload(content=text),
    )


def _plan(mixed=False):
    nodes = ([_node('math', 1, 'E=mc²', True), _node('text', 2, ' Alpha beta.')]
             if mixed else [_node('one', 1, 'Alpha.'), _node('two', 2, ' Beta.')])
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0)
    ).chunk_group(SemanticGroup(structural_path=(), context_id='ctx', nodes=nodes), 1)
    return nodes, ChunkPlan.build('doc_finish', 'ast_finish', nodes, units)


def _connect(path, filename):
    con = sqlite3.connect(path)
    con.executescript((Path(__file__).resolve().parents[2] / 'infra/db' / filename).read_text(encoding='utf-8'))
    return con


def _response(plan, unit):
    return json.dumps({
        'schema_version': 1, 'document_id': plan.document_id, 'ast_hash': plan.ast_hash,
        'manifest_sha256': plan.digest, 'chunk_id': unit.chunk_id,
        'members': [
            {'node_id': m.node_id, 'segment_index': m.segment_index,
             'source_sha256': sha256(m.source_text.encode('utf-8')).hexdigest(),
             'translated_text': 'Traducido ' + str(idx)}
            for idx, m in enumerate(unit.members)
        ],
    }, ensure_ascii=False)


def _setup(tmp_path, *, mixed=False, stage=True, publish=True):
    ast, plan = _plan(mixed)
    queue_conn = _connect(tmp_path / 'queue.db', 'schema_queue.sql')
    materialized_conn = _connect(tmp_path / 'materialized.db', 'schema_materialized.sql')
    queue = ControlPlaneRepository(queue_conn)
    queue.enqueue_chunk_plan(plan, ast)
    if stage:
        for _ in plan.units:
            lease = queue.pick_task('worker_test', plan.document_id, plan.ast_hash)
            assert lease is not None
            unit = next(u for u in plan.units if u.chunk_id == lease.node_id)
            assert queue.stage_chunk_result(
                plan, ast, chunk_id=unit.chunk_id, task_id=lease.task_id,
                worker_id='worker_test', execution_id=lease.execution_id,
                raw_response=None if unit.chunk_type.value == 'preserve' else _response(plan, unit),
            )
    if publish:
        assert publish_staged_plan(queue, materialized_conn, plan, ast) is True
    return ast, plan, queue_conn, materialized_conn, queue


def _task_rows(qc):
    return qc.execute('SELECT node_id,task_state,execution_id,lease_owner,lease_expires_at,'
                      'state_version,updated_at FROM chunk_tasks ORDER BY node_id').fetchall()


def test_full_plan_finalizes_atomically(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path, mixed=True)
    with closing(qc), closing(mc):
        assert len(plan.units) == 2
        before = _task_rows(qc)
        assert all(r[1] == 'RESULT_STAGED' for r in before)
        assert finalize_published_plan(q, mc, plan, ast) is True
        after = _task_rows(qc)
        assert all(r[1] == 'COMPLETED' and r[3] is None and r[4] is None for r in after)
        assert all(new[5] == old[5] + 1 and new[2] == old[2]
                   for old, new in zip(before, after))
        assert qc.execute('SELECT COUNT(*) FROM chunk_result_receipts').fetchone()[0] == 2


def test_replay_is_idempotent_and_preserves_timestamps(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        assert finalize_published_plan(q, mc, plan, ast)
        expected = _task_rows(qc)
        assert finalize_published_plan(q, mc, plan, ast) is False
        assert _task_rows(qc) == expected


def test_replay_after_reopening_both_databases(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path, mixed=True)
    with closing(qc), closing(mc):
        assert finalize_published_plan(q, mc, plan, ast)
    with closing(sqlite3.connect(tmp_path / 'queue.db')) as q2, closing(sqlite3.connect(tmp_path / 'materialized.db')) as m2:
        assert finalize_published_plan(ControlPlaneRepository(q2), m2, plan, ast) is False
        assert set(q2.execute('SELECT task_state FROM chunk_tasks')) == {('COMPLETED',)}


def test_recovery_after_crash_between_publication_and_completion(tmp_path):
    ast, plan, qc, mc, _ = _setup(tmp_path, mixed=True)
    with closing(qc), closing(mc):
        assert set(qc.execute('SELECT task_state FROM chunk_tasks')) == {('RESULT_STAGED',)}
    with closing(sqlite3.connect(tmp_path / 'queue.db')) as q2, closing(sqlite3.connect(tmp_path / 'materialized.db')) as m2:
        assert finalize_published_plan(ControlPlaneRepository(q2), m2, plan, ast) is True
        assert set(q2.execute('SELECT task_state FROM chunk_tasks')) == {('COMPLETED',)}


def test_missing_publication_rejects_without_marking_completed(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path, publish=False)
    with closing(qc), closing(mc):
        with pytest.raises(ValueError, match='PUBLICATION_CONFLICT_OR_MISSING'):
            finalize_published_plan(q, mc, plan, ast)
        assert set(qc.execute('SELECT task_state FROM chunk_tasks')) == {('RESULT_STAGED',)}


def test_uncommitted_materialized_publication_cannot_authorize_completion(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path, publish=False)
    with closing(qc), closing(mc):
        mc.execute('BEGIN')
        assert publish_staged_plan(q, mc, plan, ast) is True  # caller owns commit
        with pytest.raises(ValueError, match='UNCOMMITTED_PUBLICATION'):
            finalize_published_plan(q, mc, plan, ast)
        mc.rollback()
        assert set(qc.execute('SELECT task_state FROM chunk_tasks')) == {('RESULT_STAGED',)}


def test_corrupt_materialized_projection_blocks_completion(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        mc.execute("UPDATE valid_chunks_cache SET normalized_response='tampered' WHERE node_id='one'")
        mc.commit()
        with pytest.raises(ValueError, match='PROJECTION_DRIFT'):
            finalize_published_plan(q, mc, plan, ast)
        assert set(qc.execute('SELECT task_state FROM chunk_tasks')) == {('RESULT_STAGED',)}


def test_altered_publication_digest_blocks_completion(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        mc.execute("UPDATE g3_plan_publications SET result_sha256=?", ('0'*64,))
        mc.commit()
        with pytest.raises(ValueError, match='PUBLICATION_CONFLICT_OR_MISSING'):
            finalize_published_plan(q, mc, plan, ast)


def test_corrupt_queue_receipt_blocks_completion(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        qc.execute('UPDATE chunk_result_receipts SET response_sha256=?', ('0'*64,))
        qc.commit()
        with pytest.raises(ValueError, match='RECEIPT_CHECKSUM_MISMATCH'):
            finalize_published_plan(q, mc, plan, ast)
        assert set(qc.execute('SELECT task_state FROM chunk_tasks')) == {('RESULT_STAGED',)}


def test_missing_receipt_blocks_completion(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        qc.execute('DELETE FROM chunk_result_receipts')
        qc.commit()
        with pytest.raises(ValueError, match='INCOMPLETE_STAGED_PLAN'):
            finalize_published_plan(q, mc, plan, ast)


def test_execution_identity_drift_blocks_completion(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        qc.execute("UPDATE chunk_tasks SET execution_id='wrong'")
        qc.commit()
        with pytest.raises(ValueError, match='RECEIPT_QUEUE_DRIFT'):
            finalize_published_plan(q, mc, plan, ast)


def test_half_completed_plan_fails_closed(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path, mixed=True)
    with closing(qc), closing(mc):
        qc.execute("UPDATE chunk_tasks SET task_state='COMPLETED' WHERE node_id=?", (plan.units[0].chunk_id,))
        qc.commit()
        with pytest.raises(ValueError, match='INCOMPLETE_OR_MIXED_STATES'):
            finalize_published_plan(q, mc, plan, ast)


def test_queue_update_trigger_rolls_back_whole_plan(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path, mixed=True)
    with closing(qc), closing(mc):
        before = _task_rows(qc)
        second_task = qc.execute('SELECT task_id FROM chunk_tasks ORDER BY rowid DESC LIMIT 1').fetchone()[0]
        qc.execute("CREATE TRIGGER g3_abort_second BEFORE UPDATE ON chunk_tasks "
                   "WHEN NEW.task_id='" + second_task + "' AND NEW.task_state='COMPLETED' "
                   "BEGIN SELECT RAISE(ABORT, 'injected completion failure'); END;")
        qc.commit()
        with pytest.raises(sqlite3.IntegrityError, match='injected completion failure'):
            finalize_published_plan(q, mc, plan, ast)
        assert _task_rows(qc) == before
        qc.execute('DROP TRIGGER g3_abort_second')
        qc.commit()
        assert finalize_published_plan(q, mc, plan, ast)


def test_expired_lease_does_not_block_recovery_from_durable_staged_receipt(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        qc.execute('UPDATE chunk_tasks SET lease_expires_at=?', (time.time() - 500,))
        qc.commit()
        assert finalize_published_plan(q, mc, plan, ast) is True


def test_missing_owner_fails_closed(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        qc.execute('UPDATE chunk_tasks SET lease_owner=NULL')
        qc.commit()
        with pytest.raises(ValueError, match='MISSING_STAGED_AUTHORITY'):
            finalize_published_plan(q, mc, plan, ast)


def test_nested_queue_transaction_ownership(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        qc.execute('BEGIN')
        assert finalize_published_plan(q, mc, plan, ast) is True
        assert qc.in_transaction
        qc.rollback()
        assert set(qc.execute('SELECT task_state FROM chunk_tasks')) == {('RESULT_STAGED',)}
        assert finalize_published_plan(q, mc, plan, ast) is True


def test_already_completed_with_lease_is_rejected(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        assert finalize_published_plan(q, mc, plan, ast)
        qc.execute('UPDATE chunk_tasks SET lease_owner=?', ('zombie',))
        qc.commit()
        with pytest.raises(ValueError, match='COMPLETED_LEASE_DRIFT'):
            finalize_published_plan(q, mc, plan, ast)


@pytest.mark.parametrize('bad_version', [0, True, -1, 1.2])
def test_invalid_version_cannot_finalize(tmp_path, bad_version):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        with pytest.raises(ValueError, match='INVALID_VERSION'):
            finalize_published_plan(q, mc, plan, ast, projection_version=bad_version)


def test_scheduler_does_not_treat_all_result_staged_as_finished(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        with patch('infra.db.control_repo.ensure_fsm_database_attached', return_value=None):
            qc.execute("ATTACH DATABASE ':memory:' AS fsm_db")
            qc.execute('CREATE TABLE fsm_db.document_fsm '
                       '(document_id TEXT, ast_hash TEXT, current_state TEXT, updated_at REAL)')
            qc.execute('INSERT INTO fsm_db.document_fsm VALUES (?,?,?,?)',
                       (plan.document_id, plan.ast_hash, 'PROCESSING', 1.0))
            qc.commit()
            assert q.find_documents_with_pending_chunks() == []
            assert finalize_published_plan(q, mc, plan, ast)
            assert q.find_documents_with_pending_chunks() == [(plan.document_id, plan.ast_hash)]


def test_completed_replay_rejects_tampered_receipts(tmp_path):
    ast, plan, qc, mc, q = _setup(tmp_path)
    with closing(qc), closing(mc):
        assert finalize_published_plan(q, mc, plan, ast)
        qc.execute('UPDATE chunk_result_receipts SET response_sha256=?', ('0'*64,))
        qc.commit()
        with pytest.raises(ValueError, match='RECEIPT_CHECKSUM_MISMATCH'):
            finalize_published_plan(q, mc, plan, ast)
