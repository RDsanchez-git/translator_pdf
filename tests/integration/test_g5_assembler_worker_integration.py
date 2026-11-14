"""Exercise the actual G5 daemon method with disposable WAL-backed leases.

The renderer and compilation service are local fakes: no Docker, real Tectonic,
real documents, production DBs or live output paths. Fencing remains real.
"""
import types
from pathlib import Path

import pytest

from apps.compiler.__main__ import AssemblerWorkerDaemon
from core.execution.exceptions import OptimisticLockError
from infra.db.assembly_recovery import AssemblyLeaseRepository
from tests.integration.test_g5_assembler_lease_recovery import (
    _expire,
    _fsm,
    _leader,
    _recover,
    _row,
    sandbox as sandbox,
)


def _worker(c, output: Path, crash_stage=None):
    class FakeRunner:
        def compile(self, tex, *, output_dir, output_filename, image_assets=()):
            assert tex == "fake tex"
            # This particular scenario is text-only; never silently omit assets.
            assert image_assets == ()
            path = Path(output_dir) / output_filename
            assert path.name.startswith(".assembly_")
            assert output_dir == str(output)
            path.write_bytes(b"%PDF-1.4\\nsynthetic but valid header\\n")
            if crash_stage == "expire_during_compile":
                _expire(c)
            if crash_stage == "raise":
                raise RuntimeError("Simulated Tectonic failure")
            return str(path)

    class FakeResolver:
        def resolve(self, **kwargs):
            assert kwargs["document_id"] == "doc"
            assert kwargs["ast_hash"] == "ast"
            assert kwargs["projection_version"] == 1
            return types.SimpleNamespace()

    class FakeCompiler:
        def compile_document_with_assets(self, context):
            assert context is not None
            return "fake tex", ()

        def compile_document(self, context):
            raise AssertionError("G5_LEGACY_TEXT_ONLY_INTERFACE_FORBIDDEN")

    # Bind fakes to the actual class, not an AST-unparsed/exec'd copy of its
    # method. This tests precisely the version production currently imports.
    worker = AssemblerWorkerDaemon.__new__(AssemblerWorkerDaemon)
    worker.node_id = "worker_smoke"
    worker.control = types.SimpleNamespace(conn=c)
    worker.context_resolver = FakeResolver()
    worker.compilation_service = FakeCompiler()
    worker.runner = FakeRunner()
    return worker


def test_real_worker_method_publishes_fenced_document(sandbox, monkeypatch):
    c, _connect, tmp = sandbox
    monkeypatch.setenv("COMPILER_OUTPUT_DIR", str(tmp))
    worker = _worker(c, tmp)
    worker._process_assembly_task("doc", "ast")
    assert _fsm(c) == ("COMPLETED", 4, 1)
    assert _row(c)[0] == "COMPLETED"
    assert (tmp / "translated_doc.pdf").read_bytes().startswith(b"%PDF-")
    assert not list(tmp.glob(".assembly_*.pdf"))


def test_real_worker_method_rejects_expired_lease_without_final_publication(
    sandbox, monkeypatch,
):
    c, _connect, tmp = sandbox
    monkeypatch.setenv("COMPILER_OUTPUT_DIR", str(tmp))
    worker = _worker(c, tmp, crash_stage="expire_during_compile")
    with pytest.raises(OptimisticLockError, match="STALE_PDF_PROMOTION"):
        worker._process_assembly_task("doc", "ast")
    assert not (tmp / "translated_doc.pdf").exists()
    assert not list(tmp.glob(".assembly_*.pdf"))
    assert _fsm(c)[0] == "COMPILING"
    _leader(c)
    assert _recover(c, AssemblyLeaseRepository(c)) == "REQUEUED"


def test_real_worker_method_fences_failure_state(sandbox, monkeypatch):
    c, _connect, tmp = sandbox
    monkeypatch.setenv("COMPILER_OUTPUT_DIR", str(tmp))
    worker = _worker(c, tmp, crash_stage="raise")
    with pytest.raises(RuntimeError, match="Simulated Tectonic failure"):
        worker._process_assembly_task("doc", "ast")
    assert _fsm(c)[0] == "FAILED_RETRYABLE"
    assert _row(c)[0] == "FAILED"
    assert not (tmp / "translated_doc.pdf").exists()
    assert not list(tmp.glob(".assembly_*.pdf"))
