"""W08-2d: operator-only legacy receipt replay, real disposable SQLite.

No paid LLM, fake egress, Docker, canonical PDF or production DB.
W06 uncertain effects remain quarantined; this cannot infer old context.
"""
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.grouper import SemanticGroup
from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode, MathPayload, ParagraphPayload, TranslationTaskType
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import ChunkPolicy, TokenBudgetChunker
from core.execution.exceptions import PipelineIntegrityError
from infra.db.control_repo import ControlPlaneRepository
from infra.db.fsm_repository import FSMRepository
from infra.db.staged_publication import publish_staged_plan, finalize_published_plan
from runtime.legacy_context_recovery import (
    preflight_g3_context, recover_legacy_staged_document,
)


ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()))


def _response(plan, unit) -> str:
    return json.dumps({
        "schema_version": 1, "document_id": plan.document_id,
        "ast_hash": plan.ast_hash, "manifest_sha256": plan.digest,
        "chunk_id": unit.chunk_id,
        "members": [
            {"node_id": m.node_id, "segment_index": m.segment_index,
             "source_sha256": sha256(m.source_text.encode("utf-8")).hexdigest(),
             "translated_text": "Texto traducido."}
            for m in unit.members
        ],
    }, ensure_ascii=False)


@pytest.fixture
def legacy(tmp_path):
    ast = [
        ASTNode(
            node_id="equation", sequence_id=1,
            node_type=ContentNodeType.DISPLAY_EQUATION,
            strategy=TranslationStrategy.PASSTHROUGH,
            payload=MathPayload(content="E=mc^2"),
        ),
        ASTNode(
            node_id="paragraph", sequence_id=2,
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Alpha."),
        ),
    ]
    units = TokenBudgetChunker(
        _Estimator(), ChunkPolicy(max_tokens=80, prompt_overhead_tokens=0),
    ).chunk_group(
        SemanticGroup(structural_path=(), context_id="legacy_ctx", nodes=ast), 1,
    )
    plan = ChunkPlan.build("doc_legacy", compute_ast_hash(ast), ast, units)
    q = sqlite3.connect(tmp_path / "queue.db")
    m = sqlite3.connect(tmp_path / "materialized.db")
    f = sqlite3.connect(tmp_path / "fsm.db")
    q.execute("PRAGMA foreign_keys=ON")
    q.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    m.executescript((ROOT / "infra/db/schema_materialized.sql").read_text(encoding="utf-8"))
    f.execute("""CREATE TABLE document_fsm (
        document_id TEXT NOT NULL, ast_hash TEXT NOT NULL,
        current_state TEXT NOT NULL, state_version INTEGER NOT NULL,
        is_terminal INTEGER NOT NULL DEFAULT 0,
        entered_state_at REAL NOT NULL, updated_at REAL NOT NULL,
        failure_reason TEXT, suspended_state TEXT,
        PRIMARY KEY(document_id, ast_hash)
    )""")
    f.execute(
        "INSERT INTO document_fsm "
        "(document_id,ast_hash,current_state,state_version,entered_state_at,updated_at) "
        "VALUES (?,?,'PROCESSING',1,1.0,1.0)",
        (plan.document_id, plan.ast_hash),
    )
    f.commit()
    repo = ControlPlaneRepository(q)
    repo.enqueue_chunk_plan(plan, ast)
    from types import SimpleNamespace
    fixture = SimpleNamespace(
        q=q, m=m, f=f, repo=repo, fsm=FSMRepository(f),
        ast=ast, plan=plan, root=tmp_path,
    )
    try:
        yield fixture
    finally:
        q.close()
        m.close()
        f.close()


def _stage_all(d):
    for unit in d.plan.units:
        lease = d.repo.pick_task("worker", d.plan.document_id, d.plan.ast_hash)
        assert lease is not None and lease.node_id == unit.chunk_id
        d.repo.stage_chunk_result(
            d.plan, d.ast, chunk_id=unit.chunk_id, task_id=lease.task_id,
            worker_id="worker", execution_id=lease.execution_id,
            raw_response=(
                None if unit.chunk_type == TranslationTaskType.PRESERVE
                else _response(d.plan, unit)
            ),
        )


def _recover(d, **overrides):
    kwargs = {"approved_by_operator": True, "owner_id": "operator_w08"}
    kwargs.update(overrides)
    return recover_legacy_staged_document(
        d.repo, d.m, d.fsm, d.plan.document_id, d.plan.ast_hash, d.ast,
        **kwargs,
    )


def _states(d):
    return [
        x[0] for x in d.q.execute(
            "SELECT task_state FROM chunk_tasks "
            "WHERE document_id=? AND ast_hash=? ORDER BY task_id",
            (d.plan.document_id, d.plan.ast_hash),
        )
    ]


def test_legacy_default_preflight_denies_even_fully_staged(legacy):
    _stage_all(legacy)
    with pytest.raises(PipelineIntegrityError, match="OPERATOR_APPROVAL_REQUIRED"):
        preflight_g3_context(
            legacy.repo, legacy.plan.document_id, legacy.plan.ast_hash,
            legacy.ast,
        )
    with pytest.raises(PipelineIntegrityError, match="OPERATOR_APPROVAL_REQUIRED"):
        _recover(legacy, approved_by_operator=False)
    assert _states(legacy) == ["RESULT_STAGED"] * len(legacy.plan.units)
    assert legacy.m.execute("SELECT COUNT(*) FROM valid_chunks_cache").fetchone()[0] == 0


def test_legacy_fully_staged_receipts_are_published_without_provider(legacy):
    _stage_all(legacy)
    assert _recover(legacy)
    assert set(_states(legacy)) == {"COMPLETED"}
    assert legacy.fsm.get_status(
        legacy.plan.document_id, legacy.plan.ast_hash,
    ).current_state == "READY_FOR_ASSEMBLY"
    assert legacy.m.execute(
        "SELECT COUNT(*) FROM valid_chunks_cache"
    ).fetchone()[0] == len(legacy.ast)
    assert legacy.q.execute(
        "SELECT COUNT(*) FROM chunk_result_receipts"
    ).fetchone()[0] == len(legacy.plan.units)
    assert legacy.q.execute(
        "SELECT COUNT(*) FROM g3_context_snapshots"
        if legacy.q.execute(
            "SELECT 1 FROM sqlite_master WHERE name='g3_context_snapshots'"
        ).fetchone() else "SELECT 0"
    ).fetchone()[0] == 0


def test_legacy_published_projection_before_crash_is_replayed(legacy):
    _stage_all(legacy)
    assert publish_staged_plan(legacy.repo, legacy.m, legacy.plan, legacy.ast)
    assert _states(legacy) == ["RESULT_STAGED"] * len(legacy.plan.units)
    assert _recover(legacy)
    assert set(_states(legacy)) == {"COMPLETED"}


def test_legacy_completed_queue_with_pending_fsm_recovers_without_provider(legacy):
    _stage_all(legacy)
    publish_staged_plan(legacy.repo, legacy.m, legacy.plan, legacy.ast)
    finalize_published_plan(legacy.repo, legacy.m, legacy.plan, legacy.ast)
    assert set(_states(legacy)) == {"COMPLETED"}
    assert _recover(legacy)
    assert legacy.fsm.get_status(
        legacy.plan.document_id, legacy.plan.ast_hash,
    ).current_state == "READY_FOR_ASSEMBLY"


@pytest.mark.parametrize("state", ["PENDING", "PROCESSING", "RETRYABLE_ERROR", "G3_EXTERNAL_UNKNOWN", "FAILED"])
def test_legacy_never_retries_nonreceipt_states(legacy, state):
    _stage_all(legacy)
    legacy.q.execute(
        "UPDATE chunk_tasks SET task_state=? WHERE node_id=?",
        (state, legacy.plan.units[-1].chunk_id),
    )
    legacy.q.commit()
    with pytest.raises(PipelineIntegrityError, match="W08_LEGACY_RECOVERY_NOT_RECEIPT_ONLY"):
        _recover(legacy)
    assert legacy.m.execute("SELECT COUNT(*) FROM valid_chunks_cache").fetchone()[0] == 0
    assert _states(legacy).count(state) >= 1


def test_legacy_rejects_missing_receipt_without_any_publication(legacy):
    _stage_all(legacy)
    legacy.q.execute(
        "DELETE FROM chunk_result_receipts WHERE chunk_id=?",
        (legacy.plan.units[-1].chunk_id,),
    )
    legacy.q.commit()
    with pytest.raises(PipelineIntegrityError, match="W08_LEGACY_RECOVERY_RECEIPTS_UNVERIFIED"):
        _recover(legacy)
    assert legacy.m.execute("SELECT COUNT(*) FROM valid_chunks_cache").fetchone()[0] == 0


def test_legacy_rejects_corrupt_checksum_without_any_publication(legacy):
    _stage_all(legacy)
    legacy.q.execute(
        "UPDATE chunk_result_receipts SET raw_response='corrupt' WHERE chunk_id=?",
        (legacy.plan.units[-1].chunk_id,),
    )
    legacy.q.commit()
    with pytest.raises(PipelineIntegrityError, match="W08_LEGACY_RECOVERY_RECEIPTS_UNVERIFIED"):
        _recover(legacy)
    assert legacy.m.execute("SELECT COUNT(*) FROM valid_chunks_cache").fetchone()[0] == 0


def test_legacy_rejects_mismatched_fsm_state(legacy):
    _stage_all(legacy)
    legacy.f.execute("UPDATE document_fsm SET current_state='CANCELLED'")
    legacy.f.commit()
    with pytest.raises(PipelineIntegrityError, match="W08_LEGACY_RECOVERY_FSM_NOT_PROCESSING"):
        _recover(legacy)
    assert set(_states(legacy)) == {"RESULT_STAGED"}


def test_legacy_rejects_snapshot_deletion_from_modern_ast(legacy):
    _stage_all(legacy)
    enriched_ast = [
        node.model_copy(
            update={"control_plane": {"context_id": "CTX_AABBCCDDEEFF"}}
        ) for node in legacy.ast
    ]
    with pytest.raises(PipelineIntegrityError, match="W08_LEGACY_RECOVERY_PROVENANCE_NOT_LEGACY"):
        recover_legacy_staged_document(
            legacy.repo, legacy.m, legacy.fsm,
            legacy.plan.document_id, legacy.plan.ast_hash, enriched_ast,
            approved_by_operator=True, owner_id="operator_w08",
        )


def test_legacy_rejects_modern_plan_without_snapshot_even_if_all_staged(legacy):
    _stage_all(legacy)
    payload = json.loads(legacy.plan.to_json())
    assert isinstance(payload, dict)
    # Rewriting the stored manifest would invalidate its SHA and must not
    # accidentally pass a legacy preflight.
    legacy.q.execute(
        "UPDATE chunk_plans SET manifest_json='{}' WHERE document_id=?",
        (legacy.plan.document_id,),
    )
    legacy.q.commit()
    with pytest.raises(ValueError):
        _recover(legacy)
    assert legacy.m.execute("SELECT COUNT(*) FROM valid_chunks_cache").fetchone()[0] == 0
