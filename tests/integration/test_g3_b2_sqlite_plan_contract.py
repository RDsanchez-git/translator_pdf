"""G3-B2: pruebas reales SQLite. Sin PDF, proveedor, daemon ni DB productiva."""
from contextlib import closing
from dataclasses import replace
from pathlib import Path
import sqlite3

import pytest

from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, ParagraphPayload, HeadingPayload
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from core.chunking.manifest_contract import ChunkPlan
from infra.db.control_repo import ControlPlaneRepository


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)


def _ast(two_chunks: bool = False):
    if two_chunks:
        return [
            ASTNode(node_id="node_heading", sequence_id=1, node_type=ContentNodeType.HEADING,
                    payload=HeadingPayload(content="1. Heading")),
            ASTNode(node_id="node_text", sequence_id=2, node_type=ContentNodeType.PARAGRAPH,
                    payload=ParagraphPayload(content="Alpha beta gamma.")),
        ]
    return [
        ASTNode(node_id="node_a", sequence_id=1, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Alpha.")),
        ASTNode(node_id="node_b", sequence_id=2, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content=" Beta.")),
    ]


def _plan(ast, doc="doc_g3_b2", generation="ast_g3_b2"):
    units, _ = build_semantic_chunks_as_units(ast, _Estimator())
    return ChunkPlan.build(doc, generation, ast, units)


def _db(path):
    conn = sqlite3.connect(path)
    schema = (Path(__file__).resolve().parents[2] / "infra/db/schema_queue.sql").read_text(encoding="utf-8")
    conn.executescript(schema)
    return conn


def test_persisted_manifest_and_tasks_survive_reopening(tmp_path):
    path = tmp_path / "queue.db"
    ast = _ast()
    plan = _plan(ast)
    assert len(plan.units) == 1
    with closing(_db(path)) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, ast)
        assert repo.load_chunk_plan(plan.document_id, plan.ast_hash, ast) == plan
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 1
    with closing(sqlite3.connect(path)) as conn:
        loaded = ControlPlaneRepository(conn).load_chunk_plan(plan.document_id, plan.ast_hash, ast)
        assert loaded == plan


def test_retry_is_idempotent_and_does_not_reset_task_state(tmp_path):
    ast = _ast()
    plan = _plan(ast)
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, ast)
        conn.execute("UPDATE chunk_tasks SET task_state='DONE' WHERE document_id=?", (plan.document_id,))
        conn.commit()
        repo.enqueue_chunk_plan(plan, ast)
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 1
        assert conn.execute("SELECT task_state FROM chunk_tasks").fetchone()[0] == "DONE"


def test_conflicting_plan_for_same_generation_is_rejected_without_mutation(tmp_path):
    ast = _ast()
    plan = _plan(ast)
    mutated = replace(plan.units[0], chunk_id="g3_other_valid_chunk_id")
    changed = ChunkPlan.build(plan.document_id, plan.ast_hash, ast, [mutated])
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, ast)
        with pytest.raises(ValueError, match="G3_B2_GENERATION_PLAN_CONFLICT"):
            repo.enqueue_chunk_plan(changed, ast)
        assert repo.load_chunk_plan(plan.document_id, plan.ast_hash, ast) == plan


def test_legacy_tasks_without_manifest_are_not_adopted(tmp_path):
    ast = _ast()
    plan = _plan(ast)
    with closing(_db(tmp_path / "queue.db")) as conn:
        conn.execute("INSERT INTO chunk_tasks (task_id,document_id,ast_hash,node_id,task_state,created_at,updated_at) "
                     "VALUES ('old','doc_g3_b2','ast_g3_b2','old_node','PENDING',1,1)")
        conn.commit()
        repo = ControlPlaneRepository(conn)
        with pytest.raises(ValueError, match="G3_B2_LEGACY_TASKS_WITHOUT_PLAN"):
            repo.enqueue_chunk_plan(plan, ast)
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 1


def test_injected_sqlite_failure_rolls_back_plan_and_all_tasks(tmp_path):
    ast = _ast(two_chunks=True)
    plan = _plan(ast)
    assert len(plan.units) == 2
    with closing(_db(tmp_path / "queue.db")) as conn:
        # Failure en la segunda tarea, después de insertar el manifiesto y la primera tarea.
        second = plan.units[1].chunk_id.replace("'", "''")
        conn.execute(f"""CREATE TRIGGER reject_second BEFORE INSERT ON chunk_tasks
            WHEN NEW.node_id = '{second}'
            BEGIN SELECT RAISE(ABORT, 'synthetic crash'); END""")
        conn.commit()
        with pytest.raises(sqlite3.IntegrityError, match="synthetic crash"):
            ControlPlaneRepository(conn).enqueue_chunk_plan(plan, ast)
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0


def test_savepoint_does_not_commit_caller_transaction(tmp_path):
    path = tmp_path / "queue.db"
    ast = _ast()
    plan = _plan(ast)
    with closing(_db(path)) as conn:
        conn.execute("BEGIN")
        ControlPlaneRepository(conn).enqueue_chunk_plan(plan, ast)
        assert conn.in_transaction
        conn.rollback()
    with closing(sqlite3.connect(path)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0


def test_tampered_manifest_is_rejected_when_loading(tmp_path):
    ast = _ast()
    plan = _plan(ast)
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, ast)
        conn.execute("UPDATE chunk_plans SET manifest_json='{}'")
        conn.commit()
        with pytest.raises(ValueError, match="G3_INVALID_MANIFEST_ENVELOPE"):
            repo.load_chunk_plan(plan.document_id, plan.ast_hash, ast)


def test_missing_queue_task_blocks_loading_and_idempotent_retry(tmp_path):
    ast = _ast()
    plan = _plan(ast)
    with closing(_db(tmp_path / "queue.db")) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_chunk_plan(plan, ast)
        conn.execute("DELETE FROM chunk_tasks WHERE document_id=?", (plan.document_id,))
        conn.commit()
        with pytest.raises(ValueError, match="G3_B2_QUEUE_MANIFEST_DRIFT"):
            repo.load_chunk_plan(plan.document_id, plan.ast_hash, ast)
        with pytest.raises(ValueError, match="G3_B2_QUEUE_MANIFEST_DRIFT"):
            repo.enqueue_chunk_plan(plan, ast)
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0


def test_existing_queue_schema_migrates_with_no_task_data_loss(tmp_path):
    """Compatibilidad de B2 con queue.db creada antes de introducir chunk_plans."""
    ast = _ast()
    plan = _plan(ast)
    with closing(_db(tmp_path / "queue.db")) as conn:
        conn.execute("DROP TABLE chunk_plans")
        conn.commit()
        ControlPlaneRepository(conn).enqueue_chunk_plan(plan, ast)
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 1


def test_ast_generation_mismatch_fails_before_database_write(tmp_path):
    ast = _ast()
    plan = _plan(ast)
    different_ast = _ast(two_chunks=True)
    with closing(_db(tmp_path / "queue.db")) as conn:
        with pytest.raises(ValueError):
            ControlPlaneRepository(conn).enqueue_chunk_plan(plan, different_ast)
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0


def test_nested_savepoint_failure_does_not_rollback_caller_changes(tmp_path):
    ast = _ast(two_chunks=True)
    plan = _plan(ast)
    with closing(_db(tmp_path / "queue.db")) as conn:
        conn.execute("CREATE TABLE external_owner(marker TEXT)")
        conn.commit()
        second = plan.units[1].chunk_id.replace("'", "''")
        conn.execute(f"""CREATE TRIGGER reject_second_in_nested BEFORE INSERT ON chunk_tasks
            WHEN NEW.node_id = '{second}'
            BEGIN SELECT RAISE(ABORT, 'nested abort'); END""")
        conn.commit()
        conn.execute("BEGIN")
        conn.execute("INSERT INTO external_owner(marker) VALUES ('owner-kept')")
        with pytest.raises(sqlite3.IntegrityError, match="nested abort"):
            ControlPlaneRepository(conn).enqueue_chunk_plan(plan, ast)
        assert conn.in_transaction
        conn.commit()
        assert conn.execute("SELECT marker FROM external_owner").fetchone()[0] == "owner-kept"
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0
