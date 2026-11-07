"""W08-2d frozen-copy auditor: no live DBs, process control or providers."""
from contextlib import closing
from pathlib import Path
import json
import sqlite3

import pytest

from core.ast.enums import ContentNodeType, HeadingLevel
from core.ast.models import ASTNode, HeadingPayload, ParagraphPayload
from core.ast.hashing import compute_ast_hash
from core.chunking.contextual_plan import prepare_contextual_plan
from core.execution.exceptions import PipelineIntegrityError
from infra.db.control_repo import ControlPlaneRepository
from infra.db.context_snapshot_repo import DurableContextPlanRepository
from infra.db.frozen_bundle_audit import audit_frozen_bundle


ROOT = Path(__file__).resolve().parents[2]
_DOC = "a" * 64


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()))


def _db(path: Path, schema: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.executescript(
        (ROOT / "infra/db" / schema).read_text(encoding="utf8")
    )
    return conn


@pytest.fixture
def frozen(tmp_path):
    with (closing(_db(tmp_path / "queue.db", "schema_queue.sql")) as queue,
          closing(_db(tmp_path / "fsm.db", "schema_fsm.sql")) as fsm,
          closing(_db(tmp_path / "materialized.db", "schema_materialized.sql"))):
        ast = [
            ASTNode(
                node_id="h1", sequence_id=1,
                node_type=ContentNodeType.HEADING,
                payload=HeadingPayload(content="Methods", heading_level=HeadingLevel.H1),
            ),
            ASTNode(
                node_id="p1", sequence_id=2,
                node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Scientific content."),
            ),
        ]
        prepared = prepare_contextual_plan(
            document_id=_DOC, raw_ast=ast, estimator=_Estimator(),
        )
        digest = compute_ast_hash(ast)
        assert prepared.plan.ast_hash == digest
        DurableContextPlanRepository(ControlPlaneRepository(queue)).enqueue_verified(
            prepared.plan, prepared.ast,
        )
        fsm.execute(
            "INSERT INTO document_fsm (document_id,ast_hash,current_state,"
            "state_version,updated_at) VALUES (?,?,'PROCESSING',1,1)",
            (_DOC, digest),
        )
        fsm.commit()
        ast_dir = tmp_path / "ast_cache"
        ast_dir.mkdir()
        (ast_dir / f"{_DOC}.{digest}.ast.json").write_text(
            json.dumps({
                "document_id": _DOC, "ast_hash": digest,
                "nodes": [n.model_dump() for n in prepared.ast],
            }), encoding="utf8",
        )
        # Capture SQLite states closed and checkpointed before inspection.
        queue.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        yield tmp_path, prepared.plan


def test_frozen_bundle_valid_pending_generation(frozen):
    path, _ = frozen
    result = audit_frozen_bundle(path)
    assert result.generation_count == 1
    assert result.pending_generations == 1
    assert result.receipt_only_generations == 0
    assert len(result.bundle_sha256) == 64
    assert result == audit_frozen_bundle(path)


def test_frozen_bundle_rejects_missing_ast_copy(frozen):
    path, plan = frozen
    (path / "ast_cache" / f"{_DOC}.{plan.ast_hash}.ast.json").unlink()
    with pytest.raises(PipelineIntegrityError, match="AST_COPY_MISSING"):
        audit_frozen_bundle(path)


def test_frozen_bundle_rejects_missing_fsm_generation(frozen):
    path, plan = frozen
    with closing(sqlite3.connect(path / "fsm.db")) as fsm:
        fsm.execute(
            "DELETE FROM document_fsm WHERE document_id=? AND ast_hash=?",
            (_DOC, plan.ast_hash),
        )
        fsm.commit()
    with pytest.raises(PipelineIntegrityError, match="FSM_GENERATION_MISSING"):
        audit_frozen_bundle(path)


def test_frozen_bundle_rejects_ready_without_publication(frozen):
    path, plan = frozen
    with closing(sqlite3.connect(path / "fsm.db")) as fsm:
        fsm.execute(
            "UPDATE document_fsm SET current_state='READY_FOR_ASSEMBLY'"
        )
        fsm.commit()
    with pytest.raises(PipelineIntegrityError, match="READY_WITHOUT_PUBLICATION"):
        audit_frozen_bundle(path)


def test_frozen_bundle_rejects_wal_sidecar(frozen):
    path, _ = frozen
    (path / "queue.db-wal").write_bytes(b"not-a-frozen-backup")
    with pytest.raises(PipelineIntegrityError, match="UNCHECKPOINTED_SQLITE"):
        audit_frozen_bundle(path)


def test_frozen_bundle_rejects_orphan_task(frozen):
    path, _ = frozen
    with closing(sqlite3.connect(path / "queue.db")) as conn:
        conn.execute(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,created_at,updated_at) "
            "VALUES ('orphan','missing','hash','unit',1,1)"
        )
        conn.commit()
    with pytest.raises(PipelineIntegrityError, match="ORPHAN_TASK"):
        audit_frozen_bundle(path)


def test_frozen_bundle_rejects_modified_ast_semantics(frozen):
    path, plan = frozen
    file = path / "ast_cache" / f"{_DOC}.{plan.ast_hash}.ast.json"
    payload = json.loads(file.read_text(encoding="utf8"))
    payload["nodes"][0]["payload"]["content"] = "changed scientific contents"
    file.write_text(json.dumps(payload), encoding="utf8")
    with pytest.raises(PipelineIntegrityError, match="AST_GENERATION_DRIFT"):
        audit_frozen_bundle(path)


def test_frozen_bundle_does_not_create_new_files(frozen):
    path, _ = frozen
    before = {x.relative_to(path): x.read_bytes() for x in path.rglob("*") if x.is_file()}
    audit_frozen_bundle(path)
    after = {x.relative_to(path): x.read_bytes() for x in path.rglob("*") if x.is_file()}
    assert before == after


def test_frozen_bundle_missing_optional_event_is_allowed_but_invalid_is_not(frozen):
    path, _ = frozen
    audit_frozen_bundle(path)
    (path / "event.db").write_bytes(b"not-a-database")
    with pytest.raises((PipelineIntegrityError, sqlite3.DatabaseError)):
        audit_frozen_bundle(path)
