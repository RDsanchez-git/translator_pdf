"""W08-2d: adversarial offline inventory/approval test cases (no real DB)."""
from contextlib import closing
from dataclasses import replace
from pathlib import Path
import sqlite3

import pytest

from core.execution.exceptions import PipelineIntegrityError
from infra.db.runtime_cutover_approval import (
    inspect_queue_cutover, issue_cutover_approval, verify_cutover_approval,
)
from infra.db.runtime_protocol_fence import (
    activate_runtime_protocol_fence, bind_runtime_protocol,
)


ROOT = Path(__file__).resolve().parents[2]
_SECRET = b"another-test-only-operator-signing-secret-32-bytes"
_KEYS = {"operator-1": _SECRET}


def _db(tmp_path: Path, name: str = "queue.db") -> sqlite3.Connection:
    conn = sqlite3.connect(tmp_path / name)
    conn.executescript((ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf-8"))
    bind_runtime_protocol(conn)
    return conn


def _approve(conn: sqlite3.Connection, *, ts: int = 1_000_000):
    return issue_cutover_approval(
        inspect_queue_cutover(conn), operator_id="operator-1",
        change_ticket="review-001", signing_secret=_SECRET,
        issued_at=ts, lifetime_seconds=100,
    )


def _activate(conn: sqlite3.Connection, signed, *, now: int | None = None):
    # Activation checks actual clock; tests for acceptance use real-time
    # approvals, while direct verification tests use controlled timestamps.
    activate_runtime_protocol_fence(
        conn, approval=signed, trusted_operator_keys=_KEYS,
        drained_legacy_runtimes=True,
    )


def test_w08_inventory_read_only_and_stable(tmp_path):
    with closing(_db(tmp_path)) as conn:
        first = inspect_queue_cutover(conn)
        second = inspect_queue_cutover(conn)
        assert first == second
        assert first.task_count == first.receipt_count == first.plan_count == 0
        assert first.processing_count == first.active_leases == 0
        assert not conn.in_transaction
        assert conn.execute(
            "SELECT 1 FROM sqlite_master WHERE name='g3_runtime_protocol_fence'"
        ).fetchone() is None


def test_w08_inventory_covers_task_state_and_receipt_content(tmp_path):
    with closing(_db(tmp_path)) as conn:
        initial = inspect_queue_cutover(conn)
        conn.execute(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,task_state,created_at,updated_at) "
            "VALUES ('t','d','h','n','G3_EXTERNAL_UNKNOWN',1,1)"
        )
        conn.commit()
        amended = inspect_queue_cutover(conn)
        assert amended.inventory_sha256 != initial.inventory_sha256
        assert amended.external_unknown_count == 1
        conn.execute("UPDATE chunk_tasks SET task_state='RESULT_STAGED' WHERE task_id='t'")
        conn.commit()
        staged = inspect_queue_cutover(conn)
        assert staged.inventory_sha256 != amended.inventory_sha256
        assert staged.staged_count == 1
        assert conn.execute("SELECT task_state FROM chunk_tasks").fetchone() == (
            "RESULT_STAGED",
        )


def test_w08_approval_tampering_wrong_operator_and_expiry(tmp_path):
    with closing(_db(tmp_path)) as conn:
        inventory = inspect_queue_cutover(conn)
        signature = _approve(conn)
        verify_cutover_approval(signature, inventory, trusted_operator_keys=_KEYS,
                                now=1_000_010)
        with pytest.raises(PipelineIntegrityError, match="SIGNATURE_INVALID"):
            verify_cutover_approval(
                replace(signature, change_ticket="changed"),
                inventory, trusted_operator_keys=_KEYS, now=1_000_010,
            )
        with pytest.raises(PipelineIntegrityError, match="OPERATOR_NOT_TRUSTED"):
            verify_cutover_approval(
                signature, inventory, trusted_operator_keys={},
                now=1_000_010,
            )
        with pytest.raises(PipelineIntegrityError, match="SCOPE_OR_TIME_INVALID"):
            verify_cutover_approval(
                signature, inventory, trusted_operator_keys=_KEYS,
                now=1_000_200,
            )
        with pytest.raises(PipelineIntegrityError, match="SCOPE_OR_TIME_INVALID"):
            verify_cutover_approval(
                signature, inventory, trusted_operator_keys=_KEYS,
                now=999_900,
            )


def test_w08_approval_bound_to_exact_queue_path(tmp_path):
    with closing(_db(tmp_path, "queueA.db")) as a:
        signed = _approve(a)
    with closing(_db(tmp_path, "queueB.db")) as b:
        other = inspect_queue_cutover(b)
        with pytest.raises(PipelineIntegrityError, match="SCOPE_OR_TIME_INVALID"):
            verify_cutover_approval(signed, other,
                                    trusted_operator_keys=_KEYS, now=1_000_010)


def test_w08_changed_queue_rejects_signed_activation_without_triggers(tmp_path):
    import time
    with closing(_db(tmp_path)) as conn:
        signed = issue_cutover_approval(
            inspect_queue_cutover(conn), operator_id="operator-1",
            change_ticket="ticket", signing_secret=_SECRET,
            issued_at=int(time.time()),
        )
        conn.execute(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,created_at,updated_at) "
            "VALUES ('after','d','h','n',1,1)"
        )
        conn.commit()
        with pytest.raises(PipelineIntegrityError, match="SCOPE_OR_TIME_INVALID"):
            _activate(conn, signed)
        assert conn.execute(
            "SELECT 1 FROM sqlite_master WHERE name='g3_runtime_protocol_fence'"
        ).fetchone() is None
        assert conn.execute("SELECT task_id FROM chunk_tasks").fetchone() == ("after",)


def test_w08_approval_rejected_without_current_runtime_protocol(tmp_path):
    import time
    with closing(_db(tmp_path)) as conn:
        signed = issue_cutover_approval(
            inspect_queue_cutover(conn), operator_id="operator-1",
            change_ticket="ticket", signing_secret=_SECRET,
            issued_at=int(time.time()),
        )
        conn.create_function("w08_runtime_protocol", 0, lambda: None)
        with pytest.raises(PipelineIntegrityError, match="INCOMPATIBLE"):
            _activate(conn, signed)


def test_w08_approval_invalid_signature_rolls_back_completely(tmp_path):
    import time
    with closing(_db(tmp_path)) as conn:
        signed = issue_cutover_approval(
            inspect_queue_cutover(conn), operator_id="operator-1",
            change_ticket="ticket", signing_secret=_SECRET,
            issued_at=int(time.time()),
        )
        with pytest.raises(PipelineIntegrityError, match="SIGNATURE_INVALID"):
            activate_runtime_protocol_fence(
                conn, approval=signed,
                trusted_operator_keys={"operator-1": b"incorrect-secret-but-length-is-greater-than-32"},
                drained_legacy_runtimes=True,
            )
        assert not conn.in_transaction
        assert conn.execute(
            "SELECT 1 FROM sqlite_master WHERE name='g3_runtime_protocol_fence'"
        ).fetchone() is None


def test_w08_approval_expires_before_activation(tmp_path):
    with closing(_db(tmp_path)) as conn:
        signed = _approve(conn, ts=1_000_000)
        with pytest.raises(PipelineIntegrityError, match="SCOPE_OR_TIME_INVALID"):
            _activate(conn, signed)
        assert conn.execute(
            "SELECT 1 FROM sqlite_master WHERE name='g3_runtime_protocol_fence'"
        ).fetchone() is None


def test_w08_activation_forbids_live_task_lease_even_if_not_processing(tmp_path):
    import time
    with closing(_db(tmp_path)) as conn:
        conn.execute(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,task_state,lease_owner,"
            "lease_expires_at,created_at,updated_at) "
            "VALUES ('t','d','h','n','PENDING','old-worker',?,1,1)",
            (time.time() + 600,),
        )
        conn.commit()
        inventory = inspect_queue_cutover(conn)
        assert inventory.processing_count == 0
        assert inventory.active_task_leases == 1
        signed = issue_cutover_approval(
            inventory, operator_id="operator-1",
            change_ticket="ticket", signing_secret=_SECRET,
            issued_at=int(time.time()),
        )
        with pytest.raises(PipelineIntegrityError, match="ACTIVE_LEASES"):
            _activate(conn, signed)
        assert conn.execute(
            "SELECT lease_owner,task_state FROM chunk_tasks WHERE task_id='t'"
        ).fetchone() == ("old-worker", "PENDING")
        assert conn.execute(
            "SELECT 1 FROM sqlite_master WHERE name='g3_runtime_protocol_fence'"
        ).fetchone() is None


def test_w08_activation_forbids_nonzero_active_global_lease(tmp_path):
    import time
    with closing(_db(tmp_path)) as conn:
        conn.execute(
            "UPDATE system_leases SET owner_id='legacy-reconciler',"
            "lease_expires_at=? WHERE lease_name='global_reconciler'",
            (time.time() + 600,),
        )
        conn.commit()
        signed = issue_cutover_approval(
            inspect_queue_cutover(conn), operator_id="operator-1",
            change_ticket="ticket", signing_secret=_SECRET,
            issued_at=int(time.time()),
        )
        with pytest.raises(PipelineIntegrityError, match="ACTIVE_LEASES"):
            _activate(conn, signed)
        assert conn.execute(
            "SELECT owner_id FROM system_leases WHERE lease_name='global_reconciler'"
        ).fetchone() == ("legacy-reconciler",)
        assert conn.execute(
            "SELECT 1 FROM sqlite_master WHERE name='g3_runtime_protocol_fence'"
        ).fetchone() is None
