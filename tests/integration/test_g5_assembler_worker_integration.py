"""Exercise the *new worker method*, extracted from its patch source, with real WAL files.

The PDF renderer is a local stub; this verifies daemon orchestration, not Tectonic.
"""
import ast
import logging
import os
from pathlib import Path
import threading
import time
import types
import uuid

import pytest

from infra.db.assembly_recovery import AssemblyLeaseRepository
from tests.integration.test_g5_assembler_lease_recovery import (
    _expire,
    _fsm,
    _leader,
    _recover,
    _row,
    sandbox as sandbox,
)

ROOT = Path(__file__).resolve().parents[2]


class OptimisticLockError(Exception):
    pass


def worker_method():
    """Parse the actual patched compiler source; do not depend on a distributed patch."""
    source = (ROOT / 'apps/compiler/__main__.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    cls = next(node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == 'AssemblerWorkerDaemon')
    method = next(node for node in cls.body
                  if isinstance(node, ast.FunctionDef) and node.name == '_process_assembly_task')
    body = ast.unparse(method)
    assert 'AssemblyLeaseRepository' in body and 'leases.publish' in body
    return 'class Worker:\n' + '\n'.join('    '+line for line in body.splitlines()) + '\n'


def _worker(c, connect, output, crash_stage=None):
    class FakeRunner:
        def compile(self, tex, output_dir, output_filename):
            path=Path(output_dir)/output_filename
            assert path.name.startswith('.assembly_')
            assert output_dir==str(output)
            path.write_bytes(b'%PDF-1.4\nsynthetic but valid header\n')
            if crash_stage=='expire_during_compile':
                _expire(c)
            if crash_stage=='raise':
                raise RuntimeError('Simulated Tectonic failure')
            return str(path)
    class FakeResolver:
        def resolve(self, **kwargs):
            assert kwargs['document_id']=='doc'
            assert kwargs['ast_hash']=='ast'
            return types.SimpleNamespace()
    class FakeCompiler:
        def compile_document(self,ctx):return 'fake tex'
    env={'AssemblyLeaseRepository':AssemblyLeaseRepository,
         'threading':threading,'time':time,'uuid':uuid,'os':os,'logger':logging.getLogger('g5_worker_fixture'),
         'get_connection':lambda *a,**kw:connect(),'OptimisticLockError':OptimisticLockError}
    exec(worker_method(), env)
    w=env['Worker']()
    w.node_id='worker_smoke'
    w.control=types.SimpleNamespace(conn=c)
    w.context_resolver=FakeResolver()
    w.compilation_service=FakeCompiler()
    w.runner=FakeRunner()
    return w


def test_real_worker_method_publishes_fenced_document(sandbox,monkeypatch):
    c,connect,tmp=sandbox
    monkeypatch.setenv('COMPILER_OUTPUT_DIR',str(tmp))
    w=_worker(c,connect,tmp)
    w._process_assembly_task('doc','ast')
    assert _fsm(c)==('COMPLETED',4,1)
    assert _row(c)[0]=='COMPLETED'
    assert (tmp/'translated_doc.pdf').read_bytes().startswith(b'%PDF-')
    assert not list(tmp.glob('.assembly_*.pdf'))


def test_real_worker_method_rejects_expired_lease_without_final_publication(sandbox,monkeypatch):
    c,connect,tmp=sandbox
    monkeypatch.setenv('COMPILER_OUTPUT_DIR',str(tmp))
    w=_worker(c,connect,tmp,crash_stage='expire_during_compile')
    with pytest.raises(OptimisticLockError,match='STALE_PDF_PROMOTION'):
        w._process_assembly_task('doc','ast')
    assert not (tmp/'translated_doc.pdf').exists()
    assert not list(tmp.glob('.assembly_*.pdf'))
    assert _fsm(c)[0]=='COMPILING'
    _leader(c)
    assert _recover(c,AssemblyLeaseRepository(c))=='REQUEUED'


def test_real_worker_method_fences_failure_state(sandbox,monkeypatch):
    c,connect,tmp=sandbox
    monkeypatch.setenv('COMPILER_OUTPUT_DIR',str(tmp))
    w=_worker(c,connect,tmp,crash_stage='raise')
    with pytest.raises(RuntimeError,match='Simulated Tectonic failure'):
        w._process_assembly_task('doc','ast')
    assert _fsm(c)[0]=='FAILED_RETRYABLE'
    assert _row(c)[0]=='FAILED'
    assert not (tmp/'translated_doc.pdf').exists()
    assert not list(tmp.glob('.assembly_*.pdf'))
