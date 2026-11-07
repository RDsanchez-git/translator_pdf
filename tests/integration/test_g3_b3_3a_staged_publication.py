"""G3-B3/3a: staged queue -> atomic materialized projections, no external provider.

Every SQLite database is located under pytest's disposable tmp_path.  No daemon,
production DB, network, PDF renderer or external LLM is invoked.
"""
from contextlib import closing
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload, MathPayload
from core.ast.grouper import SemanticGroup
from core.chunking.semantic_chunking import TokenBudgetChunker, ChunkPolicy
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.result_contract import materialize_node_results
from infra.db.control_repo import ControlPlaneRepository
from infra.db.staged_publication import publish_staged_plan, verify_published_nodes


class Estimator:
    def estimate_tokens(self, text):
        return len(text.split())


def _node(node_id, sequence, text, *, preserve=False):
    return ASTNode(
        node_id=node_id, sequence_id=sequence,
        node_type=ContentNodeType.DISPLAY_EQUATION if preserve else ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.PASSTHROUGH if preserve else TranslationStrategy.TRANSLATE,
        payload=MathPayload(content=text) if preserve else ParagraphPayload(content=text),
    )


def _plan(*, preserve=False):
    ast = ([_node('math', 1, 'E=mc²', preserve=True), _node('text', 2, 'Alpha beta.')]
           if preserve else [_node('one', 1, 'Alpha.'), _node('two', 2, ' Beta.')])
    units = TokenBudgetChunker(
        Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0)
    ).chunk_group(SemanticGroup(structural_path=(), context_id='ctx', nodes=ast), 1)
    plan = ChunkPlan.build('doc_staging', 'ast_staging', ast, units)
    return ast, plan


def _conn(path, schema):
    conn = sqlite3.connect(path)
    sql = (Path(__file__).resolve().parents[2] / 'infra/db' / schema).read_text(encoding='utf-8')
    conn.executescript(sql)
    return conn


def _response(plan, unit, *, translation='Traducido'):
    return json.dumps({
        'schema_version': 1, 'document_id': plan.document_id, 'ast_hash': plan.ast_hash,
        'manifest_sha256': plan.digest, 'chunk_id': unit.chunk_id,
        'members': [
            {'node_id': m.node_id, 'segment_index': m.segment_index,
             'source_sha256': sha256(m.source_text.encode('utf-8')).hexdigest(),
             'translated_text': f'{translation}{index}'}
            for index, m in enumerate(unit.members)
        ],
    }, ensure_ascii=False)


def _stage_all(queue, plan, ast):
    queue.enqueue_chunk_plan(plan, ast)
    for _ in plan.units:
        lease = queue.pick_task('worker_test', plan.document_id, plan.ast_hash)
        assert lease is not None
        unit = next(u for u in plan.units if u.chunk_id == lease.node_id)
        raw = None if unit.chunk_type.value == 'preserve' else _response(plan, unit)
        assert queue.stage_chunk_result(
            plan, ast, chunk_id=unit.chunk_id, task_id=lease.task_id,
            worker_id='worker_test', execution_id=lease.execution_id, raw_response=raw,
        ) is True


def _context(tmp_path, *, preserve=False):
    ast, plan = _plan(preserve=preserve)
    qconn = _conn(tmp_path / 'queue.db', 'schema_queue.sql')
    mconn = _conn(tmp_path / 'materialized.db', 'schema_materialized.sql')
    queue = ControlPlaneRepository(qconn)
    _stage_all(queue, plan, ast)
    return ast, plan, qconn, mconn, queue


def test_publishes_complete_two_node_chunk_and_attests_source(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        assert publish_staged_plan(queue, mc, plan, ast)
        projections = mc.execute('SELECT node_id, content_hash, normalized_response, normalized_hash '
                                 'FROM valid_chunks_cache ORDER BY node_id').fetchall()
        assert len(projections) == 2
        assert projections[0][0] == 'one' and projections[1][0] == 'two'
        assert projections[0][1] == sha256('Alpha.'.encode()).hexdigest()
        assert projections[1][1] == sha256(' Beta.'.encode()).hexdigest()
        assert projections[0][3] == sha256(projections[0][2].encode()).hexdigest()
        assert mc.execute('SELECT COUNT(*) FROM g3_plan_publications').fetchone()[0] == 1
        assert set(qc.execute('SELECT task_state FROM chunk_tasks').fetchall()) == {('RESULT_STAGED',)}


def test_reopen_uses_durable_queue_receipt_for_idempotent_publication(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        assert publish_staged_plan(queue, mc, plan, ast) is True
        first_updated = mc.execute('SELECT last_updated FROM valid_chunks_cache LIMIT 1').fetchone()[0]
    with closing(sqlite3.connect(tmp_path / 'queue.db')) as qc2, closing(sqlite3.connect(tmp_path / 'materialized.db')) as mc2:
        assert publish_staged_plan(ControlPlaneRepository(qc2), mc2, plan, ast) is False
        assert mc2.execute('SELECT last_updated FROM valid_chunks_cache LIMIT 1').fetchone()[0] == first_updated
        outputs = materialize_node_results(plan, ControlPlaneRepository(qc2).load_staged_chunk_responses(plan, ast))
        verify_published_nodes(mc2, plan, ast, outputs)


def test_preserve_node_does_not_require_provider_response(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path, preserve=True)
    with closing(qc), closing(mc):
        assert publish_staged_plan(queue, mc, plan, ast)
        assert mc.execute("SELECT normalized_response FROM valid_chunks_cache WHERE node_id='math'").fetchone()[0] == 'E=mc²'
        assert len(queue.load_staged_chunk_responses(plan, ast)) == 1


def test_incomplete_receipts_cannot_publish(tmp_path):
    ast, plan = _plan(preserve=True)
    with closing(_conn(tmp_path / 'queue.db', 'schema_queue.sql')) as qc, closing(_conn(tmp_path / 'materialized.db', 'schema_materialized.sql')) as mc:
        queue = ControlPlaneRepository(qc)
        queue.enqueue_chunk_plan(plan, ast)
        lease = queue.pick_task('w', plan.document_id, plan.ast_hash)
        assert lease is not None
        unit = next(u for u in plan.units if u.chunk_id == lease.node_id)
        queue.stage_chunk_result(plan, ast, chunk_id=unit.chunk_id, task_id=lease.task_id,
                                 worker_id='w', execution_id=lease.execution_id,
                                 raw_response=None if unit.chunk_type.value == 'preserve' else _response(plan, unit))
        with pytest.raises(ValueError, match='INCOMPLETE_STAGED_PLAN'):
            publish_staged_plan(queue, mc, plan, ast)
        assert mc.execute('SELECT COUNT(*) FROM valid_chunks_cache').fetchone()[0] == 0


def test_corrupted_receipt_rejects_before_publishing(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        qc.execute("UPDATE chunk_result_receipts SET response_sha256=?", ('0' * 64,))
        qc.commit()
        with pytest.raises(ValueError, match='RECEIPT_CHECKSUM_MISMATCH'):
            publish_staged_plan(queue, mc, plan, ast)
        assert mc.execute('SELECT COUNT(*) FROM valid_chunks_cache').fetchone()[0] == 0


def test_failure_on_publication_insert_rolls_back_all_nodes(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        mc.executescript('CREATE TRIGGER fail_g3 BEFORE INSERT ON g3_plan_publications '
                         "BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END;")
        with pytest.raises(sqlite3.IntegrityError, match='synthetic failure'):
            publish_staged_plan(queue, mc, plan, ast)
        assert mc.execute('SELECT COUNT(*) FROM valid_chunks_cache').fetchone()[0] == 0
        assert mc.execute('SELECT COUNT(*) FROM g3_plan_publications').fetchone()[0] == 0
        assert set(qc.execute('SELECT task_state FROM chunk_tasks').fetchall()) == {('RESULT_STAGED',)}


def test_legacy_projection_without_publication_is_not_overwritten(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        mc.execute('INSERT INTO valid_chunks_cache VALUES (?,?,?,?,?,?,?,?)',
                   (plan.document_id, plan.ast_hash, 'one', 'a'*64, 'legacy', 'b'*64, 1, 1.0))
        mc.commit()
        with pytest.raises(ValueError, match='UNOWNED_PROJECTIONS'):
            publish_staged_plan(queue, mc, plan, ast)
        assert mc.execute('SELECT normalized_response FROM valid_chunks_cache').fetchone()[0] == 'legacy'


def test_corrupt_projection_rejected_on_replay(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        assert publish_staged_plan(queue, mc, plan, ast)
        mc.execute('UPDATE valid_chunks_cache SET normalized_response=? WHERE node_id=?', ('corrupt', 'one'))
        mc.commit()
        with pytest.raises(ValueError, match='PROJECTION_DRIFT'):
            publish_staged_plan(queue, mc, plan, ast)


def test_tampered_publication_sha_rejected_on_replay(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        publish_staged_plan(queue, mc, plan, ast)
        mc.execute('UPDATE g3_plan_publications SET result_sha256=?', ('0'*64,))
        mc.commit()
        with pytest.raises(ValueError, match='PUBLICATION_CONFLICT_OR_MISSING'):
            publish_staged_plan(queue, mc, plan, ast)


def test_source_hash_and_node_coverage_fenced(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        assert publish_staged_plan(queue, mc, plan, ast)
        out = materialize_node_results(plan, queue.load_staged_chunk_responses(plan, ast))
        wrong_hash = (replace(out[0], text_sha256='0'*64), *out[1:])
        with pytest.raises(ValueError, match='NODE_HASH_MISMATCH'):
            verify_published_nodes(mc, plan, ast, wrong_hash)
        with pytest.raises(ValueError, match='NODE_COVERAGE_OR_ORDER'):
            verify_published_nodes(mc, plan, ast, tuple(reversed(out)))


def test_nested_transaction_ownership_and_rollback(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        mc.execute('BEGIN')
        assert publish_staged_plan(queue, mc, plan, ast)
        assert mc.in_transaction
        mc.rollback()
    with closing(sqlite3.connect(tmp_path / 'materialized.db')) as reopen:
        assert reopen.execute('SELECT COUNT(*) FROM valid_chunks_cache').fetchone()[0] == 0
        assert reopen.execute('SELECT COUNT(*) FROM g3_plan_publications').fetchone()[0] == 0


def test_idempotent_retry_does_not_commit_parent_transaction(tmp_path):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        assert publish_staged_plan(queue, mc, plan, ast)
        mc.execute('BEGIN')
        assert publish_staged_plan(queue, mc, plan, ast) is False
        assert mc.in_transaction
        mc.rollback()
        assert mc.execute('SELECT COUNT(*) FROM g3_plan_publications').fetchone()[0] == 1


@pytest.mark.parametrize('version', [0, -1, True, 1.2])
def test_rejects_invalid_projection_version(tmp_path, version):
    ast, plan, qc, mc, queue = _context(tmp_path)
    with closing(qc), closing(mc):
        with pytest.raises(ValueError, match='INVALID_VERSION'):
            publish_staged_plan(queue, mc, plan, ast, projection_version=version)
        assert mc.execute('SELECT COUNT(*) FROM valid_chunks_cache').fetchone()[0] == 0
