"""C3/T05: G3 publication resumes across a real process crash, no provider.

One disposable local directory; no Docker, HTTP, PDF or persistent lab state.
The first child exits abruptly AFTER committing materialized projections but
BEFORE queue finalization/FSM transition. The second child reopens SQLite.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CRASH_EXIT = 73


def _plan():
    from core.ast.enums import ContentNodeType, TranslationStrategy
    from core.ast.models import ASTNode, MathPayload, ParagraphPayload
    from core.chunking.contextual_plan import prepare_contextual_plan

    class Estimator:
        def estimate_tokens(self, text):
            return len(text.split())

    nodes = [
        ASTNode(
            node_id="eq", sequence_id=1,
            node_type=ContentNodeType.DISPLAY_EQUATION,
            strategy=TranslationStrategy.PASSTHROUGH,
            payload=MathPayload(content="E=mc^2"),
        ),
        ASTNode(
            node_id="a", sequence_id=2,
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Alpha."),
        ),
        ASTNode(
            node_id="b", sequence_id=3,
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content=" Beta."),
        ),
    ]
    prepared = prepare_contextual_plan(
        document_id="c3_t05_process_boundary", raw_ast=nodes,
        estimator=Estimator(),
    )
    return list(prepared.ast), prepared.plan


def _connections(folder):
    return (
        sqlite3.connect(folder / "queue.db", timeout=10),
        sqlite3.connect(folder / "materialized.db", timeout=10),
        sqlite3.connect(folder / "fsm.db", timeout=10),
    )


def _stage_and_crash(folder):
    from core.ast.models import TranslationTaskType
    from infra.db.context_snapshot_repo import DurableContextPlanRepository
    from infra.db.control_repo import ControlPlaneRepository
    from infra.db.staged_publication import publish_staged_plan

    ast, plan = _plan()
    q, m, f = _connections(folder)
    q.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    m.executescript((ROOT / "infra/db/schema_materialized.sql").read_text(encoding="utf-8"))
    f.executescript("""
        CREATE TABLE document_fsm (
            document_id TEXT NOT NULL,
            ast_hash TEXT NOT NULL,
            current_state TEXT NOT NULL,
            state_version INTEGER NOT NULL,
            is_terminal INTEGER NOT NULL DEFAULT 0,
            entered_state_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            failure_reason TEXT,
            suspended_state TEXT,
            PRIMARY KEY(document_id,ast_hash)
        );
    """)
    f.execute(
        "INSERT INTO document_fsm "
        "(document_id,ast_hash,current_state,state_version,entered_state_at,updated_at) "
        "VALUES (?,?,'PROCESSING',1,1,1)",
        (plan.document_id, plan.ast_hash),
    )
    f.commit()
    repo = ControlPlaneRepository(q)
    DurableContextPlanRepository(repo).enqueue_verified(plan, ast)

    assert len(plan.units) == 2
    assert {unit.chunk_type.value for unit in plan.units} == {"preserve", "translate"}
    for _ in plan.units:
        lease = repo.pick_task("c3_stage", plan.document_id, plan.ast_hash)
        assert lease is not None
        unit = next(unit for unit in plan.units if unit.chunk_id == lease.node_id)
        response = None
        if unit.chunk_type != TranslationTaskType.PRESERVE:
            response = json.dumps({
                "schema_version": 1,
                "document_id": plan.document_id,
                "ast_hash": plan.ast_hash,
                "manifest_sha256": plan.digest,
                "chunk_id": unit.chunk_id,
                "members": [{
                    "node_id": member.node_id,
                    "segment_index": member.segment_index,
                    "source_sha256": hashlib.sha256(
                        member.source_text.encode("utf-8")
                    ).hexdigest(),
                    "translated_text": f"Traduccion-{index}",
                } for index, member in enumerate(unit.members)],
            }, ensure_ascii=False)
        repo.stage_chunk_result(
            plan, ast, chunk_id=unit.chunk_id, task_id=lease.task_id,
            worker_id="c3_stage", execution_id=lease.execution_id,
            raw_response=response,
        )

    assert publish_staged_plan(repo, m, plan, ast)
    assert q.execute(
        "SELECT COUNT(*) FROM chunk_tasks WHERE task_state='RESULT_STAGED'"
    ).fetchone()[0] == 2
    assert f.execute("SELECT current_state FROM document_fsm").fetchone()[0] == "PROCESSING"
    assert m.execute("SELECT COUNT(*) FROM g3_plan_publications").fetchone()[0] == 1

    print("C3_T05_PUBLISHED_BEFORE_CRASH_PASS", flush=True)
    # Deliberately bypass close/finalize: simulate abrupt process termination.
    os._exit(CRASH_EXIT)


def _recover_in_new_process(folder):
    from infra.db.control_repo import ControlPlaneRepository
    from infra.db.fsm_repository import FSMRepository
    from runtime.publication_pipeline import advance_staged_document

    ast, plan = _plan()
    q, m, f = _connections(folder)
    try:
        repo = ControlPlaneRepository(q)
        assert q.execute(
            "SELECT COUNT(*) FROM chunk_result_receipts"
        ).fetchone()[0] == 2
        assert f.execute("SELECT current_state FROM document_fsm").fetchone()[0] == "PROCESSING"
        before = m.execute(
            "SELECT node_id,normalized_hash,last_updated "
            "FROM valid_chunks_cache ORDER BY node_id"
        ).fetchall()
        assert len(before) == len(ast)
        assert advance_staged_document(
            repo, m, FSMRepository(f), plan, ast, "c3_recovered",
        )
        assert q.execute(
            "SELECT COUNT(*) FROM chunk_tasks "
            "WHERE worker_type='LLM' AND task_state='COMPLETED'"
        ).fetchone()[0] == 2
        assert f.execute("SELECT current_state FROM document_fsm").fetchone()[0] == "READY_FOR_ASSEMBLY"
        assert m.execute("SELECT COUNT(*) FROM g3_plan_publications").fetchone()[0] == 1
        assert m.execute(
            "SELECT node_id,normalized_hash,last_updated "
            "FROM valid_chunks_cache ORDER BY node_id"
        ).fetchall() == before
        print("C3_T05_INDEPENDENT_RECOVERY_NO_PROVIDER_PASS", flush=True)
    finally:
        q.close()
        m.close()
        f.close()


def test_t05_g3_staged_publication_crash_and_recovery_between_processes():
    """Only the durable recovery boundary is new; W06/fencing already tested."""
    with tempfile.TemporaryDirectory(prefix="tpdf_c3_t05_") as temp:
        folder = Path(temp)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        def run(phase):
            return subprocess.run(
                [sys.executable, "-B", str(Path(__file__).resolve()), phase, str(folder)],
                cwd=ROOT, env=env, text=True, capture_output=True, timeout=30,
                check=False,
            )

        first = run("crash")
        assert first.returncode == CRASH_EXIT, (first.stdout, first.stderr)
        assert "C3_T05_PUBLISHED_BEFORE_CRASH_PASS" in first.stdout

        second = run("recover")
        assert second.returncode == 0, (second.stdout, second.stderr)
        assert "C3_T05_INDEPENDENT_RECOVERY_NO_PROVIDER_PASS" in second.stdout

        # Parent is a third independent SQLite reader.
        with sqlite3.connect((folder / "fsm.db").as_uri() + "?mode=ro", uri=True) as conn:
            assert conn.execute(
                "SELECT current_state FROM document_fsm"
            ).fetchone() == ("READY_FOR_ASSEMBLY",)
        with sqlite3.connect((folder / "queue.db").as_uri() + "?mode=ro", uri=True) as conn:
            assert conn.execute(
                "SELECT COUNT(*) FROM chunk_result_receipts"
            ).fetchone()[0] == 2
        assert not list(folder.glob("*.pdf"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("test-only process: crash|recover, temporary directory")
    directory = Path(sys.argv[2]).resolve(strict=True)
    if not directory.is_dir() or "tpdf_c3_t05_" not in directory.name:
        raise SystemExit("C3_T05_INVALID_TEMP_DIR")
    if sys.argv[1] == "crash":
        _stage_and_crash(directory)
    elif sys.argv[1] == "recover":
        _recover_in_new_process(directory)
    else:
        raise SystemExit("C3_T05_INVALID_PHASE")
