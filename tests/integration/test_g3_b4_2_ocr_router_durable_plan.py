"""G3-B4/2: OCR Router -> G3 durable ChunkPlan and bounded FSM replay.

Uses temporary SQLite queue and faked OCR/profiler/FSM commands; never runs
Marker, paid LLM services, Docker, or a real PDF parser.
"""
from contextlib import closing
from hashlib import sha256
from pathlib import Path
import sqlite3
from types import SimpleNamespace

import pytest

from apps.ocr_router import __main__ as router_module
from core.ast.enums import ContentNodeType
from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode, ParagraphPayload
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from infra.db.control_repo import ControlPlaneRepository

ROOT = Path(__file__).resolve().parents[2]


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)


class _Parser:
    def __init__(self, ast):
        self.ast = ast
        self.calls = 0

    def parse(self, _path):
        self.calls += 1
        return self.ast


class _FSM:
    def __init__(self, document_id, ast_hash, initial=None, *, previous_hash=None):
        self.document_id = document_id
        self.ast_hash = ast_hash
        self.initial = initial
        self.previous_hash = previous_hash if previous_hash is not None else ast_hash
        self.state = initial
        self.version = 0
        self.initializes = 0

    def get_by_document_id(self, doc):
        assert doc == self.document_id
        if self.state is None:
            return None
        return SimpleNamespace(current_state=self.state, ast_hash=self.previous_hash,
                               state_version=self.version)

    def initialize_document(self, doc, ast_hash):
        assert (doc, ast_hash) == (self.document_id, self.ast_hash)
        self.initializes += 1
        if self.state is None:
            self.state = "CREATED"

    def get_status(self, doc, ast_hash):
        assert (doc, ast_hash) == (self.document_id, self.ast_hash)
        if self.state is None:
            return None
        return SimpleNamespace(current_state=self.state, state_version=self.version)


class _Handler:
    def __init__(self, fsm):
        self.fsm = fsm
        self.calls = []

    def handle(self, command):
        kind = type(command).__name__
        assert command.expected_version == self.fsm.version
        if kind == 'StartParsingCommand':
            assert self.fsm.state == 'CREATED'
            self.fsm.state = 'PARSING'
        elif kind == 'StartProcessingCommand':
            assert self.fsm.state == 'PARSING'
            self.fsm.state = 'PROCESSING'
        else:
            raise AssertionError('unexpected command ' + kind)
        self.fsm.version += 1
        self.calls.append(kind)
        return self.fsm.version


class _Registry:
    def __init__(self):
        self.calls = []

    def register_ast(self, document_id, ast_hash, ast):
        self.calls.append((document_id, ast_hash, ast))


class _Profiler:
    def profile(self, _input):
        return SimpleNamespace(profile=SimpleNamespace(layout='single', document_type='technical'))


class _ProfileStore:
    def __init__(self):
        self.calls = []

    def save(self, document_id, profile):
        self.calls.append((document_id, profile))


def _harness(tmp_path, monkeypatch, *, initial=None, previous_hash=None):
    monkeypatch.setattr(router_module, 'ExactBPEEstimator', _Estimator)
    ast = [
        ASTNode(node_id='n_one', sequence_id=1, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content='Alpha.')),
        ASTNode(node_id='n_two', sequence_id=2, node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content=' Beta.')),
    ]
    pdf_bytes = b'%PDF-1.4\nG3-B4/2 fixture, no real parsing\n'
    doc_id = sha256(pdf_bytes).hexdigest()
    ast_hash = compute_ast_hash(ast)
    db = sqlite3.connect(tmp_path / 'queue.db')
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript((ROOT / 'infra/db/schema_queue.sql').read_text(encoding='utf-8'))
    repo = ControlPlaneRepository(db)
    fsm = _FSM(doc_id, ast_hash, initial, previous_hash=previous_hash)
    handler = _Handler(fsm)
    parser = _Parser(ast)
    registry = _Registry()
    store = _ProfileStore()
    daemon = router_module.OCRRouterDaemon(
        fsm_repo=fsm, task_repo=repo, cmd_handler=handler,
        ast_registry=registry, document_profiler=_Profiler(),
        profile_store=store, parser=parser, workspace_dir=str(tmp_path),
    )
    pdf = daemon.inbox_dir / 'sample.pdf'
    pdf.write_bytes(pdf_bytes)
    units, _ = build_semantic_chunks_as_units(ast, _Estimator())
    plan = ChunkPlan.build(doc_id, ast_hash, ast, units)
    assert len(plan.units) == 1
    return SimpleNamespace(ast=ast, doc_id=doc_id, ast_hash=ast_hash, db=db,
                           repo=repo, fsm=fsm, handler=handler, parser=parser,
                           registry=registry, store=store, daemon=daemon,
                           pdf=pdf, plan=plan)


def _assert_durable_plan(h):
    assert h.repo.load_chunk_plan(h.doc_id, h.ast_hash, h.ast) == h.plan
    rows = h.db.execute('SELECT node_id,worker_type,task_state FROM chunk_tasks').fetchall()
    assert rows == [(h.plan.units[0].chunk_id, 'LLM', 'PENDING')]
    assert len(h.registry.calls) == 1
    assert (h.daemon.archive_dir / f'{h.doc_id[:8]}_sample.pdf').is_file()
    assert not h.pdf.exists()


def test_fresh_ingestion_persists_manifest_and_exactly_one_ast(tmp_path, monkeypatch):
    h = _harness(tmp_path, monkeypatch)
    with closing(h.db):
        h.daemon._process_document(h.pdf)
        _assert_durable_plan(h)
        assert h.handler.calls == ['StartParsingCommand', 'StartProcessingCommand']
        assert len(h.store.calls) == 1


@pytest.mark.parametrize('initial, expected_calls', [
    ('CREATED', ['StartParsingCommand', 'StartProcessingCommand']),
    ('PARSING', ['StartProcessingCommand']),
])
def test_incomplete_generation_retries_without_illegal_cas(tmp_path, monkeypatch,
                                                            initial, expected_calls):
    h = _harness(tmp_path, monkeypatch, initial=initial)
    with closing(h.db):
        h.daemon._process_document(h.pdf)
        _assert_durable_plan(h)
        assert h.handler.calls == expected_calls


def test_replay_existing_identical_manifest_is_idempotent(tmp_path, monkeypatch):
    h = _harness(tmp_path, monkeypatch, initial='PARSING')
    with closing(h.db):
        h.repo.enqueue_chunk_plan(h.plan, h.ast)
        h.daemon._process_document(h.pdf)
        _assert_durable_plan(h)
        assert h.db.execute('SELECT COUNT(*) FROM chunk_plans').fetchone()[0] == 1
        assert h.db.execute('SELECT COUNT(*) FROM chunk_tasks').fetchone()[0] == 1
        assert h.handler.calls == ['StartProcessingCommand']


def test_generation_drift_fails_closed_before_ast_or_enqueue(tmp_path, monkeypatch):
    h = _harness(tmp_path, monkeypatch, initial='PARSING', previous_hash='different_hash')
    with closing(h.db):
        h.daemon._process_document(h.pdf)
        assert h.handler.calls == []
        assert h.registry.calls == []
        assert h.db.execute('SELECT COUNT(*) FROM chunk_tasks').fetchone()[0] == 0
        assert len(list(h.daemon.error_dir.glob('FAILED_*_sample.pdf'))) == 1
        assert not list(h.daemon.archive_dir.glob('*.pdf'))


def test_legacy_tasks_without_plan_not_adopted(tmp_path, monkeypatch):
    h = _harness(tmp_path, monkeypatch, initial='PARSING')
    with closing(h.db):
        h.repo.enqueue_tasks(h.doc_id, h.ast_hash, [h.plan.units[0].chunk_id])
        h.daemon._process_document(h.pdf)
        assert h.handler.calls == []
        assert h.db.execute('SELECT COUNT(*) FROM chunk_tasks').fetchone()[0] == 1
        assert len(list(h.daemon.error_dir.glob('FAILED_*_sample.pdf'))) == 1
        assert not list(h.daemon.archive_dir.glob('*.pdf'))


@pytest.mark.parametrize('initial', ['PROCESSING', 'COMPLETED'])
def test_active_or_finished_document_shortcuts_before_ocr(tmp_path, monkeypatch, initial):
    h = _harness(tmp_path, monkeypatch, initial=initial)
    with closing(h.db):
        h.daemon._process_document(h.pdf)
        assert h.parser.calls == 0
        assert h.registry.calls == []
        assert h.handler.calls == []
        assert (h.daemon.archive_dir / f'DUP_SHORT_{h.doc_id[:8]}_sample.pdf').is_file()


def test_fsm_lookup_error_fails_closed_without_parsing(tmp_path, monkeypatch):
    h = _harness(tmp_path, monkeypatch)
    def unavailable(_doc):
        raise sqlite3.OperationalError('temporary test failure')
    monkeypatch.setattr(h.fsm, 'get_by_document_id', unavailable)
    with closing(h.db):
        h.daemon._process_document(h.pdf)
        assert h.parser.calls == 0
        assert h.handler.calls == []
        assert len(list(h.daemon.error_dir.glob('FAILED_*_sample.pdf'))) == 1


def test_failed_generation_requires_explicit_policy(tmp_path, monkeypatch):
    h = _harness(tmp_path, monkeypatch, initial='FAILED_RETRYABLE')
    with closing(h.db):
        h.daemon._process_document(h.pdf)
        assert h.parser.calls == 0
        assert h.handler.calls == []
        assert len(list(h.daemon.error_dir.glob('FAILED_*_sample.pdf'))) == 1
