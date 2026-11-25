"""PPPR 5.1.2 / GAP-0.5-03: composed sweeper has no logical authority.

Use real schema files, WAL, the existing connection factory and independent
observations. These are local synthetic states, not live-provider receipts.
"""
from contextlib import closing
import logging
from pathlib import Path
import sqlite3
import time

import pytest

from infra.db import connection
from runtime import sweeper

ROOT = Path(__file__).resolve().parents[2]
PLANES = {
    "FSM_DB_PATH": ("fsm.db", "schema_fsm.sql"),
    "QUEUE_DB_PATH": ("queue.db", "schema_queue.sql"),
    "EVENT_DB_PATH": ("event.db", "schema_event.sql"),
    "MAT_DB_PATH": ("materialized.db", "schema_materialized.sql"),
}


@pytest.fixture
def planes(tmp_path, monkeypatch):
    paths = {}
    for setting, (name, ddl) in PLANES.items():
        path = tmp_path / name
        monkeypatch.setattr(sweeper, setting, str(path))
        monkeypatch.setenv(setting, str(path))
        with closing(sqlite3.connect(path)) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript((ROOT / "infra/db" / ddl).read_text(encoding="utf-8"))
        paths[name] = path
    return paths


def _dump(path):
    with closing(sqlite3.connect(path)) as db:
        return tuple(db.iterdump())


@pytest.mark.integration
def test_sweeper_preserves_aged_fsm_claims_receipts_and_quarantine(
    planes, monkeypatch, caplog,
):
    now = time.time()
    old = now - 7200
    cases = (
        ("parsing", "PARSING", None),
        ("active", "PROCESSING", None),
        ("expired", "PROCESSING", None),
        ("receipt", "PROCESSING", None),
        ("unknown", "STALLED", "PROCESSING"),
        ("ready", "READY_FOR_ASSEMBLY", None),
        ("assembly", "ASSEMBLING", None),
        ("complete", "COMPLETED", None),
    )
    with closing(sqlite3.connect(planes["fsm.db"])) as fsm, fsm:
        fsm.executemany(
            "INSERT INTO document_fsm "
            "(document_id,ast_hash,current_state,state_version,updated_at,"
            "suspended_state,failure_reason,is_terminal) VALUES (?,?,?,?,?,?,?,?)",
            [(doc, "ast", state, 7, old, suspended,
              "G3_EXTERNAL_UNKNOWN" if doc == "unknown" else None,
              int(state == "COMPLETED")) for doc, state, suspended in cases],
        )
    with closing(sqlite3.connect(planes["queue.db"])) as queue, queue:
        queue.executemany(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,task_state,worker_type,"
            "execution_id,lease_owner,lease_expires_at,created_at,updated_at,state_version)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                (doc, doc, "ast", "chunk", state, worker, "execution", "owner",
                 expiry, old, old, 4)
                for doc, state, worker, expiry in (
                    ("active", "PROCESSING", "LLM", now + 600),
                    ("expired", "PROCESSING", "LLM", old),
                    ("receipt", "RESULT_STAGED", "LLM", old),
                    ("unknown", "G3_EXTERNAL_UNKNOWN", "LLM", old),
                    ("assembly", "PROCESSING", "ASSEMBLER", now + 600),
                )
            ],
        )
        queue.execute(
            "INSERT INTO chunk_result_receipts "
            "(document_id,ast_hash,chunk_id,task_id,execution_id,created_at)"
            " VALUES ('receipt','ast','chunk','receipt','execution',?)",
            (old,),
        )
        queue.execute(
            "UPDATE system_leases SET owner_id='reconciler',"
            "lease_version=3,lease_expires_at=? WHERE lease_name='global_reconciler'",
            (now + 600,),
        )
    before = {name: _dump(path) for name, path in planes.items()}
    opened = []

    def record(db_path, timeout=15):
        db = connection.get_connection(db_path, timeout=timeout)
        opened.append(db)
        return db

    monkeypatch.setattr(sweeper, "get_connection", record)
    with caplog.at_level(logging.INFO, logger=sweeper.__name__):
        sweeper.RecoveryDaemon().run_sweep_cycle()
        sweeper.RecoveryDaemon().run_sweep_cycle()

    assert {name: _dump(path) for name, path in planes.items()} == before
    assert len(opened) == 8
    for db in opened:
        with pytest.raises(sqlite3.ProgrammingError, match="closed"):
            db.execute("SELECT 1")
    assert caplog.text.count("SWEEPER_WAL_CHECKPOINT_OK") == 8
    assert "SWEEPER_ABORTED" not in caplog.text
    assert "SWEEPER_PERMANENT_FAILURE" not in caplog.text


@pytest.mark.integration
def test_missing_plane_is_reported_without_bootstrapping(planes, caplog):
    missing = planes["event.db"]
    missing.unlink()
    before = {name: _dump(path) for name, path in planes.items() if path.exists()}
    with caplog.at_level(logging.INFO, logger=sweeper.__name__):
        sweeper.RecoveryDaemon().run_sweep_cycle()
    assert not missing.exists()
    assert caplog.text.count("SWEEPER_WAL_CHECKPOINT_OK") == 3
    assert "SWEEPER_WAL_PLANE_MISSING plane=Event Plane" in caplog.text
    assert {name: _dump(path) for name, path in planes.items() if path.exists()} == before
