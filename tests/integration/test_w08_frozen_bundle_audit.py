"""W08-2d frozen-copy auditor: no live DBs, process control or providers."""
from contextlib import closing
from hashlib import sha256
from pathlib import Path
import json
import sqlite3

import pytest

from core.ast.enums import ContentNodeType, HeadingLevel
from core.ast.models import ASTNode, HeadingPayload, ParagraphPayload, TranslationTaskType
from core.ast.hashing import compute_ast_hash
from core.chunking.contextual_plan import prepare_contextual_plan
from core.execution.exceptions import PipelineIntegrityError
from infra.db.control_repo import ControlPlaneRepository
from infra.db.context_snapshot_repo import DurableContextPlanRepository
from infra.db.frozen_bundle_audit import audit_frozen_bundle
from infra.db.staged_publication import finalize_published_plan, publish_staged_plan


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


def test_frozen_bundle_rejects_orphan_receipt(frozen):
    path, _ = frozen
    with closing(sqlite3.connect(path / "queue.db")) as conn:
        conn.execute(
            "INSERT INTO chunk_tasks "
            "(task_id,document_id,ast_hash,node_id,created_at,updated_at) "
            "VALUES ('orphan-task','other','hash','unit',1,1)"
        )
        conn.execute(
            "INSERT INTO chunk_result_receipts "
            "(document_id,ast_hash,chunk_id,task_id,execution_id,created_at) "
            "VALUES ('other','hash','chunk','orphan-task','execution',1)"
        )
        conn.commit()
        # Remove the orphan task to ensure the receipt alone is rejected.
        # FK constraints are not enabled in this isolated corruption witness.
        conn.execute("DELETE FROM chunk_tasks WHERE task_id='orphan-task'")
        conn.commit()
    with pytest.raises(PipelineIntegrityError, match="ORPHAN_DURABLE_EVIDENCE"):
        audit_frozen_bundle(path)


def test_frozen_bundle_rejects_orphan_publication(frozen):
    path, _ = frozen
    with closing(sqlite3.connect(path / "materialized.db")) as conn:
        conn.execute(
            "INSERT INTO g3_plan_publications "
            "(document_id,ast_hash,manifest_sha256,result_sha256,"
            "projection_version,created_at) VALUES ('other','hash',?,?,1,1)",
            ("a" * 64, "b" * 64),
        )
        conn.commit()
    with pytest.raises(PipelineIntegrityError, match="ORPHAN_DURABLE_EVIDENCE"):
        audit_frozen_bundle(path)


def test_frozen_bundle_rejects_context_snapshot_identity_tampering(frozen):
    path, plan = frozen
    with closing(sqlite3.connect(path / "queue.db")) as conn:
        conn.execute(
            "UPDATE g3_context_snapshots SET manifest_sha256=? "
            "WHERE document_id=? AND ast_hash=?",
            ("f" * 64, _DOC, plan.ast_hash),
        )
        conn.commit()
    with pytest.raises(PipelineIntegrityError, match="CONTEXT_SNAPSHOT_DRIFT"):
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


def _stage_frozen_generation(frozen, *, publish=False, complete=False):
    path, plan = frozen
    ast_file = path / "ast_cache" / f"{_DOC}.{plan.ast_hash}.ast.json"
    ast = [ASTNode.model_validate(node) for node in json.loads(
        ast_file.read_text(encoding="utf8")
    )["nodes"]]
    with closing(sqlite3.connect(path / "queue.db")) as queue:
        repo = ControlPlaneRepository(queue)
        units = {unit.chunk_id: unit for unit in plan.units}
        for _ in plan.units:
            lease = repo.pick_task("audit-worker", plan.document_id, plan.ast_hash)
            assert lease is not None
            unit = units[lease.node_id]
            response = None
            if unit.chunk_type != TranslationTaskType.PRESERVE:
                response = json.dumps({
                    "schema_version": 1, "document_id": plan.document_id,
                    "ast_hash": plan.ast_hash, "manifest_sha256": plan.digest,
                    "chunk_id": unit.chunk_id,
                    "members": [{
                        "node_id": member.node_id,
                        "segment_index": member.segment_index,
                        "source_sha256": sha256(
                            member.source_text.encode("utf-8")
                        ).hexdigest(),
                        "translated_text": "Contenido traducido.",
                    } for member in unit.members],
                }, ensure_ascii=False)
            assert repo.stage_chunk_result(
                plan, ast, chunk_id=unit.chunk_id, task_id=lease.task_id,
                worker_id="audit-worker", execution_id=lease.execution_id,
                raw_response=response,
            )
        if publish or complete:
            with closing(sqlite3.connect(path / "materialized.db")) as material:
                assert publish_staged_plan(repo, material, plan, ast)
                if complete:
                    assert finalize_published_plan(
                        repo, material, plan, ast,
                    )
    return ast


def test_frozen_bundle_accepts_valid_staged_receipt_only(frozen):
    _stage_frozen_generation(frozen)
    report = audit_frozen_bundle(frozen[0])
    assert report.receipt_only_generations == 1
    assert report.pending_generations == 0
    assert report.published_generations == 0


def test_frozen_bundle_accepts_staged_publication_without_double_count(frozen):
    _stage_frozen_generation(frozen, publish=True)
    report = audit_frozen_bundle(frozen[0])
    assert report.published_generations == 1
    assert report.receipt_only_generations == 0


def test_frozen_bundle_accepts_completed_ready_publication(frozen):
    _stage_frozen_generation(frozen, complete=True)
    with closing(sqlite3.connect(frozen[0] / "fsm.db")) as fsm:
        fsm.execute("UPDATE document_fsm SET current_state='READY_FOR_ASSEMBLY'")
        fsm.commit()
    report = audit_frozen_bundle(frozen[0])
    assert report.published_generations == 1
    assert report.receipt_only_generations == 0


def test_frozen_bundle_rejects_tampered_publication_result_digest(frozen):
    _stage_frozen_generation(frozen, publish=True)
    with closing(sqlite3.connect(frozen[0] / "materialized.db")) as material:
        material.execute(
            "UPDATE g3_plan_publications SET result_sha256=?",
            ("0" * 64,),
        )
        material.commit()
    with pytest.raises(ValueError, match="PUBLICATION_CONFLICT_OR_MISSING"):
        audit_frozen_bundle(frozen[0])


def test_frozen_bundle_rejects_projection_version_drift(frozen):
    _stage_frozen_generation(frozen, publish=True)
    with closing(sqlite3.connect(frozen[0] / "materialized.db")) as material:
        material.execute(
            "UPDATE g3_plan_publications SET projection_version=2"
        )
        material.commit()
    with pytest.raises(ValueError, match="PROJECTION_DRIFT"):
        audit_frozen_bundle(frozen[0])


def test_frozen_bundle_rejects_missing_modern_context_snapshots(frozen):
    with closing(sqlite3.connect(frozen[0] / "queue.db")) as queue:
        queue.execute("DELETE FROM g3_context_snapshots")
        queue.commit()
    with pytest.raises(PipelineIntegrityError, match="CONTEXT_SNAPSHOT_COVERAGE"):
        audit_frozen_bundle(frozen[0])


def test_frozen_bundle_rejects_noncanonical_task_id(frozen):
    with closing(sqlite3.connect(frozen[0] / "queue.db")) as queue:
        queue.execute("UPDATE chunk_tasks SET task_id='different-task'")
        queue.commit()
    with pytest.raises(ValueError, match="QUEUE_MANIFEST_DRIFT"):
        audit_frozen_bundle(frozen[0])


def test_frozen_bundle_rejects_missing_nonpreserve_payload(frozen):
    _stage_frozen_generation(frozen)
    with closing(sqlite3.connect(frozen[0] / "queue.db")) as queue:
        queue.execute(
            "UPDATE chunk_result_receipts "
            "SET raw_response=NULL,response_sha256=NULL WHERE raw_response IS NOT NULL"
        )
        queue.commit()
    with pytest.raises(PipelineIntegrityError, match="RECEIPT_PAYLOAD_DRIFT"):
        audit_frozen_bundle(frozen[0])


def test_frozen_bundle_rejects_checksum_valid_but_invalid_response(frozen):
    _stage_frozen_generation(frozen)
    forged = '{"not":"a-translation-response"}'
    with closing(sqlite3.connect(frozen[0] / "queue.db")) as queue:
        queue.execute(
            "UPDATE chunk_result_receipts SET raw_response=?, response_sha256=? "
            "WHERE raw_response IS NOT NULL",
            (forged, sha256(forged.encode("utf-8")).hexdigest()),
        )
        queue.commit()
    with pytest.raises(ValueError):
        audit_frozen_bundle(frozen[0])


def test_frozen_bundle_rejects_published_generation_with_pending_task(frozen):
    _stage_frozen_generation(frozen, publish=True)
    with closing(sqlite3.connect(frozen[0] / "queue.db")) as queue:
        queue.execute(
            "UPDATE chunk_tasks SET task_state='PENDING' "
            "WHERE node_id=?",
            (frozen[1].units[-1].chunk_id,),
        )
        queue.commit()
    with pytest.raises(PipelineIntegrityError, match="RECEIPT_BINDING"):
        audit_frozen_bundle(frozen[0])


def test_frozen_bundle_hash_includes_extra_custody_file(frozen):
    path, _ = frozen
    original = audit_frozen_bundle(path).bundle_sha256
    (path / "custody-manifest.json").write_text(
        '{"custody":"synthetic"}', encoding="utf8",
    )
    changed = audit_frozen_bundle(path).bundle_sha256
    assert changed != original


def test_frozen_bundle_accepts_safe_legacy_document_ids(frozen):
    from infra.db.frozen_bundle_audit import _ast_from_copy
    path, plan = frozen
    source = path / "ast_cache" / f"{_DOC}.{plan.ast_hash}.ast.json"
    target = path / "ast_cache" / f"doc_legacy.{plan.ast_hash}.ast.json"
    payload = json.loads(source.read_text(encoding="utf8"))
    payload["document_id"] = "doc_legacy"
    target.write_text(json.dumps(payload), encoding="utf8")
    assert len(_ast_from_copy(path, "doc_legacy", plan.ast_hash)) == len(
        payload["nodes"]
    )
