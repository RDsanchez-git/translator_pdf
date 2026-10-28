"""G3-B4/8: Engine must stage PRESERVE without constructing a paid provider.

Real disposable queue/FSM/materialized SQLite; no Docker, network, OCR or Groq.
"""
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, MathPayload, ParagraphPayload, TranslationTaskType
from core.ast.grouper import SemanticGroup
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from infra.db.control_repo import ControlPlaneRepository

ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text):
        return len(text.split())


def _plan(mixed):
    ast = []
    if mixed:
        ast.append(ASTNode(node_id="body", sequence_id=1,
                           node_type=ContentNodeType.PARAGRAPH,
                           payload=ParagraphPayload(content="Translate this.")))
    ast.append(ASTNode(node_id="equation", sequence_id=2 if mixed else 1,
                       node_type=ContentNodeType.DISPLAY_EQUATION,
                       strategy=TranslationStrategy.PASSTHROUGH,
                       payload=MathPayload(content="E=mc^2")))
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0),
    ).chunk_group(SemanticGroup(structural_path=(), context_id="ctx", nodes=ast), 1)
    plan = ChunkPlan.build("doc_preserve_mixed" if mixed else "doc_preserve_only",
                           "ast_g3_b48", ast, units)
    assert len(plan.units) == (2 if mixed else 1)
    assert plan.units[-1].chunk_type == TranslationTaskType.PRESERVE
    return ast, plan


def _translation(plan, unit):
    return json.dumps({
        "schema_version": 1,
        "document_id": plan.document_id,
        "ast_hash": plan.ast_hash,
        "manifest_sha256": plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [{
            "node_id": member.node_id,
            "segment_index": member.segment_index,
            "source_sha256": sha256(member.source_text.encode("utf-8")).hexdigest(),
            "translated_text": "Texto traducido.",
        } for member in unit.members],
    }, ensure_ascii=False)


def _dbs(tmp_path, plan, ast):
    queue = sqlite3.connect(tmp_path / "queue.db")
    fsm = sqlite3.connect(tmp_path / "fsm.db")
    materialized = sqlite3.connect(tmp_path / "materialized.db")
    queue.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    materialized.executescript((ROOT / "infra/db/schema_materialized.sql").read_text(encoding="utf-8"))
    fsm.executescript("""CREATE TABLE document_fsm (
        document_id TEXT NOT NULL, ast_hash TEXT NOT NULL,
        current_state TEXT NOT NULL, state_version INTEGER NOT NULL,
        is_terminal INTEGER NOT NULL DEFAULT 0,
        entered_state_at REAL NOT NULL, updated_at REAL NOT NULL,
        failure_reason TEXT, suspended_state TEXT,
        PRIMARY KEY(document_id, ast_hash)
    );""")
    fsm.execute("INSERT INTO document_fsm "
                "(document_id, ast_hash, current_state, state_version, entered_state_at, updated_at) "
                "VALUES (?, ?, 'PROCESSING', 1, 1.0, 1.0)",
                (plan.document_id, plan.ast_hash))
    fsm.commit()
    repo = ControlPlaneRepository(queue)
    repo.enqueue_chunk_plan(plan, ast)
    return SimpleNamespace(queue=queue, fsm=fsm, materialized=materialized, repo=repo)


@pytest.mark.parametrize("mode", ["preserve_only", "translated_already_staged", "mixed_runnable"])
def test_engine_preserve_provider_decision_and_full_publication(tmp_path, monkeypatch, mode):
    import runtime.engine as engine

    mixed = mode != "preserve_only"
    ast, plan = _plan(mixed)
    dbs = _dbs(tmp_path, plan, ast)
    try:
        if mode == "translated_already_staged":
            lease = dbs.repo.pick_task("setup_worker", plan.document_id, plan.ast_hash)
            assert lease is not None and lease.node_id == plan.units[0].chunk_id
            assert dbs.repo.stage_chunk_result(
                plan, ast, chunk_id=lease.node_id, task_id=lease.task_id,
                worker_id="setup_worker", execution_id=lease.execution_id,
                raw_response=_translation(plan, plan.units[0]),
            )

        monkeypatch.setenv("IS_BENCHMARK", "0")
        monkeypatch.setenv("MAX_CONCURRENT_CHUNKS", "1")
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.setattr(engine, "ASTRegistry", lambda: SimpleNamespace(
            get_document_ast=lambda document_id, ast_hash: ast,
        ))
        monkeypatch.setattr(engine, "compute_ast_hash", lambda _ast: plan.ast_hash)
        monkeypatch.setattr(engine, "get_connection", lambda path, timeout=30:
                            sqlite3.connect(tmp_path / Path(path).name, timeout=timeout))

        calls = []
        shutdowns = []
        def _provider_factory():
            if mode != "mixed_runnable":
                pytest.fail("PRESERVE path initialized an unnecessary provider")
            def execute_chunk(actual_plan, unit):
                calls.append(unit.chunk_id)
                return _translation(actual_plan, unit)
            processor = SimpleNamespace(execute_chunk=execute_chunk,
                                        shutdown=lambda: shutdowns.append("provider"))
            quota = SimpleNamespace(close=lambda: shutdowns.append("quota"))
            return processor, quota

        monkeypatch.setattr(engine, "_create_chunk_processor", _provider_factory)
        result = engine.run_pipeline(plan.document_id, plan.ast_hash)
        assert result == {"status": "ready_for_assembly", "final_state": "READY_FOR_ASSEMBLY"}
        assert dbs.fsm.execute("SELECT current_state FROM document_fsm").fetchone() == ("READY_FOR_ASSEMBLY",)
        assert {r[0] for r in dbs.queue.execute("SELECT task_state FROM chunk_tasks WHERE worker_type='LLM'")} == {"COMPLETED"}
        assert dbs.queue.execute("SELECT COUNT(*) FROM chunk_result_receipts").fetchone()[0] == len(plan.units)
        assert dbs.materialized.execute("SELECT COUNT(*) FROM valid_chunks_cache").fetchone()[0] == len(ast)
        assert dbs.materialized.execute("SELECT normalized_response FROM valid_chunks_cache "
                                        "WHERE node_id='equation'").fetchone() == ("E=mc^2",)
        assert dbs.queue.execute("SELECT raw_response,response_sha256 FROM chunk_result_receipts "
                                 "WHERE chunk_id=?", (plan.units[-1].chunk_id,)).fetchone() == (None, None)
        assert calls == ([plan.units[0].chunk_id] if mode == "mixed_runnable" else [])
        assert shutdowns == (["provider", "quota"] if mode == "mixed_runnable" else [])
    finally:
        dbs.materialized.close()
        dbs.fsm.close()
        dbs.queue.close()
