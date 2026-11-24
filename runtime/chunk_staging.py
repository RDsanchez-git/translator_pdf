"""G3-B4/3a: stage one leased semantic unit; never publish or acknowledge.

The ControlPlaneRepository owns the fencing and the SQLite transaction.
This adapter has no provider-specific code, daemon dependencies or side effects
outside the repo/provider passed by its caller.
"""

from __future__ import annotations

import sqlite3
import time
import logging
from threading import Semaphore
from typing import Protocol, Sequence, cast

from core.ast.models import ASTNode, TranslationTaskType, TranslationUnit
from core.chunking.manifest_contract import ChunkPlan
from core.execution.ports import TaskLease
from core.execution.exceptions import G3ExternalEffectNotStartedError
from core.execution.effect_guard import (
    g3_pre_effect_guard, g3_admission_audit_writer,
)
from infra.db.control_repo import ControlPlaneRepository


logger = logging.getLogger(__name__)


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
    expected_task_id = repo.chunk_plan_task_ids(plan).get(unit.chunk_id)
    if expected_task_id != lease.task_id:
        raise ValueError("G3_B4_3A_LEASE_TASK_MISMATCH")
    if lease.lease_expires_at <= time.time():
        raise G3ExternalEffectNotStartedError("G3_B4_3A_EXPIRED_LEASE")

    generation_sha256: str | None = None
    root_config_sha256: str | None = None
    response_ready_ns: int | None = None
    if unit.chunk_type == TranslationTaskType.PRESERVE:
        raw_response = None
    elif unit.chunk_type in (TranslationTaskType.TRANSLATE, TranslationTaskType.PARTIAL):
        if processor is None:
            raise G3ExternalEffectNotStartedError("G3_B4_3A_PROVIDER_REQUIRED")
        with llm_semaphore:
            # Recheck *durable* owner/execution/expiry after semaphore wait.
            # This is the last controlled boundary before provider invocation.
            repo.assert_g3_effect_authority(
                lease=lease, worker_id=worker_id,
                document_id=plan.document_id, ast_hash=plan.ast_hash,
            )
            # SyncProviderBridge propagates this context into its asyncio task.
            # The rate limiter rechecks it after its last quota wait, immediately
            # before delegating to the actual external provider.
            queue_path = repo.conn.execute("PRAGMA database_list").fetchone()[2]

            def check_before_external_io() -> None:
                if not queue_path:
                    raise G3ExternalEffectNotStartedError(
                        "PPPR_G3_PRE_EFFECT_QUEUE_NOT_RECOVERABLE"
                    )
                # The guard executes on the asyncio thread; do not share the
                # worker thread's SQLite connection. This is a short read.
                with sqlite3.connect(queue_path, timeout=5.0) as probe:
                    ControlPlaneRepository(probe).assert_g3_effect_authority(
                        lease=lease, worker_id=worker_id,
                        document_id=plan.document_id, ast_hash=plan.ast_hash,
                    )

            def record_admission(generation_sha256: str, audit_json: str) -> None:
                repo.record_g3_admission_decision(
                    task_id=lease.task_id, worker_id=worker_id,
                    execution_id=lease.execution_id,
                    generation_sha256=generation_sha256,
                    audit_json=audit_json,
                )

            token = g3_pre_effect_guard.set(check_before_external_io)
            audit_token = g3_admission_audit_writer.set(record_admission)
            try:
                if getattr(processor, "generation_identity_enabled", False):
                    attested_executor = getattr(processor, "execute_chunk_with_generation", None)
                    if not callable(attested_executor):
                        raise G3ExternalEffectNotStartedError("PPPR_G2_ATTESTED_PROVIDER_MISSING")
                    raw_response, generation_sha256 = cast(tuple[str, str], attested_executor(plan, unit))
                    response_ready_ns = time.monotonic_ns()
                    root_config_sha256 = getattr(processor, "generation_root_config_sha256", None)
                else:
                    # Historic/offline providers cannot claim an accredited
                    # generation; no reuse authority is inferred from this path.
                    raw_response = processor.execute_chunk(plan, unit)
            finally:
                g3_admission_audit_writer.reset(audit_token)
                g3_pre_effect_guard.reset(token)
        if not isinstance(cast(object, raw_response), str):
            raise ValueError("G3_B4_3A_PROVIDER_RESPONSE_NOT_TEXT")
    else:
        raise ValueError("G3_B4_3A_UNSUPPORTED_TASK_TYPE")

    if generation_sha256 is not None:
        # Observe the narrower client interval: validated bridge return to
        # locally committed new receipt. Never imply remote completion time,
        # fsync/power-loss durability or a bound on external exposure.
        duration_ns: int | None = None
        try:
            inserted = repo.stage_chunk_result(
                plan, ast, chunk_id=unit.chunk_id, task_id=lease.task_id,
                worker_id=worker_id, execution_id=lease.execution_id,
                raw_response=raw_response, generation_sha256=generation_sha256,
                root_config_sha256=root_config_sha256,
            )
            if inserted and not repo.conn.in_transaction and response_ready_ns is not None:
                duration_ns = time.monotonic_ns() - response_ready_ns
            return inserted
        finally:
            # No committed new receipt observed (fault, replay or caller-owned
            # transaction): the complete interval is unavailable, not zero.
            logger.info("PPPR_G3_CLIENT_RECEIPT_WINDOW", extra={"extra_data": {
                "task_id": lease.task_id, "execution_id": lease.execution_id,
                "generation_sha256": generation_sha256,
                "observed_at_ns": time.time_ns(),
                "duration_ns": duration_ns,
                "classification": "MEASURED" if duration_ns is not None else "NOT_OBSERVABLE",
            }})
    return repo.stage_chunk_result(
        plan, ast, chunk_id=unit.chunk_id, task_id=lease.task_id,
        worker_id=worker_id, execution_id=lease.execution_id,
        raw_response=raw_response,
    )
