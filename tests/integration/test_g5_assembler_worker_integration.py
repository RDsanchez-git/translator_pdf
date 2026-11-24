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


def _worker(
    c, output: Path, monkeypatch: pytest.MonkeyPatch, crash_stage=None,
):
    # The production heartbeat starts its own thread-confined SQLite
    # connection. Bind BOTH paths to the disposable WAL databases created by
    # the sandbox fixture, rather than falling back to infra/db/*.db.
    monkeypatch.setenv("QUEUE_DB_PATH", str(output / "queue.db"))
    monkeypatch.setenv("FSM_DB_PATH", str(output / "fsm.db"))

    class FakeRunner:
        def compile(self, tex, *, output_dir, output_filename, image_assets=()):
            assert tex == "fake tex"
            # This particular scenario is text-only; never silently omit assets.
            assert image_assets == ()
            path = Path(output_dir) / output_filename
            assert path.name.startswith(".assembly_")
            assert output_dir == str(output)
            path.write_bytes(b"%PDF-1.4\nsynthetic but valid header\n")
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
    # These fakes intentionally implement only the methods exercised here, not
    # the complete concrete service classes. Inject them dynamically into this
    # __new__-constructed test instance, leaving production type contracts intact.
    setattr(worker, "control", types.SimpleNamespace(conn=c))
    setattr(worker, "context_resolver", FakeResolver())
    setattr(worker, "compilation_service", FakeCompiler())
    setattr(worker, "runner", FakeRunner())
    return worker


def test_real_worker_method_publishes_fenced_document(sandbox, monkeypatch):
    c, _connect, tmp = sandbox
    monkeypatch.setenv("COMPILER_OUTPUT_DIR", str(tmp))
    worker = _worker(c, tmp, monkeypatch)
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
    worker = _worker(c, tmp, monkeypatch, crash_stage="expire_during_compile")
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
    worker = _worker(c, tmp, monkeypatch, crash_stage="raise")
    with pytest.raises(RuntimeError, match="Simulated Tectonic failure"):
        worker._process_assembly_task("doc", "ast")
    assert _fsm(c)[0] == "FAILED_RETRYABLE"
    assert _row(c)[0] == "FAILED"
    assert not (tmp / "translated_doc.pdf").exists()
    assert not list(tmp.glob(".assembly_*.pdf"))


def test_real_worker_blocks_unverified_image_width_and_records_attributable_failure(
    sandbox, monkeypatch,
):
    """R8/DC-12: no final artifact or compiler effect for an unverified span."""
    from hashlib import sha256

    from apps.compiler.__main__ import RenderAssetAdapter, RenderGeometryAdapter
    from core.ast.enums import ContentNodeType, TranslationStrategy
    from core.ast.models import ASTNode, ImagePayload
    from core.compiler.assembler import DocumentAssembler
    from core.compiler.assembly_context import AssemblyExecutionContext
    from core.compiler.exceptions import ASTConsistencyError
    from core.compiler.rendering.mapper import DefaultRenderUnitMapper
    from core.compiler.service import CompilationService
    from core.document_profile.models import (
        InferredDocumentProfile, PageLayout, ProfileDiagnostics, SamplingCoverage,
    )
    from core.execution.ports import ProjectionRecord

    c, connect, tmp = sandbox
    monkeypatch.setenv("COMPILER_OUTPUT_DIR", str(tmp))
    worker = _worker(c, tmp, monkeypatch)
    asset = "data/assets/" + sha256(b"synthetic-image").hexdigest() + ".png"
    node = ASTNode(
        node_id="figure-1", sequence_id=1, node_type=ContentNodeType.IMAGE,
        strategy=TranslationStrategy.PASSTHROUGH,
        payload=ImagePayload(asset_path=asset),
    )
    context = AssemblyExecutionContext(
        document_id="doc", ast_hash="ast",
        ast_nodes=(node,),
        projections=(ProjectionRecord(node.node_id, asset, 1),),
        projection_version=1,
    )

    class Resolver:
        def resolve(self, **kwargs):
            assert kwargs == {
                "document_id": "doc", "ast_hash": "ast", "projection_version": 1,
            }
            return context

    class NoFallback:
        def get_verified_payload(self, job_id, chunk_id, expected_sha256):
            pytest.fail("CURRENT projection must not fall back to source")

    class Profiles:
        def get(self, document_id):
            assert document_id == "doc"
            return InferredDocumentProfile(
                layout=PageLayout.DOUBLE_COLUMN, document_type=None,
                physical_diagnostics=ProfileDiagnostics(
                    layout_confidence=1.0, type_confidence=1.0,
                    sampling_coverage=SamplingCoverage.STRICT_SCOPE,
                ),
            )

    class NoRunner:
        def compile(self, *args, **kwargs):
            pytest.fail("Unverified image span must not reach Tectonic")

    repo = NoFallback()
    service = CompilationService(
        DocumentAssembler(repo), repo, Profiles(),
        DefaultRenderUnitMapper(RenderGeometryAdapter(), RenderAssetAdapter()),
    )
    setattr(worker, "context_resolver", Resolver())
    setattr(worker, "compilation_service", service)
    setattr(worker, "runner", NoRunner())

    with pytest.raises(ASTConsistencyError, match="PPPR_G4_IMAGE_WIDTH_UNVERIFIED.*figure-1"):
        worker._process_assembly_task("doc", "ast")

    # The authorized failure is durable and attributable in the existing
    # FSM/queue, not merely a transient warning or a successful partial PDF.
    other = connect()
    try:
        assert _fsm(other) == ("FAILED_RETRYABLE", 2, 0)
        assert _row(other)[0] == "FAILED"
        reason = "PPPR_G4_IMAGE_WIDTH_UNVERIFIED node_id='figure-1'"
        assert other.execute(
            "SELECT failure_reason FROM fsm_db.document_fsm "
            "WHERE document_id='doc' AND ast_hash='ast'"
        ).fetchone() == (reason,)
        assert other.execute(
            "SELECT error_log FROM chunk_tasks WHERE worker_type='ASSEMBLER'"
        ).fetchone() == (reason,)
    finally:
        other.close()

    assert not (tmp / "translated_doc.pdf").exists()
    assert not list(tmp.glob(".assembly_*.pdf"))

