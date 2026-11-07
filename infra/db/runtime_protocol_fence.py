"""W08-2d: opt-in SQLite protocol fence for cooperative rolling upgrades.

This is a VERSION COMPATIBILITY guard, not caller authentication. A legacy
SQLite client which does not register the W08 function cannot write guarded
queue tables once the fence has been explicitly activated.

Activation must follow operator-controlled drain and exclusive shutdown of
old runtimes. SQLite DDL privileges can drop triggers; other DBs and already
started external calls are outside this boundary.
"""
from __future__ import annotations

import sqlite3
import time
from typing import Mapping

from infra.db.runtime_cutover_approval import (
    SignedCutoverApproval, inventory_in_transaction, verify_cutover_approval,
)

from core.execution.exceptions import PipelineIntegrityError


_PROTOCOL = "w08-context-durable-v1"
_FUNCTION_NAME = "w08_runtime_protocol"
_GUARDED_TABLES = (
    "chunk_tasks", "chunk_plans", "chunk_result_receipts",
    "g3_context_snapshots", "g3_runtime_protocol_fence",
)
_ACTIONS = ("INSERT", "UPDATE", "DELETE")

_DDL = """CREATE TABLE IF NOT EXISTS g3_runtime_protocol_fence (
    slot INTEGER PRIMARY KEY CHECK(slot=1),
    required_protocol TEXT NOT NULL,
    operator_id TEXT NOT NULL,
    change_ticket TEXT NOT NULL,
    activated_at REAL NOT NULL
)"""


def bind_runtime_protocol(conn: sqlite3.Connection) -> None:
    """Composition-root opt-in on new queue connections, never a secret."""
    conn.create_function(_FUNCTION_NAME, 0, lambda: _PROTOCOL)


def verify_runtime_protocol(conn: sqlite3.Connection) -> None:
    """Read-only check before intake/dispatch; old DBs remain unmodified."""
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' "
        "AND name='g3_runtime_protocol_fence'",
    ).fetchone()
    if table is None:
        return
    rows = conn.execute(
        "SELECT required_protocol FROM g3_runtime_protocol_fence WHERE slot=1",
    ).fetchall()
    if len(rows) != 1 or rows[0][0] != _PROTOCOL:
        raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_INCOMPATIBLE")
    try:
        actual = conn.execute("SELECT w08_runtime_protocol()").fetchone()
    except sqlite3.OperationalError as exc:
        raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_NOT_REGISTERED") from exc
    if actual != (_PROTOCOL,):
        raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_INCOMPATIBLE")
    # An activation record without all matching triggers is an invalid
    # fence, never an invitation to run or to repair it silently.
    triggers = conn.execute(
        "SELECT name,sql FROM sqlite_master "
        "WHERE type='trigger' AND name LIKE 'g3_w08_fence_%'",
    ).fetchall()
    expected = {
        f"g3_w08_fence_{table}_{action.lower()}"
        for table in _GUARDED_TABLES for action in _ACTIONS
    }
    actual_names = {name for name, _ in triggers}
    if (actual_names != expected
            or any(
                not isinstance(sql, str)
                or _FUNCTION_NAME not in sql
                or _PROTOCOL not in sql
                for _, sql in triggers
            )):
        raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_TRIGGERS_INCOMPLETE")


def activate_runtime_protocol_fence(
    conn: sqlite3.Connection, *,
    approval: SignedCutoverApproval,
    trusted_operator_keys: Mapping[str, bytes],
    drained_legacy_runtimes: bool,
) -> None:
    """Signed, inventory-bound activation; external process drain still required.

    No unsigned operator_id/change_ticket or bare boolean can activate the
    fence. The trusted registry is supplied by a separately controlled operator
    channel; this function does not supply/derive operator keys or IAM.
    """
    if type(drained_legacy_runtimes) is not bool or not drained_legacy_runtimes:
        raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_ACTIVATION_NOT_AUTHORIZED")
    if conn.in_transaction:
        raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_ACTIVE_TRANSACTION")

    verify_runtime_protocol(conn)  # Reject drift if already activated.
    try:
        current = conn.execute("SELECT w08_runtime_protocol()").fetchone()
    except sqlite3.OperationalError as exc:
        raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_NOT_REGISTERED") from exc
    if current != (_PROTOCOL,):
        raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_INCOMPATIBLE")
    try:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' "
            "AND name='g3_runtime_protocol_fence'"
        ).fetchone() is not None:
            raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_ALREADY_ACTIVATED")
        inventory = inventory_in_transaction(conn)
        verify_cutover_approval(
            approval, inventory, trusted_operator_keys=trusted_operator_keys,
        )
        if inventory.processing_count:
            raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_ACTIVE_CLAIMS")
        if inventory.active_leases or inventory.active_task_leases:
            raise PipelineIntegrityError("W08_RUNTIME_PROTOCOL_ACTIVE_LEASES")

        # No schema auto-upgrade/migration of existing plans or receipts.
        conn.execute(_DDL)
        conn.execute(
            "INSERT INTO g3_runtime_protocol_fence "
            "(slot,required_protocol,operator_id,change_ticket,activated_at) "
            "VALUES (1,?,?,?,?)",
            (_PROTOCOL, approval.operator_id, approval.change_ticket, time.time()),
        )

        # W08-2b's snapshot table is added only if not yet present. It stays
        # empty for legacy generations; it never backfills or makes them runnable.
        from infra.db.context_snapshot_repo import _CONTEXT_SNAPSHOTS_DDL

        conn.execute(_CONTEXT_SNAPSHOTS_DDL)
        for table in _GUARDED_TABLES:
            for action in _ACTIONS:
                # Names are compile-time constants. The UDF is intentionally
                # absent in old binaries: any legacy write aborts atomically.
                name = f"g3_w08_fence_{table}_{action.lower()}"
                conn.execute(
                    f"CREATE TRIGGER IF NOT EXISTS {name} "
                    f"BEFORE {action} ON {table} BEGIN "
                    f"SELECT CASE WHEN {_FUNCTION_NAME}() IS NOT '{_PROTOCOL}' "
                    "THEN RAISE(ABORT, 'W08_RUNTIME_PROTOCOL_INCOMPATIBLE') END; "
                    "END"
                )
        conn.commit()
    except BaseException:
        if conn.in_transaction:
            conn.rollback()
        raise
