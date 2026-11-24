"""PPPR 5.2.2: recovery with the attested offline foreground generation.

Real OCR, verified AST, engine, loopback SDK/bridge, admission and SQLite.
Faults are injected at local commit boundaries; these are not SIGKILL,
power-loss, physical host restart, commercial effects or science witnesses.
The container-isolation guard and tokenizer are substituted for CI; no
new model, cache or dependency acquisition is required.
All files and DBs are fresh pytest workspaces, never the owner's 5.2.1 evidence.
"""
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import threading

import pytest

from apps.cli import pdf_product
from apps.lab import pppr_offline_scope as lab
from apps.lab.g3_fake import FakeServer
from apps.lab.offline_pdf_lab import _smoke_source
from core.ast.registry import ASTRegistry
from core.ast.models import TranslationTaskType
from infra.db.context_snapshot_repo import DurableContextPlanRepository
from infra.db.control_repo import ControlPlaneRepository
from core.validation import estimators
from apps.ocr_router import __main__ as ocr_router
from runtime import engine, publication_pipeline
from tests.integration.test_w08_cli_foreground_single_generation_offline import (
    _prepare_workspace,
)

pytestmark = pytest.mark.integration


def _rows(state: Path, database: str, query: str):
    with closing(sqlite3.connect(state / database)) as conn:
        return conn.execute(query).fetchall()


def _evidence(state: Path):
    # Fresh workspace contains a single generation. Include whole immutable
    # rows, including original attempt IDs, checksums and creation timestamps.
    return {
        "plan": _rows(state, "queue.db", "SELECT * FROM chunk_plans"),
        "contexts": _rows(state, "queue.db",
                          "SELECT * FROM g3_context_snapshots ORDER BY context_id"),
        "receipts": _rows(state, "queue.db",
                          "SELECT * FROM chunk_result_receipts ORDER BY chunk_id"),
        "admissions": _rows(state, "queue.db",
                            "SELECT * FROM g3_admission_decisions ORDER BY task_id,execution_id"),
    }


def _publication(state: Path):
    return (
        _rows(state, "materialized.db", "SELECT * FROM g3_plan_publications"),
        _rows(state, "materialized.db", "SELECT * FROM valid_chunks_cache ORDER BY node_id"),
    )


def _fsm(state: Path):
    return _rows(state, "fsm.db",
                 "SELECT document_id,ast_hash,current_state,state_version,is_terminal "
                 "FROM document_fsm")


def _tasks(state: Path):
    return _rows(state, "queue.db",
                 "SELECT task_id,node_id,task_state,execution_id,retry_count,"
                 "lease_owner,lease_expires_at,error_log FROM chunk_tasks "
                 "WHERE worker_type='LLM' ORDER BY task_id")


def _assert_sqlite_integrity(state: Path):
    for database in ("fsm.db", "queue.db", "materialized.db"):
        assert _rows(state, database, "PRAGMA quick_check") == [("ok",)]
        assert _rows(state, database, "PRAGMA journal_mode") == [("wal",)]


@pytest.fixture
def recovery_subject(tmp_path, monkeypatch):
    state = _prepare_workspace(tmp_path, monkeypatch)
    # Do not inherit a path override from another test or local environment.
    for name in ("FSM_DB_PATH", "QUEUE_DB_PATH"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("TPDF_OFFLINE_LAB", lab.OPT_IN)
    monkeypatch.setenv("GROQ_API_KEY", lab.DUMMY_KEY)
    monkeypatch.setattr(lab, "require_isolated_environment", lambda: None)

    # Deterministic local estimator, consistent across OCR planning and G3.
    # The physical witness 5.2.1 already exercised the real cached tokenizer.
    class LocalEstimator:
        def estimate_tokens(self, text: str) -> int:
            return len(text.split())

    monkeypatch.setattr(estimators, "ExactBPEEstimator", LocalEstimator)
    monkeypatch.setattr(ocr_router, "ExactBPEEstimator", LocalEstimator)

    source = tmp_path / "data" / "inbox" / "recovery.pdf"
    source.parent.mkdir(parents=True)
    _smoke_source(source)
    document_id = sha256(source.read_bytes()).hexdigest()
    # Reuse the real foreground OCR consumer, not a fabricated AST/manifest.
    # This is a recovery witness, not another CLI/physical compiler witness.
    pdf_product._ingest(source, tmp_path)
    fsm = _fsm(state)
    assert len(fsm) == 1 and fsm[0][0] == document_id
    assert fsm[0][2] == "PROCESSING" and fsm[0][4] == 0
    ast_hash = fsm[0][1]
    ast = ASTRegistry().get_verified_document_ast(document_id, ast_hash)
    with closing(sqlite3.connect(state / "queue.db")) as queue:
        plan, snapshots = DurableContextPlanRepository(
            ControlPlaneRepository(queue),
        ).load_verified(document_id, ast_hash, ast)
    assert len(plan.units) == 7 and len(snapshots) == 4
    assert sum(u.chunk_type == TranslationTaskType.PRESERVE for u in plan.units) == 1
    assert sum(u.chunk_type == TranslationTaskType.TRANSLATE for u in plan.units) == 6

    with FakeServer(("127.0.0.1", 0), state / "queue.db", max_requests=16) as server:
        monkeypatch.setattr(lab, "ENDPOINT", f"http://127.0.0.1:{server.server_address[1]}")
        scope = lab.OfflineLabScope(document_id)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield state, document_id, ast_hash, scope, server
        finally:
            server.shutdown()
            thread.join(timeout=5)
            assert not thread.is_alive()


def _stop_at_boundary(*args, **kwargs):
    raise RuntimeError("PPPR_G5_RECOVERY_INJECTED_INTERRUPTION")


def _forbid_processor(*args, **kwargs):
    pytest.fail("Recovery must not initialize another inference processor")


@pytest.mark.parametrize(
    "boundary,expected_state,has_publication",
    [
        ("before_publication", "RESULT_STAGED", False),
        ("after_publication", "RESULT_STAGED", True),
        ("after_queue_ack", "COMPLETED", True),
    ],
)
def test_pppr_g5_attested_generation_recovery(
    recovery_subject, monkeypatch, boundary, expected_state, has_publication,
):
    state, document_id, ast_hash, scope, server = recovery_subject
    original_fsm = _fsm(state)
    with monkeypatch.context() as fault:
        if boundary == "before_publication":
            fault.setattr(publication_pipeline, "publish_staged_plan", _stop_at_boundary)
        elif boundary == "after_publication":
            fault.setattr(publication_pipeline, "finalize_published_plan", _stop_at_boundary)
        else:
            fault.setattr(publication_pipeline.DocumentCommandHandler, "handle", _stop_at_boundary)
        result = engine.run_pipeline(document_id, ast_hash, offline_scope=scope)
    assert result["status"] == "failed" and result["final_state"] == "PROCESSING"
    assert server.requests == 6
    assert _fsm(state) == original_fsm
    prior_tasks = _tasks(state)
    assert len(prior_tasks) == 7 and {r[2] for r in prior_tasks} == {expected_state}
    assert all(r[3] and r[4] == 0 for r in prior_tasks)
    if expected_state == "RESULT_STAGED":
        # Staged authority is retained until queue finalization (not a new claim).
        assert all(r[5] is not None and r[6] is not None for r in prior_tasks)
    else:
        assert all(r[5:7] == (None, None) for r in prior_tasks)
    evidence = _evidence(state)
    assert len(evidence["receipts"]) == 7 and len(evidence["admissions"]) == 6
    assert _rows(
        state, "queue.db",
        "SELECT COUNT(*) FROM chunk_result_receipts r JOIN g3_admission_decisions a "
        "ON r.task_id=a.task_id AND r.execution_id=a.execution_id "
        "AND r.generation_sha256=a.generation_sha256 WHERE r.raw_response IS NOT NULL",
    ) == [(6,)]
    published = _publication(state)
    assert (len(published[0]), len(published[1])) == ((1, 7) if has_publication else (0, 0))

    # The restart gets new engine connections and a fresh AST registry.
    # A different effective config is NOT the same generation and must
    # neither consume these receipts nor initialize inference as a fallback.
    monkeypatch.setattr(engine, "_create_chunk_processor", _forbid_processor)
    with monkeypatch.context() as drift:
        drift.setattr(lab, "PROMPT_VERSION", "pppr-g5-incompatible-recovery")
        rejected = engine.run_pipeline(document_id, ast_hash, offline_scope=scope)
    assert rejected["status"] == "failed" and rejected["final_state"] == "PROCESSING"
    assert server.requests == 6
    assert _fsm(state) == original_fsm
    assert _tasks(state) == prior_tasks
    assert _evidence(state) == evidence
    assert _publication(state) == published

    recovered = engine.run_pipeline(document_id, ast_hash, offline_scope=scope)
    assert recovered["status"] == "ready_for_assembly"
    assert server.requests == 6  # No extra HTTP POST in either recovery invocation.
    assert _fsm(state) == [(document_id, ast_hash, "READY_FOR_ASSEMBLY", original_fsm[0][3] + 1, 0)]
    after_tasks = _tasks(state)
    assert {r[2] for r in after_tasks} == {"COMPLETED"}
    assert [(r[0], r[1], r[3]) for r in after_tasks] == [
        (r[0], r[1], r[3]) for r in prior_tasks
    ]
    assert all(r[4] == 0 and r[5:7] == (None, None) for r in after_tasks)
    assert _evidence(state) == evidence
    final_publication = _publication(state)
    assert (len(final_publication[0]), len(final_publication[1])) == (1, 7)
    if has_publication:
        assert final_publication == published  # No rewriting an existing commit.
    _assert_sqlite_integrity(state)


def test_pppr_g5_loopback_response_before_receipt_stays_unknown(recovery_subject, monkeypatch):
    state, document_id, ast_hash, scope, server = recovery_subject
    original = ControlPlaneRepository.stage_chunk_result
    lost_attempts = []

    def fail_first_response_before_receipt(self, *args, **kwargs):
        if kwargs["raw_response"] is not None and not lost_attempts:
            # The real SDK/bridge has returned an accepted response, but its
            # local result is not durable. Admission is NOT a result receipt.
            lost_attempts.append((kwargs["task_id"], kwargs["execution_id"]))
            raise RuntimeError("PPPR_G5_RECOVERY_RESPONSE_NOT_DURABLE")
        return original(self, *args, **kwargs)

    with monkeypatch.context() as fault:
        fault.setattr(ControlPlaneRepository, "stage_chunk_result", fail_first_response_before_receipt)
        outcome = engine.run_pipeline(document_id, ast_hash, offline_scope=scope)
    assert outcome["status"] == "staging_incomplete"
    assert len(lost_attempts) == 1
    task_id, execution_id = lost_attempts[0]
    prior_tasks = _tasks(state)
    unknown = [r for r in prior_tasks if r[2] == "G3_EXTERNAL_UNKNOWN"]
    assert len(unknown) == 1
    assert unknown[0][0] == task_id and unknown[0][3] == execution_id
    assert unknown[0][4:7] == (0, None, None)
    assert json.loads(unknown[0][7])["execution_id"] == execution_id
    assert sum(r[2] == "RESULT_STAGED" for r in prior_tasks) == 6
    assert server.requests == 6
    assert _fsm(state)[0][2] == "PROCESSING"
    evidence = _evidence(state)
    assert len(evidence["receipts"]) == 6 and len(evidence["admissions"]) == 6
    assert _rows(
        state, "queue.db",
        "SELECT a.task_id,a.execution_id FROM g3_admission_decisions a "
        "LEFT JOIN chunk_result_receipts r ON a.task_id=r.task_id AND a.execution_id=r.execution_id "
        "WHERE r.task_id IS NULL",
    ) == [(task_id, execution_id)]
    assert _publication(state) == ([], [])

    monkeypatch.setattr(engine, "_create_chunk_processor", _forbid_processor)
    restarted = engine.run_pipeline(document_id, ast_hash, offline_scope=scope)
    assert restarted["status"] == "staging_incomplete"
    assert server.requests == 6
    assert _tasks(state) == prior_tasks
    assert _evidence(state) == evidence
    assert _publication(state) == ([], [])
    assert _fsm(state)[0][2] == "PROCESSING"
    _assert_sqlite_integrity(state)
