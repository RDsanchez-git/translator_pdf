"""G3-B4/3a: stage one leased semantic unit; never publish or acknowledge.

The ControlPlaneRepository owns the fencing and the SQLite transaction.
This adapter has no provider-specific code, daemon dependencies or side effects
outside the repo/provider passed by its caller.
"""

from __future__ import annotations

import time
from threading import Semaphore
from typing import Protocol, Sequence

from core.ast.models import ASTNode, TranslationTaskType, TranslationUnit
from core.chunking.manifest_contract import ChunkPlan
from core.execution.ports import TaskLease
from infra.db.control_repo import ControlPlaneRepository


class ChunkProcessor(Protocol):
    def execute_chunk(self, plan: ChunkPlan, unit: TranslationUnit) -> str: ...


def stage_claimed_unit(
    repo: ControlPlaneRepository,
    plan: ChunkPlan,
    ast: Sequence[ASTNode],
    unit: TranslationUnit,
    lease: TaskLease,
    worker_id: str,
    processor: ChunkProcessor | None,
    llm_semaphore: Semaphore,
) -> bool:
    """Stage only. False means an *identical* existing receipt, never ACK.

    Reject an obviously wrong or expired lease before invoking a paid provider;
    stage_chunk_result performs authoritative database fencing afterwards.
    """
    if unit.chunk_id != lease.node_id:
        raise ValueError("G3_B4_3A_LEASE_CHUNK_MISMATCH")
    expected_task_id = repo._chunk_plan_task_ids(plan).get(unit.chunk_id)
    if expected_task_id != lease.task_id:
        raise ValueError("G3_B4_3A_LEASE_TASK_MISMATCH")
    if lease.lease_expires_at <= time.time():
        raise ValueError("G3_B4_3A_EXPIRED_LEASE")

    if unit.chunk_type == TranslationTaskType.PRESERVE:
        raw_response = None
    elif unit.chunk_type in (TranslationTaskType.TRANSLATE, TranslationTaskType.PARTIAL):
        if processor is None:
            raise ValueError("G3_B4_3A_PROVIDER_REQUIRED")
        with llm_semaphore:
            raw_response = processor.execute_chunk(plan, unit)
        if not isinstance(raw_response, str):
            raise ValueError("G3_B4_3A_PROVIDER_RESPONSE_NOT_TEXT")
    else:
        raise ValueError("G3_B4_3A_UNSUPPORTED_TASK_TYPE")

    return repo.stage_chunk_result(
        plan, ast, chunk_id=unit.chunk_id, task_id=lease.task_id,
        worker_id=worker_id, execution_id=lease.execution_id,
        raw_response=raw_response,
    )
