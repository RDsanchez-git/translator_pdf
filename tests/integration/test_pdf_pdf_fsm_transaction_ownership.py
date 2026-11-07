"""D2-11 / G2: characterization of transaction ownership in FSMRepository.

Run from the root of the corrective worktree after copying this file to
``tests/integration/test_pdf_pdf_fsm_transaction_ownership.py``.

This does NOT assert cross-database atomicity. All writes are made to a disposable
SQLite database supplied by pytest.tmp_path. No application daemons are launched.

The tests express a proposed guardrail: a repository call must not commit or
rollback an already active, caller-owned transaction. The current G2 candidate
may fail these tests. Such a failure requires transaction-boundary design
review, not weakening the test just to achieve green.
"""

from pathlib import Path
import sqlite3

import pytest

from core.execution.exceptions import OptimisticLockError
from infra.db.fsm_repository import FSMRepository


ROOT = Path(__file__).resolve().parents[2]
DOC = "g2_transaction_owner_doc"
AST = "g2_transaction_owner_ast"


@pytest.fixture
def fsm_connection(tmp_path: Path):
    path = tmp_path / "fsm.db"
    conn = sqlite3.connect(path)
    try:
        schema = (ROOT / "infra/db/schema_fsm.sql").read_text(encoding="utf-8")
        conn.executescript(schema)
        conn.execute("CREATE TABLE caller_marker (id TEXT PRIMARY KEY)")
        conn.commit()
        yield conn, path
    finally:
        if conn.in_transaction:
            conn.rollback()
        conn.close()


def _marker_count(path: Path) -> int:
    with sqlite3.connect(path) as reader:
        return reader.execute("SELECT COUNT(*) FROM caller_marker").fetchone()[0]


def _fsm_state(path: Path):
    with sqlite3.connect(path) as reader:
        return reader.execute(
            "SELECT current_state FROM document_fsm WHERE document_id = ? AND ast_hash = ?",
            (DOC, AST),
        ).fetchone()


def test_initialize_does_not_commit_outer_transaction(fsm_connection) -> None:
    """Caller rollback must undo its own write AND an FSM initialization."""
    conn, path = fsm_connection
    repo = FSMRepository(conn)

    conn.execute("BEGIN")
    conn.execute("INSERT INTO caller_marker (id) VALUES ('before_initialize')")
    repo.initialize_document(DOC, AST)
    transaction_still_open = conn.in_transaction
    conn.rollback()

    assert transaction_still_open, "FSM initialization committed the caller's transaction"
    assert _marker_count(path) == 0, "Unrelated caller write was prematurely committed"
    assert _fsm_state(path) is None, "FSM initialization escaped caller rollback"


def test_transition_does_not_commit_outer_transaction(fsm_connection) -> None:
    """A successful CAS update must remain reversible by the caller."""
    conn, path = fsm_connection
    repo = FSMRepository(conn)
    repo.initialize_document(DOC, AST)  # Standalone setup, already durable in G2.

    conn.execute("BEGIN")
    conn.execute("INSERT INTO caller_marker (id) VALUES ('before_transition')")
    repo.transition_to(DOC, AST, "CREATED", "PARSING", 0, "g2_test_owner")
    transaction_still_open = conn.in_transaction
    conn.rollback()

    assert transaction_still_open, "Successful FSM transition committed caller transaction"
    assert _marker_count(path) == 0, "Unrelated caller write was prematurely committed"
    assert _fsm_state(path) == ("CREATED",), "CAS transition escaped caller rollback"


def test_failed_cas_does_not_rollback_outer_transaction(fsm_connection) -> None:
    """A failed CAS must not roll back unrelated caller work."""
    conn, path = fsm_connection
    repo = FSMRepository(conn)
    repo.initialize_document(DOC, AST)

    conn.execute("BEGIN")
    conn.execute("INSERT INTO caller_marker (id) VALUES ('caller_work_to_keep')")
    with pytest.raises(OptimisticLockError):
        repo.transition_to(DOC, AST, "CREATED", "PARSING", 999, "g2_test_owner")
    transaction_still_open = conn.in_transaction
    conn.commit()

    assert transaction_still_open, "Failed FSM CAS rolled back caller transaction"
    assert _marker_count(path) == 1, "Failed FSM CAS discarded unrelated caller work"
    assert _fsm_state(path) == ("CREATED",), "Failed CAS changed persisted FSM state"
