"""W08-2d: deterministic read-only queue inventory and short-lived signed approval.

The HMAC verifier is a *cryptographic gate*, not a complete IAM system.
The trusted key registry MUST come from a separate access-controlled operator
channel, never from the approval payload, client request or repository. Both
issuing and verifying parties hold the shared secret; its custody is external.

No database mutations, remote provider calls, PID checks, Docker or PDF corpus.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
import json
import os
import secrets
import sqlite3
import time
from typing import Mapping

from core.execution.exceptions import PipelineIntegrityError


_APPROVAL_SCHEMA = 1
_APPROVAL_ACTION = "activate-w08-context-durable-v1"
_MAX_APPROVAL_LIFETIME_SEC = 300
_MAX_CLOCK_SKEW_SEC = 30


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")


def _required_table(conn: sqlite3.Connection, name: str) -> None:
    if conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone() is None:
        raise PipelineIntegrityError("W08_CUTOVER_INVENTORY_TABLE_MISSING")


@dataclass(frozen=True, slots=True)
class QueueCutoverInventory:
    """Document-free summary; digest covers all selected rows, not just counts."""

    queue_path_sha256: str
    inventory_sha256: str
    task_count: int
    plan_count: int
    receipt_count: int
    context_count: int
    processing_count: int
    external_unknown_count: int
    staged_count: int
    completed_count: int
    active_leases: int
    active_task_leases: int


def _rows(conn: sqlite3.Connection, query: str) -> list[tuple[object, ...]]:
    return [tuple(row) for row in conn.execute(query).fetchall()]


def inventory_in_transaction(
    conn: sqlite3.Connection, *, now: float | None = None,
) -> QueueCutoverInventory:
    """Snapshot under caller-owned SQLite transaction. Never COMMIT here."""
    if not conn.in_transaction:
        raise PipelineIntegrityError("W08_CUTOVER_INVENTORY_REQUIRES_TRANSACTION")
    for table in ("chunk_tasks", "chunk_plans", "chunk_result_receipts", "system_leases"):
        _required_table(conn, table)
    db_paths = [
        path for _, name, path in conn.execute("PRAGMA database_list").fetchall()
        if name == "main"
    ]
    if len(db_paths) != 1 or not db_paths[0]:
        raise PipelineIntegrityError("W08_CUTOVER_INVENTORY_UNBOUND_QUEUE")
    path_sha = sha256(os.path.realpath(db_paths[0]).encode("utf-8")).hexdigest()

    task_rows = _rows(conn,
        "SELECT task_id,document_id,ast_hash,node_id,task_state,worker_type,"
        "execution_id,retry_count,lease_owner,lease_expires_at,state_version,"
        "error_log FROM chunk_tasks ORDER BY task_id"
    )
    plan_rows = _rows(conn,
        "SELECT document_id,ast_hash,manifest_sha256,manifest_json "
        "FROM chunk_plans ORDER BY document_id,ast_hash"
    )
    receipt_rows = _rows(conn,
        "SELECT document_id,ast_hash,chunk_id,task_id,execution_id,"
        "raw_response,response_sha256 FROM chunk_result_receipts "
        "ORDER BY document_id,ast_hash,chunk_id"
    )
    receipt_fingerprints = [
        (*row[:5], sha256(row[5].encode("utf-8")).hexdigest()
         if isinstance(row[5], str) else None, row[6])
        for row in receipt_rows
    ]
    exists_snapshots = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' "
        "AND name='g3_context_snapshots'"
    ).fetchone() is not None
    snap_rows = _rows(conn,
        "SELECT document_id,ast_hash,manifest_sha256,context_id,"
        "snapshot_sha256,snapshot_json FROM g3_context_snapshots "
        "ORDER BY document_id,ast_hash,context_id"
    ) if exists_snapshots else []
    snap_fingerprints = [
        (*row[:5], sha256(str(row[5]).encode("utf-8")).hexdigest())
        for row in snap_rows
    ]
    lease_rows = _rows(conn,
        "SELECT lease_name,owner_id,lease_expires_at,lease_version "
        "FROM system_leases ORDER BY lease_name"
    )
    time_now = time.time() if now is None else now
    active_leases = sum(
        isinstance(row[1], str) and bool(row[1])
        and row[2] is not None and float(row[2]) >= time_now
        for row in lease_rows
    )
    active_task_leases = sum(
        isinstance(row[8], str) and bool(row[8])
        and row[9] is not None and float(row[9]) >= time_now
        for row in task_rows
    )
    fingerprint = sha256(_canonical({
        "schema_version": 1,
        "queue_path_sha256": path_sha,
        "tasks": task_rows, "plans": plan_rows,
        "receipts": receipt_fingerprints,
        "snapshots_present": exists_snapshots,
        "snapshots": snap_fingerprints,
        "leases": lease_rows,
    })).hexdigest()
    states = [row[4] for row in task_rows]
    return QueueCutoverInventory(
        queue_path_sha256=path_sha, inventory_sha256=fingerprint,
        task_count=len(task_rows), plan_count=len(plan_rows),
        receipt_count=len(receipt_rows), context_count=len(snap_rows),
        processing_count=states.count("PROCESSING"),
        external_unknown_count=states.count("G3_EXTERNAL_UNKNOWN"),
        staged_count=states.count("RESULT_STAGED"),
        completed_count=states.count("COMPLETED"),
        active_leases=active_leases,
        active_task_leases=active_task_leases,
    )


def inspect_queue_cutover(conn: sqlite3.Connection) -> QueueCutoverInventory:
    """Read-only transaction; release owned SQLite snapshot before return."""
    if conn.in_transaction:
        return inventory_in_transaction(conn)
    conn.execute("BEGIN")
    try:
        return inventory_in_transaction(conn)
    finally:
        conn.rollback()


@dataclass(frozen=True, slots=True)
class SignedCutoverApproval:
    schema_version: int
    action: str
    operator_id: str
    change_ticket: str
    inventory_sha256: str
    queue_path_sha256: str
    issued_at: int
    expires_at: int
    nonce: str
    hmac_sha256: str

    def _body(self) -> dict[str, str | int]:
        return {
            "schema_version": self.schema_version,
            "action": self.action,
            "operator_id": self.operator_id,
            "change_ticket": self.change_ticket,
            "inventory_sha256": self.inventory_sha256,
            "queue_path_sha256": self.queue_path_sha256,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
        }


def _key_is_valid(secret: object) -> bool:
    return isinstance(secret, bytes) and len(secret) >= 32


def issue_cutover_approval(
    inventory: QueueCutoverInventory, *, operator_id: str,
    change_ticket: str, signing_secret: bytes,
    issued_at: int | None = None, lifetime_seconds: int = 120,
) -> SignedCutoverApproval:
    """Offline signing boundary; only run in an approved operator environment."""
    if (not operator_id.strip() or not change_ticket.strip()
            or not _key_is_valid(signing_secret)
            or type(lifetime_seconds) is not int
            or not 1 <= lifetime_seconds <= _MAX_APPROVAL_LIFETIME_SEC):
        raise PipelineIntegrityError("W08_CUTOVER_INVALID_APPROVAL_INPUT")
    ts = int(time.time()) if issued_at is None else issued_at
    unsigned = SignedCutoverApproval(
        schema_version=_APPROVAL_SCHEMA, action=_APPROVAL_ACTION,
        operator_id=operator_id, change_ticket=change_ticket,
        inventory_sha256=inventory.inventory_sha256,
        queue_path_sha256=inventory.queue_path_sha256,
        issued_at=ts, expires_at=ts + lifetime_seconds,
        nonce=secrets.token_hex(16), hmac_sha256="",
    )
    digest = hmac.new(signing_secret, _canonical(unsigned._body()), sha256).hexdigest()
    return SignedCutoverApproval(
        schema_version=unsigned.schema_version, action=unsigned.action,
        operator_id=unsigned.operator_id, change_ticket=unsigned.change_ticket,
        inventory_sha256=unsigned.inventory_sha256,
        queue_path_sha256=unsigned.queue_path_sha256,
        issued_at=unsigned.issued_at, expires_at=unsigned.expires_at,
        nonce=unsigned.nonce, hmac_sha256=digest,
    )


def verify_cutover_approval(
    approval: SignedCutoverApproval,
    inventory: QueueCutoverInventory, *,
    trusted_operator_keys: Mapping[str, bytes],
    now: float | None = None,
) -> None:
    """Reject stale, mismatched or untrusted signatures before any activation."""
    time_now = int(time.time() if now is None else now)
    if (
        approval.schema_version != _APPROVAL_SCHEMA
        or approval.action != _APPROVAL_ACTION
        or type(approval.issued_at) is not int
        or type(approval.expires_at) is not int
        or approval.expires_at <= approval.issued_at
        or approval.expires_at - approval.issued_at > _MAX_APPROVAL_LIFETIME_SEC
        or approval.issued_at > time_now + _MAX_CLOCK_SKEW_SEC
        or approval.expires_at < time_now
        or approval.inventory_sha256 != inventory.inventory_sha256
        or approval.queue_path_sha256 != inventory.queue_path_sha256
        or not approval.operator_id.strip()
        or not approval.change_ticket.strip()
        or len(approval.nonce) != 32
    ):
        raise PipelineIntegrityError("W08_CUTOVER_APPROVAL_SCOPE_OR_TIME_INVALID")
    secret = trusted_operator_keys.get(approval.operator_id)
    if not _key_is_valid(secret):
        raise PipelineIntegrityError("W08_CUTOVER_OPERATOR_NOT_TRUSTED")
    assert isinstance(secret, bytes)
    signed = hmac.new(secret, _canonical(approval._body()), sha256).hexdigest()
    if not hmac.compare_digest(signed, approval.hmac_sha256):
        raise PipelineIntegrityError("W08_CUTOVER_APPROVAL_SIGNATURE_INVALID")
