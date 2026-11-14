"""G3-B4/1: coexistencia LLM/ASSEMBLER en queue.db sin falsos completados.

Todos los estados y ficheros SQLite son efimeros. No arranca daemons ni PDF/LLM.
"""
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

import pytest

from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, ParagraphPayload
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from infra.db.control_repo import ControlPlaneRepository
from infra.db.staged_publication import publish_staged_plan, finalize_published_plan


ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)


def _conn(path: Path, schema_name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript((ROOT / "infra" / "db" / schema_name).read_text(encoding="utf-8"))
    return conn


def _context(tmp_path):
    ast = [
        ASTNode(node_id="n_one", sequence_id=1, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Alpha.")),
        ASTNode(node_id="n_two", sequence_id=2, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content=" Beta.")),
    ]
    units, _ = build_semantic_chunks_as_units(ast, _Estimator())
    plan = ChunkPlan.build("g3_b4_coexist", "g3_b4_hash", ast, units)
    assert len(plan.units) == 1 and len(plan.units[0].members) == 2
    queue = _conn(tmp_path / "queue.db", "schema_queue.sql")
    materialized = _conn(tmp_path / "materialized.db", "schema_materialized.sql")
    repo = ControlPlaneRepository(queue)
    repo.enqueue_chunk_plan(plan, ast)
    return ast, plan, queue, materialized, repo


def _response(plan, unit):
    return json.dumps({
        "schema_version": 1,
        "document_id": plan.document_id,
        "ast_hash": plan.ast_hash,
        "manifest_sha256": plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [
            {
                "node_id": m.node_id,
                "segment_index": m.segment_index,
                "source_sha256": sha256(m.source_text.encode("utf-8")).hexdigest(),
                "translated_text": "Traducción " + str(i),
            }
            for i, m in enumerate(unit.members)
        ],
    }, ensure_ascii=False)


def _stage_publish_finalize(repo, materialized, plan, ast):
    lease = repo.pick_task("worker_llm", plan.document_id, plan.ast_hash)
    assert lease is not None and lease.node_id == plan.units[0].chunk_id
    assert repo.stage_chunk_result(
        plan, ast, chunk_id=lease.node_id, task_id=lease.task_id,
        worker_id="worker_llm", execution_id=lease.execution_id,
        raw_response=_response(plan, plan.units[0]),
    ) is True
    assert publish_staged_plan(repo, materialized, plan, ast) is True
    assert finalize_published_plan(repo, materialized, plan, ast) is True


def _assembler(repo, plan):
    assert repo.enqueue_assembler_task("assembly_trigger_g3_b4", plan.document_id, plan.ast_hash)


def test_read_manifest_and_idempotent_enqueue_after_assembler_trigger(tmp_path):
    ast, plan, qc, mc, repo = _context(tmp_path)
    with closing(qc), closing(mc):
        _assembler(repo, plan)
        assert repo.load_chunk_plan(plan.document_id, plan.ast_hash, ast) == plan
        repo.enqueue_chunk_plan(plan, ast)  # reingesta nunca reemplaza el trigger
        assert qc.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 2
        assert qc.execute("SELECT worker_type, task_state FROM chunk_tasks "
                          "WHERE node_id='ROOT_ASSEMBLY'").fetchone() == ("ASSEMBLER", "PENDING")


def test_engine_pickup_never_claims_assembler_trigger(tmp_path):
    ast, plan, qc, mc, repo = _context(tmp_path)
    with closing(qc), closing(mc):
        _assembler(repo, plan)
        lease = repo.pick_task("llm", plan.document_id, plan.ast_hash)
        assert lease is not None and lease.node_id == plan.units[0].chunk_id
        assert repo.pick_task("llm", plan.document_id, plan.ast_hash) is None
        assert qc.execute("SELECT task_state, lease_owner FROM chunk_tasks "
                          "WHERE node_id='ROOT_ASSEMBLY'").fetchone() == ("PENDING", None)


def test_finalize_ignores_assembler_trigger_but_never_completes_it(tmp_path):
    ast, plan, qc, mc, repo = _context(tmp_path)
    with closing(qc), closing(mc):
        _assembler(repo, plan)
        _stage_publish_finalize(repo, mc, plan, ast)
        assert qc.execute("SELECT task_state FROM chunk_tasks WHERE worker_type='LLM'").fetchone() == ("COMPLETED",)
        assert qc.execute("SELECT task_state FROM chunk_tasks WHERE worker_type='ASSEMBLER'").fetchone() == ("PENDING",)
        assert finalize_published_plan(repo, mc, plan, ast) is False
        assert repo.load_chunk_plan(plan.document_id, plan.ast_hash, ast) == plan


def test_replay_after_both_dbs_reopen_with_assembler_task(tmp_path):
    ast, plan, qc, mc, repo = _context(tmp_path)
    with closing(qc), closing(mc):
        _stage_publish_finalize(repo, mc, plan, ast)
        _assembler(repo, plan)
    with closing(sqlite3.connect(tmp_path / "queue.db")) as q2, \
         closing(sqlite3.connect(tmp_path / "materialized.db")) as m2:
        repo2 = ControlPlaneRepository(q2)
        assert repo2.load_chunk_plan(plan.document_id, plan.ast_hash, ast) == plan
        assert finalize_published_plan(repo2, m2, plan, ast) is False
        assert q2.execute("SELECT task_state FROM chunk_tasks WHERE worker_type='ASSEMBLER'").fetchone() == ("PENDING",)


def test_unexpected_foreign_worker_does_not_hide_as_assembler(tmp_path):
    ast, plan, qc, mc, repo = _context(tmp_path)
    with closing(qc), closing(mc):
        qc.execute("INSERT INTO chunk_tasks "
                   "(task_id,document_id,ast_hash,node_id,worker_type,created_at,updated_at) "
                   "VALUES (?,?,?,?,?,1,1)",
                   ("task_foreign", plan.document_id, plan.ast_hash, "foreign", "UNEXPECTED"))
        qc.commit()
        with pytest.raises(ValueError, match="G3_B2_QUEUE_MANIFEST_DRIFT"):
            repo.load_chunk_plan(plan.document_id, plan.ast_hash, ast)


def test_scheduler_considers_only_llm_tasks_even_if_assembler_pending(tmp_path, monkeypatch):
    ast, plan, qc, mc, repo = _context(tmp_path)
    with closing(qc), closing(mc):
        _stage_publish_finalize(repo, mc, plan, ast)
        _assembler(repo, plan)
        fsm_path = tmp_path / "fsm.db"
        with closing(sqlite3.connect(fsm_path)) as fsm:
            fsm.execute("CREATE TABLE document_fsm (document_id TEXT, ast_hash TEXT, "
                        "current_state TEXT, updated_at REAL)")
            fsm.execute("INSERT INTO document_fsm VALUES (?,?,?,1)",
                        (plan.document_id, plan.ast_hash, "PROCESSING"))
            fsm.commit()
        monkeypatch.setenv("FSM_DB_PATH", str(fsm_path))
        assert (plan.document_id, plan.ast_hash) in repo.find_documents_with_pending_chunks(10)
