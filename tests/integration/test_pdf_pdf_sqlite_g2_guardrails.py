"""G2: guardarrailes de persistencia FSM y propiedad del alias SQLite.

Ejecucion separada de los dos tests G1 originales (que NO se editan).
Todos los ficheros SQLite residen en pytest.tmp_path; sin Docker ni proveedor.
No establece consistencia atomica entre FSM y queue ni certifica PDF->PDF.
"""
from pathlib import Path
from contextlib import closing
import sqlite3

import pytest

from core.execution.exceptions import OptimisticLockError
from core.execution.handlers import DocumentCommandHandler
from core.execution.state import StartParsingCommand, StartProcessingCommand
from infra.db.connection import ensure_fsm_database_attached, get_connection
from infra.db.control_repo import ControlPlaneRepository
from infra.db.fsm_repository import FSMRepository

ROOT = Path(__file__).resolve().parents[2]
DOC = "g2_doc"
AST = "g2_ast"


@pytest.fixture
def sqlite_planes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    fsm_db, queue_db = tmp_path / "fsm.db", tmp_path / "queue.db"
    for path, schema_name in (
        (fsm_db, "infra/db/schema_fsm.sql"),
        (queue_db, "infra/db/schema_queue.sql"),
    ):
        with closing(sqlite3.connect(path)) as conn:
            conn.executescript((ROOT / schema_name).read_text(encoding="utf-8"))
            conn.commit()
    monkeypatch.setenv("FSM_DB_PATH", str(fsm_db))
    monkeypatch.setenv("QUEUE_DB_PATH", str(queue_db))
    return fsm_db, queue_db


def _status(fsm_db: Path):
    with closing(sqlite3.connect(fsm_db)) as conn:
        return conn.execute(
            "SELECT current_state, state_version FROM document_fsm WHERE document_id=? AND ast_hash=?",
            (DOC, AST),
        ).fetchone()


def _processing(fsm_db: Path):
    with closing(get_connection(str(fsm_db))) as conn:
        repository = FSMRepository(conn)
        repository.initialize_document(DOC, AST)
        handler = DocumentCommandHandler(repository)
        v1 = handler.handle(StartParsingCommand(DOC, AST, "g2_owner", 0))
        handler.handle(StartProcessingCommand(DOC, AST, "g2_owner", v1))


def test_initialize_is_durable_without_caller_commit(sqlite_planes: tuple[Path, Path]) -> None:
    fsm_db, _ = sqlite_planes
    conn = get_connection(str(fsm_db))
    try:
        FSMRepository(conn).initialize_document(DOC, AST)
        assert not conn.in_transaction, "La operacion local FSM quedo sin commit"
    finally:
        conn.close()
    assert _status(fsm_db) == ("CREATED", 0)


def test_each_fsm_command_is_durable_on_separate_reopen(sqlite_planes: tuple[Path, Path]) -> None:
    fsm_db, _ = sqlite_planes
    with closing(get_connection(str(fsm_db))) as conn:
        FSMRepository(conn).initialize_document(DOC, AST)
    assert _status(fsm_db) == ("CREATED", 0)

    with closing(get_connection(str(fsm_db))) as conn:
        v = DocumentCommandHandler(FSMRepository(conn)).handle(
            StartParsingCommand(DOC, AST, "g2_owner", 0)
        )
        assert v == 1
    assert _status(fsm_db) == ("PARSING", 1)

    with closing(get_connection(str(fsm_db))) as conn:
        v = DocumentCommandHandler(FSMRepository(conn)).handle(
            StartProcessingCommand(DOC, AST, "g2_owner", 1)
        )
        assert v == 2
    assert _status(fsm_db) == ("PROCESSING", 2)


def test_wrong_cas_rolls_back_without_state_mutation(sqlite_planes: tuple[Path, Path]) -> None:
    fsm_db, _ = sqlite_planes
    _processing(fsm_db)
    conn = get_connection(str(fsm_db))
    try:
        with pytest.raises(OptimisticLockError):
            FSMRepository(conn).transition_to(
                DOC, AST, "PROCESSING", "READY_FOR_ASSEMBLY", 0, "g2_owner"
            )
        assert not conn.in_transaction
    finally:
        conn.close()
    assert _status(fsm_db) == ("PROCESSING", 2)


def test_scheduler_repeated_queries_do_not_detach_factory_alias(sqlite_planes: tuple[Path, Path]) -> None:
    fsm_db, queue_db = sqlite_planes
    _processing(fsm_db)
    conn = get_connection(str(queue_db))
    try:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_tasks(DOC, AST, ["task_node"])
        names_before = {entry[1]: entry[2] for entry in conn.execute("PRAGMA database_list")}
        assert "fsm_db" in names_before
        assert repo.find_documents_with_pending_chunks() == [(DOC, AST)]
        assert repo.find_documents_with_pending_chunks() == [(DOC, AST)]
        names_after = {entry[1]: entry[2] for entry in conn.execute("PRAGMA database_list")}
        assert names_after["fsm_db"] == names_before["fsm_db"]
    finally:
        conn.close()


def test_existing_alias_to_wrong_fsm_fails_closed(sqlite_planes: tuple[Path, Path], tmp_path: Path) -> None:
    _fsm_db, queue_db = sqlite_planes
    other_db = tmp_path / "other_fsm.db"
    with closing(sqlite3.connect(other_db)) as conn:
        conn.execute("CREATE TABLE marker (x TEXT)")
    with closing(sqlite3.connect(queue_db)) as conn:
        conn.execute("ATTACH DATABASE ? AS fsm_db", (str(other_db),))
        before = {x[1]: x[2] for x in conn.execute("PRAGMA database_list")}
        with pytest.raises(sqlite3.OperationalError, match="Alias fsm_db apunta a otra base"):
            ControlPlaneRepository(conn).find_documents_with_pending_chunks()
        after = {x[1]: x[2] for x in conn.execute("PRAGMA database_list")}
        assert after["fsm_db"] == before["fsm_db"]


def test_unprepared_connection_attaches_once_and_keeps_alias(sqlite_planes: tuple[Path, Path]) -> None:
    fsm_db, queue_db = sqlite_planes
    _processing(fsm_db)
    with closing(sqlite3.connect(queue_db)) as conn:
        repo = ControlPlaneRepository(conn)
        repo.enqueue_tasks(DOC, AST, ["task_node"])
        assert "fsm_db" not in {x[1] for x in conn.execute("PRAGMA database_list")}
        assert repo.find_documents_with_pending_chunks() == [(DOC, AST)]
        assert repo.find_documents_with_pending_chunks() == [(DOC, AST)]
        names = {x[1] for x in conn.execute("PRAGMA database_list")}
        assert "fsm_db" in names


def test_absent_fsm_rejected_without_creating_database(sqlite_planes: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _fsm_db, queue_db = sqlite_planes
    missing_db = tmp_path / "missing" / "fsm.db"
    monkeypatch.setenv("FSM_DB_PATH", str(missing_db))
    with closing(sqlite3.connect(queue_db)) as conn:
        with pytest.raises(FileNotFoundError, match="Base FSM ausente"):
            ensure_fsm_database_attached(conn)
        assert "fsm_db" not in {x[1] for x in conn.execute("PRAGMA database_list")}
        assert not missing_db.exists()
