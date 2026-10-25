"""G3-B4/3b: durable staged-plan publication and document FSM barrier.

Publication, queue finalization and FSM transition are separate committed steps.
Re-execution verifies persisted evidence rather than repeating provider inference.
"""
from __future__ import annotations

import sqlite3
from typing import Sequence

from core.ast.models import ASTNode
from core.chunking.manifest_contract import ChunkPlan
from core.execution.handlers import DocumentCommandHandler
from core.execution.state import DocumentState, MarkAssemblyReadyCommand
from infra.db.control_repo import ControlPlaneRepository
from infra.db.fsm_repository import FSMRepository
from infra.db.staged_publication import finalize_published_plan, publish_staged_plan


def advance_staged_document(
    queue_repo: ControlPlaneRepository,
    materialized_conn: sqlite3.Connection,
    fsm_repo: FSMRepository,
    plan: ChunkPlan,
    ast: Sequence[ASTNode],
    owner_id: str,
    *,
    projection_version: int = 1,
) -> bool:
    """Publish -> finalize -> CAS FSM, returning True only on an FSM transition.

    Both durable intermediate steps can be replayed after process termination.
    All generation/receipt/projection checks remain in the B2/B3 contracts.
    Never call a provider, synthesize missing members or acknowledge a lease.
    """
    status = fsm_repo.get_status(plan.document_id, plan.ast_hash)
    if status is None or status.current_state != DocumentState.PROCESSING.value:
        raise ValueError("G3_B4_3B_DOCUMENT_NOT_PROCESSING")

    rows = queue_repo.conn.execute(
        "SELECT task_state FROM chunk_tasks WHERE document_id=? AND ast_hash=? "
        "AND worker_type='LLM'",
        (plan.document_id, plan.ast_hash),
    ).fetchall()
    states = {row[0] for row in rows}
    if len(rows) != len(plan.units) or states not in ({"RESULT_STAGED"}, {"COMPLETED"}):
        raise ValueError("G3_B4_3B_INCOMPLETE_OR_MIXED_PLAN")

    if states == {"RESULT_STAGED"}:
        publish_staged_plan(queue_repo, materialized_conn, plan, ast,
                            projection_version=projection_version)

    # Verifies committed publication and every original receipt, including replay
    # with all queue tasks COMPLETED. Never trusts a noncommitted materialized DB.
    finalize_published_plan(queue_repo, materialized_conn, plan, ast,
                            projection_version=projection_version)

    # Revalidate before FSM CAS. The handler rejects competing state versions.
    status = fsm_repo.get_status(plan.document_id, plan.ast_hash)
    if status is None or status.current_state != DocumentState.PROCESSING.value:
        raise ValueError("G3_B4_3B_DOCUMENT_STATE_DRIFT")
    DocumentCommandHandler(fsm_repo, task_repo=queue_repo).handle(
        MarkAssemblyReadyCommand(plan.document_id, plan.ast_hash,
                                 owner_id, status.state_version),
    )
    return True
