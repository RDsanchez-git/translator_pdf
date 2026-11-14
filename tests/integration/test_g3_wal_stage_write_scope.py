"""Regression for G3 WAL stage write scope (no provider, Docker or host state)."""

import sqlite3
import threading
from queue import Queue

import pytest

from infra.db.control_repo import ControlPlaneRepository


def _connection(path, *, timeout=0.25):
    conn = sqlite3.connect(path, timeout=timeout)
    conn.execute(f"PRAGMA busy_timeout={int(timeout * 1000)}")
    return conn


@pytest.fixture
def wal_db(tmp_path):
    path = tmp_path / "queue.db"
    conn = _connection(path)
    assert conn.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
    conn.executescript(
        "CREATE TABLE competing_writer (k INTEGER PRIMARY KEY, v INTEGER NOT NULL);"
        "INSERT INTO competing_writer VALUES (1, 0);"
        "CREATE TABLE staged_result (k INTEGER PRIMARY KEY, v TEXT NOT NULL);"
    )
    conn.close()
    return path


def test_staging_write_scope_reserves_wal_writer_before_snapshot(wal_db):
    """HEAD fails SQLITE_BUSY_SNAPSHOT here; patched scope must commit one insert."""
    conn = _connection(wal_db)
    repo = ControlPlaneRepository(conn)
    outcomes = Queue()

    def competitor():
        other = _connection(wal_db)
        try:
            other.execute("UPDATE competing_writer SET v=1 WHERE k=1")
            other.commit()
            outcomes.put(("committed", None))
        except sqlite3.OperationalError as exc:
            other.rollback()
            outcomes.put(("blocked", exc.sqlite_errorcode))
        finally:
            other.close()

    worker = threading.Thread(target=competitor, name="competing-sqlite-writer")
    try:
        with repo._chunk_plan_write_scope():
            assert conn.execute("SELECT v FROM competing_writer WHERE k=1").fetchone() == (0,)
            worker.start()
            worker.join(timeout=3)
            assert not worker.is_alive(), "Competing SQLite writer did not finish"
            status, code = outcomes.get_nowait()
            assert status == "blocked" and code == sqlite3.SQLITE_BUSY, (status, code)
            conn.execute("INSERT INTO staged_result VALUES (1, 'receipt')")
        assert not conn.in_transaction
        assert conn.execute("SELECT COUNT(*) FROM staged_result").fetchone()[0] == 1
        assert conn.execute("SELECT v FROM competing_writer WHERE k=1").fetchone() == (0,)
    finally:
        if conn.in_transaction:
            conn.rollback()
        worker.join(timeout=3) if worker.ident is not None else None
        conn.close()


def test_existing_caller_transaction_remains_caller_owned(wal_db):
    conn = _connection(wal_db)
    try:
        repo = ControlPlaneRepository(conn)
        conn.execute("BEGIN IMMEDIATE")
        with repo._chunk_plan_write_scope():
            conn.execute("INSERT INTO staged_result VALUES (1, 'uncommitted')")
        assert conn.in_transaction
        assert conn.execute("SELECT COUNT(*) FROM staged_result").fetchone()[0] == 1
        conn.rollback()
        assert conn.execute("SELECT COUNT(*) FROM staged_result").fetchone()[0] == 0
        assert not conn.in_transaction
    finally:
        conn.close()


def test_nested_and_owned_write_scopes_rollback_on_exception(wal_db):
    conn = _connection(wal_db)
    try:
        repo = ControlPlaneRepository(conn)
        conn.execute("BEGIN IMMEDIATE")
        with pytest.raises(RuntimeError, match="nested-failure"):
            with repo._chunk_plan_write_scope():
                conn.execute("INSERT INTO staged_result VALUES (1, 'nested')")
                raise RuntimeError("nested-failure")
        assert conn.in_transaction
        assert conn.execute("SELECT COUNT(*) FROM staged_result").fetchone()[0] == 0
        conn.rollback()
        with pytest.raises(RuntimeError, match="owned-failure"):
            with repo._chunk_plan_write_scope():
                conn.execute("INSERT INTO staged_result VALUES (2, 'owned')")
                raise RuntimeError("owned-failure")
        assert not conn.in_transaction
        assert conn.execute("SELECT COUNT(*) FROM staged_result").fetchone()[0] == 0
    finally:
        conn.close()
