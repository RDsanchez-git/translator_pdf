"""W08-2d: disposable SQLite capability fence witnesses, no Docker/network."""
from contextlib import closing
from pathlib import Path
import sqlite3

import pytest

from core.execution.exceptions import PipelineIntegrityError
from infra.db.connection import get_connection
from infra.db.runtime_protocol_fence import (
    activate_runtime_protocol_fence, bind_runtime_protocol,
    verify_runtime_protocol,
)


ROOT = Path(__file__).resolve().parents[2]


def _queue(path: Path, *, current: bool = False) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    if current:
        bind_runtime_protocol(conn)
    return conn


def _setup(tmp_path: Path) -> Path:
    path = tmp_path / "queue.db"
    with closing(_queue(path)) as conn:
        conn.executescript(
            (ROOT / "infra/db/schema_queue.sql").read_text(encoding="utf8")
        )
    return path


def _activate(conn: sqlite3.Connection, *, operator: str = "reviewer",
              ticket: str = "W08-CHANGE-001") -> None:
    activate_runtime_protocol_fence(
        conn, operator_id=operator, change_ticket=ticket,
        drained_legacy_runtimes=True,
    )


def test_w08_fence_legacy_writes_blocked_and_new_writes_allowed(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path, current=True)) as new:
        _activate(new)
        verify_runtime_protocol(new)
        new.execute(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,created_at,updated_at) "
            "VALUES ('task1','doc','hash','chunk',1,1)"
        )
        new.commit()
        new.execute("UPDATE chunk_tasks SET task_state='COMPLETED' WHERE task_id='task1'")
        new.commit()

    with closing(_queue(path)) as old:
        with pytest.raises(PipelineIntegrityError, match="NOT_REGISTERED"):
            verify_runtime_protocol(old)
        for sql in (
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,created_at,updated_at) "
            "VALUES ('task2','doc','hash','chunk2',1,1)",
            "UPDATE chunk_tasks SET task_state='PENDING' WHERE task_id='task1'",
            "DELETE FROM chunk_tasks WHERE task_id='task1'",
            "INSERT INTO chunk_plans "
            "(document_id,ast_hash,manifest_sha256,manifest_json,created_at) "
            "VALUES ('doc','hash',?,'{}',1)",
            "INSERT INTO chunk_result_receipts "
            "(document_id,ast_hash,chunk_id,task_id,execution_id,created_at) "
            "VALUES ('doc','hash','chunk','task1','ex',1)",
        ):
            try:
                with pytest.raises(sqlite3.OperationalError, match="no such function"):
                    if "manifest_sha256" in sql:
                        old.execute(sql, ("a" * 64,))
                    else:
                        old.execute(sql)
            finally:
                old.rollback()
        assert old.execute(
            "SELECT task_state FROM chunk_tasks WHERE task_id='task1'"
        ).fetchone() == ("COMPLETED",)
        with pytest.raises(sqlite3.OperationalError, match="no such function"):
            old.execute(
                "INSERT INTO g3_context_snapshots "
                "(document_id,ast_hash,manifest_sha256,context_id,"
                "snapshot_sha256,snapshot_json,created_at) "
                "VALUES ('doc','hash',?,'CTX_x',?,'{}',1)",
                ("a" * 64, "b" * 64),
            )


def test_w08_fence_not_installed_by_default(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path)) as old:
        old.execute(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,created_at,updated_at) "
            "VALUES ('legacy','doc','h','chunk',1,1)"
        )
        old.commit()
        assert old.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type='trigger' AND name LIKE 'g3_w08_fence_%'"
        ).fetchone() == (0,)


def test_w08_fence_refuses_active_claim_without_writing_ddl(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path, current=True)) as conn:
        conn.execute(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,task_state,created_at,updated_at) "
            "VALUES ('t','doc','h','c','PROCESSING',1,1)"
        )
        conn.commit()
        with pytest.raises(PipelineIntegrityError, match="ACTIVE_CLAIMS"):
            _activate(conn)
        assert conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name='g3_runtime_protocol_fence'"
        ).fetchone() == (0,)
        assert conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' "
            "AND name LIKE 'g3_w08_fence_%'"
        ).fetchone() == (0,)


def test_w08_fence_rejects_unapproved_and_caller_transaction(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path, current=True)) as conn:
        with pytest.raises(PipelineIntegrityError, match="ACTIVATION_NOT_AUTHORIZED"):
            activate_runtime_protocol_fence(
                conn, operator_id="reviewer", change_ticket="ticket",
                drained_legacy_runtimes=False,
            )
        conn.execute("BEGIN")
        with pytest.raises(PipelineIntegrityError, match="ACTIVE_TRANSACTION"):
            _activate(conn)
        conn.rollback()


def test_w08_fence_activation_is_idempotent_and_audited(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path, current=True)) as conn:
        _activate(conn)
        record = conn.execute(
            "SELECT required_protocol,operator_id,change_ticket,activated_at "
            "FROM g3_runtime_protocol_fence"
        ).fetchone()
        assert record[:3] == ("w08-context-durable-v1", "reviewer", "W08-CHANGE-001")
        assert record[3] > 0
        _activate(conn)
        assert conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' "
            "AND name LIKE 'g3_w08_fence_%'"
        ).fetchone() == (15,)
        with pytest.raises(PipelineIntegrityError, match="ACTIVATION_CONFLICT"):
            _activate(conn, ticket="W08-DIFFERENT")
        assert conn.execute(
            "SELECT operator_id,change_ticket FROM g3_runtime_protocol_fence"
        ).fetchone() == ("reviewer", "W08-CHANGE-001")


def test_w08_old_writer_cannot_edit_operator_record(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path, current=True)) as current:
        _activate(current)
    with closing(_queue(path)) as old:
        with pytest.raises(sqlite3.OperationalError, match="no such function"):
            old.execute(
                "UPDATE g3_runtime_protocol_fence SET operator_id='forged' "
                "WHERE slot=1"
            )
        old.rollback()
    with closing(_queue(path, current=True)) as reopened:
        verify_runtime_protocol(reopened)
        assert reopened.execute(
            "SELECT operator_id FROM g3_runtime_protocol_fence WHERE slot=1"
        ).fetchone() == ("reviewer",)


@pytest.mark.parametrize("invalid", [None, "", "w08-incompatible-v0"])
def test_w08_invalid_protocol_function_cannot_write(tmp_path, invalid):
    path = _setup(tmp_path)
    with closing(_queue(path, current=True)) as current:
        _activate(current)
    with closing(_queue(path)) as incompatible:
        incompatible.create_function("w08_runtime_protocol", 0, lambda: invalid)
        with pytest.raises(sqlite3.IntegrityError, match="W08_RUNTIME_PROTOCOL_INCOMPATIBLE"):
            incompatible.execute(
                "INSERT INTO chunk_tasks "
                "(task_id,document_id,ast_hash,node_id,created_at,updated_at) "
                "VALUES ('new','doc','hash','chunk',1,1)"
            )
        incompatible.rollback()
        assert incompatible.execute(
            "SELECT COUNT(*) FROM chunk_tasks WHERE task_id='new'"
        ).fetchone() == (0,)


def test_w08_activation_requires_current_runtime_capability(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path)) as legacy:
        with pytest.raises(PipelineIntegrityError, match="NOT_REGISTERED"):
            _activate(legacy)
        assert legacy.execute(
            "SELECT 1 FROM sqlite_master WHERE name='g3_runtime_protocol_fence'"
        ).fetchone() is None


def test_w08_missing_trigger_blocks_current_runtime_startup(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path, current=True)) as current:
        _activate(current)
        # DDL-capable actors can defeat the fence; the *new* runtime must at
        # least notice tampering and fail closed rather than silently proceed.
        current.execute("DROP TRIGGER g3_w08_fence_chunk_tasks_insert")
        current.commit()
        with pytest.raises(PipelineIntegrityError, match="TRIGGERS_INCOMPLETE"):
            verify_runtime_protocol(current)


def test_w08_new_connection_factory_registers_capability(tmp_path, monkeypatch):
    path = _setup(tmp_path)
    monkeypatch.setenv("SQLITE_STATE_DIR", str(tmp_path))
    with closing(_queue(path, current=True)) as conn:
        _activate(conn)
    with closing(get_connection("infra/db/queue.db")) as current:
        verify_runtime_protocol(current)
        assert current.execute("SELECT w08_runtime_protocol()").fetchone() == (
            "w08-context-durable-v1",
        )


def test_w08_missing_guarded_table_rolls_back_activation(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path, current=True)) as conn:
        conn.execute("DROP TABLE chunk_result_receipts")
        conn.commit()
        with pytest.raises(sqlite3.OperationalError):
            _activate(conn)
        assert conn.execute(
            "SELECT 1 FROM sqlite_master WHERE name='g3_runtime_protocol_fence'"
        ).fetchone() is None
        assert conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' "
            "AND name LIKE 'g3_w08_fence_%'"
        ).fetchone() == (0,)


def test_w08_fence_no_silent_modification_of_unknown_task(tmp_path):
    path = _setup(tmp_path)
    with closing(_queue(path, current=True)) as conn:
        conn.execute(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,task_state,execution_id,"
            "error_log,created_at,updated_at) "
            "VALUES ('t','doc','h','c','G3_EXTERNAL_UNKNOWN','exec-1',"
            "'G3_W06_EXTERNAL_UNKNOWN',1,1)"
        )
        conn.commit()
        _activate(conn)
        assert conn.execute(
            "SELECT task_state,execution_id,error_log FROM chunk_tasks WHERE task_id='t'"
        ).fetchone() == (
            "G3_EXTERNAL_UNKNOWN", "exec-1", "G3_W06_EXTERNAL_UNKNOWN",
        )
