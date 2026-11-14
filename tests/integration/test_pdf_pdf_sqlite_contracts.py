"""D2-11/07: regresiones previas a cualquier correccion funcional PDF->PDF.

Ejecutar SOLO en el worktree correctivo, bajo tests/integration/.
Dos pruebas deben FALLAR sobre a308ca7; NO son una prueba E2E.
DB y datos temporales aislados mediante pytest.tmp_path y monkeypatch.

Basado en los contratos AS-IS de:
  apps/ocr_router/__main__.py
  infra/db/fsm_repository.py
  infra/db/control_repo.py
  infra/db/connection.py
No introduce nuevos contratos sobre chunk_id/node_id ni selecciona ejecutor.
"""
from pathlib import Path
import sqlite3

import pytest

from core.execution.handlers import DocumentCommandHandler
from core.execution.state import StartParsingCommand, StartProcessingCommand
from infra.db.connection import get_connection
from infra.db.control_repo import ControlPlaneRepository
from infra.db.fsm_repository import FSMRepository


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def sqlite_planes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """Replica los esquemas, pero nunca toca infra/db/*.db del checkout."""
    fsm_db = tmp_path / "fsm.db"
    queue_db = tmp_path / "queue.db"

    for db_path, schema in (
        (fsm_db, "infra/db/schema_fsm.sql"),
        (queue_db, "infra/db/schema_queue.sql"),
    ):
        conn = sqlite3.connect(db_path)
        try:
            conn.executescript((REPO_ROOT / schema).read_text(encoding="utf-8"))
            conn.commit()
        finally:
            conn.close()

    monkeypatch.setenv("FSM_DB_PATH", str(fsm_db))
    monkeypatch.setenv("QUEUE_DB_PATH", str(queue_db))
    return fsm_db, queue_db


def _transition_to_processing(fsm_repo: FSMRepository, queue_repo: ControlPlaneRepository) -> None:
    """Secuencia operativa equivalente a la del OCR Router, sin parsear un PDF."""
    document_id = "d2_11_contract_doc"
    ast_hash = "d2_11_contract_ast"
    owner_id = "d2_11_test_owner"
    handler = DocumentCommandHandler(fsm_repo, task_repo=queue_repo)

    fsm_repo.initialize_document(document_id, ast_hash)
    current = fsm_repo.get_status(document_id, ast_hash)
    assert current is not None, "Ni la inicializacion es visible en la misma conexion FSM"

    next_version = handler.handle(
        StartParsingCommand(document_id, ast_hash, owner_id, current.state_version)
    )
    queue_repo.enqueue_tasks(document_id, ast_hash, ["chunk_a", "chunk_b"])
    handler.handle(StartProcessingCommand(document_id, ast_hash, owner_id, next_version))
    current = fsm_repo.get_status(document_id, ast_hash)
    assert current is not None and current.current_state == "PROCESSING"


def test_ocr_handoff_fsm_is_durable_when_connections_close(sqlite_planes: tuple[Path, Path]) -> None:
    """La cola durable no debe apuntar a una generacion FSM perdida al cerrar conexiones."""
    fsm_db, queue_db = sqlite_planes
    fsm_conn = get_connection(str(fsm_db), timeout=5)
    queue_conn = get_connection(str(queue_db), timeout=5)
    try:
        _transition_to_processing(
            FSMRepository(fsm_conn), ControlPlaneRepository(queue_conn)
        )
    finally:
        queue_conn.close()
        fsm_conn.close()

    with sqlite3.connect(queue_db) as check_queue:
        persisted_tasks = check_queue.execute(
            "SELECT COUNT(*) FROM chunk_tasks WHERE document_id = ? AND ast_hash = ?",
            ("d2_11_contract_doc", "d2_11_contract_ast"),
        ).fetchone()[0]

    with sqlite3.connect(fsm_db) as check_fsm:
        persisted_fsm = check_fsm.execute(
            "SELECT current_state FROM document_fsm WHERE document_id = ? AND ast_hash = ?",
            ("d2_11_contract_doc", "d2_11_contract_ast"),
        ).fetchone()

    assert persisted_tasks == 2, "No se reprodujo el handoff de 2 tareas a la cola"
    assert persisted_fsm == ("PROCESSING",), (
        "BRECHA FSM/cola: tareas persistidas sin FSM PROCESSING durable "
        f"(valor observado: {persisted_fsm!r})"
    )


def test_scheduler_reuses_attached_fsm_database(sqlite_planes: tuple[Path, Path]) -> None:
    """Una conexion queue con fsm_db preadjunta debe poder consultar el scheduler."""
    fsm_db, queue_db = sqlite_planes

    # Este test aísla el scheduler: el fixture persiste FSM explícitamente
    # para no confundir este defecto con la falta de commit del test anterior.
    fsm_conn = get_connection(str(fsm_db), timeout=5)
    try:
        fsm_repo = FSMRepository(fsm_conn)
        fsm_repo.initialize_document("d2_11_contract_doc", "d2_11_contract_ast")
        handler = DocumentCommandHandler(fsm_repo)
        v = handler.handle(
            StartParsingCommand("d2_11_contract_doc", "d2_11_contract_ast", "owner", 0)
        )
        handler.handle(
            StartProcessingCommand("d2_11_contract_doc", "d2_11_contract_ast", "owner", v)
        )
        fsm_conn.commit()  # SOLO preparacion del test, no arreglo de produccion
    finally:
        fsm_conn.close()

    queue_conn = get_connection(str(queue_db), timeout=5)
    try:
        repository = ControlPlaneRepository(queue_conn)
        repository.enqueue_tasks("d2_11_contract_doc", "d2_11_contract_ast", ["chunk_a"])
        attached_names = {row[1] for row in queue_conn.execute("PRAGMA database_list")}
        assert "fsm_db" in attached_names, "Precondicion fallida: get_connection no adjunto FSM"

        # En a308ca7 este metodo intenta ATTACH fsm_db por segunda vez.
        result = repository.find_documents_with_pending_chunks(sample_size=10)
        assert ("d2_11_contract_doc", "d2_11_contract_ast") in result
    finally:
        queue_conn.close()
