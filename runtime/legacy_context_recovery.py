"""W08-2d: explicit, providerless recovery for historical G3 plan receipts.

An old plan without contextual snapshots is NOT eligible for inference, retry,
task claim, or content reconstruction. An operator may authorize only the
existing B4/3b publication replay, after all original receipts are verified.
This policy does not prove exclusive deployment or migrate the legacy plan.
"""
from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Sequence

from core.ast.models import ASTNode, TranslationTaskType
from core.chunking.manifest_contract import ChunkPlan
from core.context.snapshot_contract import ContextSnapshotV1
from core.execution.exceptions import PipelineIntegrityError
from infra.db.context_snapshot_repo import DurableContextPlanRepository
from infra.db.control_repo import ControlPlaneRepository


@dataclass(frozen=True, slots=True)
class G3ContextPreflight:
    plan: ChunkPlan
    context_snapshots: dict[str, ContextSnapshotV1]
    receipt_only_legacy: bool


def _snapshot_table_exists(conn: sqlite3.Connection) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master "
        "WHERE type='table' AND name='g3_context_snapshots'"
    ).fetchone() is not None


def _has_generation_snapshots(
    conn: sqlite3.Connection, document_id: str, ast_hash: str,
) -> bool:
    if not _snapshot_table_exists(conn):
        return False
    return conn.execute(
        "SELECT 1 FROM g3_context_snapshots "
        "WHERE document_id=? AND ast_hash=? LIMIT 1",
        (document_id, ast_hash),
    ).fetchone() is not None


def preflight_g3_context(
    repo: ControlPlaneRepository,
    document_id: str,
    ast_hash: str,
    ast: Sequence[ASTNode],
    *,
    allow_receipt_only_legacy: bool = False,
) -> G3ContextPreflight:
    """Resolve all inference context or authorize verified receipt-only replay.

    False is the default for all normal engine/daemon calls. Even an authorized
    legacy replay requires a complete homogeneous RESULT_STAGED or COMPLETED
    plan with every original receipt bound to the persisted manifest and
    execution. A partial generation, any UNKNOWN, or a modern generation with
    lost context is NEVER accepted as a legacy recovery.
    """
    if type(allow_receipt_only_legacy) is not bool:
        raise ValueError("W08_LEGACY_RECOVERY_INVALID_AUTHORIZATION")

    # Verify durable AST/manifest/task identity even when snapshots are absent.
    plan = repo.load_chunk_plan(document_id, ast_hash, ast)
    table_exists = _snapshot_table_exists(repo.conn)
    has_snapshots = _has_generation_snapshots(repo.conn, document_id, ast_hash)
    needs_context = any(
        unit.chunk_type != TranslationTaskType.PRESERVE for unit in plan.units
    )

    # Contextual generations must pass the same complete verification as W08-2c.
    # PRESERVE-only current plans legitimately have zero snapshot rows.
    if has_snapshots or (table_exists and not needs_context):
        verified, snapshots = DurableContextPlanRepository(repo).load_verified(
            document_id, ast_hash, ast,
        )
        return G3ContextPreflight(verified, snapshots, False)

    if not allow_receipt_only_legacy:
        raise PipelineIntegrityError("W08_LEGACY_RECOVERY_OPERATOR_APPROVAL_REQUIRED")

    # Contextual ASTs and modern CTX units are not silently reclassified as
    # historical when their snapshot rows disappear due to corruption.
    if (
        any(node.control_plane.get("context_id") is not None for node in ast)
        or any(unit.context_id.startswith("CTX_") for unit in plan.units)
    ):
        raise PipelineIntegrityError("W08_LEGACY_RECOVERY_PROVENANCE_NOT_LEGACY")

    rows = repo.conn.execute(
        "SELECT task_state FROM chunk_tasks "
        "WHERE document_id=? AND ast_hash=? AND worker_type='LLM'",
        (document_id, ast_hash),
    ).fetchall()
    states = {state for (state,) in rows}
    if len(rows) != len(plan.units) or states not in (
        {"RESULT_STAGED"}, {"COMPLETED"},
    ):
        raise PipelineIntegrityError("W08_LEGACY_RECOVERY_NOT_RECEIPT_ONLY")

    # This existing read-only gate checks plan/AST, per-member source hashes,
    # task/receipt/execution IDs and complete response coverage. Absence of a
    # cache hit is NEVER evidence of an unstarted provider effect.
    try:
        repo.load_staged_chunk_responses(
            plan, ast, allow_completed=states == {"COMPLETED"},
        )
    except (ValueError, sqlite3.Error) as exc:
        raise PipelineIntegrityError("W08_LEGACY_RECOVERY_RECEIPTS_UNVERIFIED") from exc

    return G3ContextPreflight(plan, {}, True)
