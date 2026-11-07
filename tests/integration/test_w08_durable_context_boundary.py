"""W08-2b: offline SQLite witnesses for generation-bound context snapshots.

No production SQLite, provider, Docker, real PDF or network.
"""
from contextlib import closing
from dataclasses import replace
from pathlib import Path
import sqlite3

import pytest

from core.ast.enums import ContentNodeType
from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode, ParagraphPayload
from core.ast.grouper import SemanticGroup
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from core.context.plan_context_contract import derive_verified_plan_contexts
from core.normalization.enrichers.context_enricher import HierarchicalContextEnricher
from infra.db.control_repo import ControlPlaneRepository
from infra.db.context_snapshot_repo import DurableContextPlanRepository


ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()))


def _fixture():
    ast = [
        ASTNode(node_id="node_a", sequence_id=1, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Alpha.")),
        ASTNode(node_id="node_b", sequence_id=2, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content=" Beta.")),
    ]
    enriched, registry, _, _ = HierarchicalContextEnricher().enrich_document(ast)
    assert registry["schema_version"] == "1.0.1"
    context_id = enriched[0].control_plane["context_id"]
    assert enriched[1].control_plane["context_id"] == context_id
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0),
    ).chunk_group(
        SemanticGroup(structural_path=("root",), context_id=context_id, nodes=ast),
        1,
    )
    plan = ChunkPlan.build("doc_w08", compute_ast_hash(ast), ast, units)
    return ast, plan, context_id


def _connection(path: Path):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    return conn


def test_w08_snapshot_persists_with_plan_and_survives_new_connection(tmp_path):
    ast, plan, context_id = _fixture()
    path = tmp_path / "queue.db"
    with closing(_connection(path)) as conn:
        repo = DurableContextPlanRepository(ControlPlaneRepository(conn))
        repo.enqueue_verified(plan, ast)
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == len(plan.units)
        assert conn.execute("SELECT COUNT(*) FROM g3_context_snapshots").fetchone()[0] == 1
    with closing(sqlite3.connect(path)) as conn:
        hydrated_plan, snapshots = DurableContextPlanRepository(
            ControlPlaneRepository(conn),
        ).load_verified(plan.document_id, plan.ast_hash, ast)
        assert hydrated_plan == plan
        assert set(snapshots) == {context_id}
        assert snapshots[context_id].breadcrumbs[0].title == "[ROOT_DOCUMENT_CONTEXT]"


def test_w08_context_enrollment_idempotent_and_does_not_reset_task(tmp_path):
    ast, plan, _ = _fixture()
    with closing(_connection(tmp_path / "queue.db")) as conn:
        repo = DurableContextPlanRepository(ControlPlaneRepository(conn))
        repo.enqueue_verified(plan, ast)
        conn.execute("UPDATE chunk_tasks SET task_state='PROCESSING'")
        conn.commit()
        repo.enqueue_verified(plan, ast)
        assert conn.execute("SELECT COUNT(*) FROM g3_context_snapshots").fetchone()[0] == 1
        assert conn.execute("SELECT task_state FROM chunk_tasks").fetchone()[0] == "PROCESSING"


def test_w08_rejects_legacy_manifest_without_snapshots(tmp_path):
    ast, plan, _ = _fixture()
    with closing(_connection(tmp_path / "queue.db")) as conn:
        plain = ControlPlaneRepository(conn)
        plain.enqueue_chunk_plan(plan, ast)
        with pytest.raises(ValueError, match="W08_CONTEXT_LEGACY_PLAN_WITHOUT_SNAPSHOTS"):
            DurableContextPlanRepository(plain).enqueue_verified(plan, ast)
        assert conn.execute("SELECT COUNT(*) FROM g3_context_snapshots").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == len(plan.units)


@pytest.mark.parametrize("field", ["snapshot_json", "snapshot_sha256", "manifest_sha256"])
def test_w08_detects_snapshot_tampering_on_restart(tmp_path, field):
    ast, plan, _ = _fixture()
    path = tmp_path / "queue.db"
    with closing(_connection(path)) as conn:
        repo = DurableContextPlanRepository(ControlPlaneRepository(conn))
        repo.enqueue_verified(plan, ast)
        conn.execute(f"UPDATE g3_context_snapshots SET {field}=?",
                     ("{}",) if field == "snapshot_json" else ("f" * 64,))
        conn.commit()
    with closing(sqlite3.connect(path)) as conn:
        with pytest.raises(ValueError, match="W08_CONTEXT_SNAPSHOT_"):
            DurableContextPlanRepository(ControlPlaneRepository(conn)).load_verified(
                plan.document_id, plan.ast_hash, ast,
            )


def test_w08_missing_snapshot_fails_closed_after_restart(tmp_path):
    ast, plan, _ = _fixture()
    path = tmp_path / "queue.db"
    with closing(_connection(path)) as conn:
        repo = DurableContextPlanRepository(ControlPlaneRepository(conn))
        repo.enqueue_verified(plan, ast)
        conn.execute("DELETE FROM g3_context_snapshots")
        conn.commit()
    with closing(sqlite3.connect(path)) as conn:
        with pytest.raises(ValueError, match="W08_CONTEXT_SNAPSHOT_COVERAGE_MISMATCH"):
            DurableContextPlanRepository(ControlPlaneRepository(conn)).load_verified(
                plan.document_id, plan.ast_hash, ast,
            )


def test_w08_inference_plan_with_global_root_is_rejected_before_writing(tmp_path):
    ast, plan, _ = _fixture()
    mutated_unit = replace(plan.units[0], context_id="GLOBAL_ROOT")
    wrong = ChunkPlan.build(plan.document_id, plan.ast_hash, ast, [mutated_unit])
    with closing(_connection(tmp_path / "queue.db")) as conn:
        repo = DurableContextPlanRepository(ControlPlaneRepository(conn))
        with pytest.raises(ValueError, match="W08_CONTEXT_PLAN_ID_MISMATCH"):
            repo.enqueue_verified(wrong, ast)
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0


def test_w08_plan_context_depth_mismatch_is_rejected(tmp_path):
    ast, plan, _ = _fixture()
    wrong_unit = replace(plan.units[0], context_depth=0)
    wrong = ChunkPlan.build(plan.document_id, plan.ast_hash, ast, [wrong_unit])
    with closing(_connection(tmp_path / "queue.db")) as conn:
        with pytest.raises(ValueError, match="W08_CONTEXT_PLAN_DEPTH_MISMATCH"):
            DurableContextPlanRepository(ControlPlaneRepository(conn)).enqueue_verified(
                wrong, ast,
            )
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0


def test_w08_ast_generation_mismatch_rejected_without_database_mutation(tmp_path):
    ast, plan, _ = _fixture()
    alternate = [
        ast[0].model_copy(update={"payload": ParagraphPayload(content="Other source.")}),
        ast[1],
    ]
    with closing(_connection(tmp_path / "queue.db")) as conn:
        with pytest.raises(ValueError, match="W08_CONTEXT_AST_GENERATION_MISMATCH"):
            DurableContextPlanRepository(ControlPlaneRepository(conn)).enqueue_verified(
                plan, alternate,
            )
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0


def test_w08_injected_sqlite_failure_rolls_back_plan_tasks_and_snapshot(tmp_path):
    ast, plan, _ = _fixture()
    with closing(_connection(tmp_path / "queue.db")) as conn:
        # The trigger fires only after the manifest and its task have been staged.
        conn.execute("""CREATE TABLE g3_context_snapshots (
            document_id TEXT, ast_hash TEXT, manifest_sha256 TEXT,
            context_id TEXT, snapshot_sha256 TEXT, snapshot_json TEXT,
            created_at REAL
        )""")
        conn.execute("""CREATE TRIGGER deny_w08_snapshot BEFORE INSERT
            ON g3_context_snapshots BEGIN SELECT RAISE(ABORT, 'synthetic snapshot crash'); END""")
        conn.commit()
        with pytest.raises(sqlite3.IntegrityError, match="synthetic snapshot crash"):
            DurableContextPlanRepository(ControlPlaneRepository(conn)).enqueue_verified(
                plan, ast,
            )
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM g3_context_snapshots").fetchone()[0] == 0


def test_w08_snapshot_write_respects_external_transaction_rollback(tmp_path):
    ast, plan, _ = _fixture()
    with closing(_connection(tmp_path / "queue.db")) as conn:
        conn.execute("BEGIN")
        DurableContextPlanRepository(ControlPlaneRepository(conn)).enqueue_verified(plan, ast)
        assert conn.in_transaction
        conn.rollback()
        assert conn.execute("SELECT COUNT(*) FROM chunk_plans").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM chunk_tasks").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM g3_context_snapshots").fetchone()[0] == 0


def test_w08_derived_snapshots_never_claim_a_provider_authority():
    ast, plan, context_id = _fixture()
    snapshots = derive_verified_plan_contexts(plan, ast)
    assert set(snapshots) == {context_id}
    assert "execution_id" not in snapshots[context_id].to_json()
