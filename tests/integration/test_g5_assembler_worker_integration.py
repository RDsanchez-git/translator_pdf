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


@pytest.mark.parametrize("case", ["image", "heading", "empty_heading"])
def test_real_worker_blocks_unverified_representation_and_records_attributable_failure(
    sandbox, monkeypatch, case,
):
    """R6/R8/DC-12: an unverified representation has no compiler effect."""
    from hashlib import sha256

    from apps.compiler.__main__ import RenderAssetAdapter, RenderGeometryAdapter
    from core.ast.enums import ContentNodeType, HeadingLevel, TranslationStrategy
    from core.ast.models import ASTNode, HeadingPayload, ImagePayload
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
    if case == "image":
        node = ASTNode(
            node_id="figure-1", sequence_id=1, node_type=ContentNodeType.IMAGE,
            strategy=TranslationStrategy.PASSTHROUGH,
            payload=ImagePayload(asset_path=asset),
        )
        selected = asset
        code = "PPPR_G4_IMAGE_WIDTH_UNVERIFIED"
        expected_error = ASTConsistencyError
    else:
        node = ASTNode(
            node_id="heading-1", sequence_id=1, node_type=ContentNodeType.HEADING,
            strategy=TranslationStrategy.TRANSLATE,
            payload=HeadingPayload(
                content="Methods",
                heading_level=HeadingLevel.UNKNOWN if case == "heading" else HeadingLevel.H1,
            ),
        )
        selected = "Methods" if case == "heading" else " "
        code = (
            "PPPR_G4_HEADING_LEVEL_UNVERIFIED" if case == "heading"
            else "PPPR_G4_HEADING_CONTENT_MISSING"
        )
        expected_error = ValueError
    reason = f"{code} node_id={ascii(node.node_id)}"
    context = AssemblyExecutionContext(
        document_id="doc", ast_hash="ast",
        ast_nodes=(node,),
        projections=(ProjectionRecord(node.node_id, selected, 1),),
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
            pytest.fail("Unverified representation must not reach Tectonic")

    repo = NoFallback()
    service = CompilationService(
        DocumentAssembler(repo), repo, Profiles(),
        DefaultRenderUnitMapper(RenderGeometryAdapter(), RenderAssetAdapter()),
    )
    setattr(worker, "context_resolver", Resolver())
    setattr(worker, "compilation_service", service)
    setattr(worker, "runner", NoRunner())

    with pytest.raises(expected_error) as error:
        worker._process_assembly_task("doc", "ast")
    assert str(error.value) == reason

    # The authorized failure is durable and attributable in the existing
    # FSM/queue, not merely a transient warning or a successful partial PDF.
    other = connect()
    try:
        assert _fsm(other) == ("FAILED_RETRYABLE", 2, 0)
        assert _row(other)[0] == "FAILED"
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


@pytest.mark.integration
@pytest.mark.parametrize(
    ("total", "missing_indices", "heading", "status"),
    [
        (10, (1,), True, "REJECTED"),
        (20, (1,), True, "DEGRADED"),
        (21, (1,), True, "DEGRADED"),
        (20, (1,), False, "DEGRADED"),
        (10, (1, 2, 3, 4), False, "REJECTED"),
        (20, (), False, "SUCCESS"),
    ],
)
def test_product_assembly_requires_complete_current_projections(
    sandbox, monkeypatch, total, missing_indices, heading, status,
):
    """H-G4-03/04: historical SHA-valid backing is not final PDF authority."""
    from contextlib import closing
    from hashlib import sha256
    import sqlite3

    from apps.compiler.__main__ import RenderAssetAdapter, RenderGeometryAdapter
    from core.ast.enums import ContentNodeType, HeadingLevel, TranslationStrategy
    from core.ast.models import ASTNode, HeadingPayload, ParagraphPayload
    from core.compiler.assembler import AssemblyPolicy, AssemblyStatus, DocumentAssembler
    from core.compiler.assembly_context import AssemblyExecutionContext
    from core.compiler.exceptions import AssemblyRejectedError
    from core.compiler.rendering.mapper import DefaultRenderUnitMapper
    from core.compiler.service import CompilationService
    from core.document_profile.models import InferredDocumentProfile, PageLayout
    from core.execution.ports import ProjectionRecord
    from infra.db.document_repository import SQLiteDocumentRepository

    c, connect, tmp = sandbox
    monkeypatch.setenv("COMPILER_OUTPUT_DIR", str(tmp))
    worker = _worker(c, tmp, monkeypatch)
    source = "Original source content."
    digest = sha256(source.encode("utf-8")).hexdigest()
    # Long, distinct identities also falsify truncation of durable evidence.
    nodes = tuple(
        ASTNode(
            node_id=f"node-{i}-" + ("x" * 80 if len(missing_indices) > 1 else ""),
            sequence_id=i,
            node_type=ContentNodeType.HEADING if heading and i == 1 else ContentNodeType.PARAGRAPH,
            strategy=TranslationStrategy.TRANSLATE,
            payload=(
                HeadingPayload(content=source, heading_level=HeadingLevel.H1)
                if heading and i == 1 else ParagraphPayload(content=source)
            ),
            control_plane={"chunk_id": f"legacy-{i}", "payload_sha256": digest},
        )
        for i in range(1, total + 1)
    )
    context = AssemblyExecutionContext(
        document_id="doc", ast_hash="ast", ast_nodes=nodes,
        projections=tuple(
            ProjectionRecord(n.node_id, f"Texto seleccionado {n.sequence_id}.", 1)
            for n in nodes if n.sequence_id not in missing_indices
        ),
        projection_version=1,
    )

    class Resolver:
        def resolve(self, **kwargs):
            return context

    class Profiles:
        def get(self, document_id):
            assert document_id == "doc"
            return InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)

    class Runner:
        def compile(self, tex, *, output_dir, output_filename, image_assets=()):
            assert status == "SUCCESS", "Rejected assembly must never reach Tectonic"
            assert source not in tex
            assert all(f"Texto seleccionado {i}." in tex for i in range(1, total + 1))
            assert image_assets == ()
            target = Path(output_dir) / output_filename
            target.write_bytes(b"%PDF-1.4\nsynthetic publication witness\n")
            return str(target)

    with closing(sqlite3.connect(tmp / "backing.db")) as backing:
        repository = SQLiteDocumentRepository(backing)
        with backing:
            backing.executemany(
                "INSERT INTO original_chunks (job_id,chunk_id,payload,payload_sha256) VALUES (?,?,?,?)",
                [("doc", f"legacy-{i}", source, digest) for i in missing_indices],
            )
        # Establish independently that the historical fallback is available
        # and passes the actual repository's integrity checks.
        for i in missing_indices:
            assert repository.get_verified_payload("doc", f"legacy-{i}", digest) == source

        def forbidden_fallback(*args, **kwargs):
            pytest.fail("Product compilation must not read historical backing")

        monkeypatch.setattr(repository, "get_verified_payload", forbidden_fallback)
        assembler = DocumentAssembler(
            repository, policy=AssemblyPolicy(tolerance_ratio=0.05, allow_fallback=True),
        )
        decision = assembler.assemble(context)
        assert decision.status == AssemblyStatus[status]
        assert decision.is_accepted == (status != "REJECTED")
        assert decision.missing_node_ids == tuple(
            n.node_id for n in nodes if n.sequence_id in missing_indices
        )
        service = CompilationService(
            assembler, repository, Profiles(),
            DefaultRenderUnitMapper(RenderGeometryAdapter(), RenderAssetAdapter()),
        )
        setattr(worker, "context_resolver", Resolver())
        setattr(worker, "compilation_service", service)
        setattr(worker, "runner", Runner())

        if status == "SUCCESS":
            worker._process_assembly_task("doc", "ast")
            assert _fsm(c) == ("COMPLETED", 4, 1)
            assert _row(c)[0] == "COMPLETED"
            assert (tmp / "translated_doc.pdf").is_file()
        else:
            with pytest.raises(AssemblyRejectedError) as error:
                worker._process_assembly_task("doc", "ast")
            missing = ascii(decision.missing_node_ids)
            expected = (
                f"PPPR_G4_DEGRADED_ASSEMBLY_FORBIDDEN missing_node_ids={missing}"
                if status == "DEGRADED" else
                f"PPPR_G4_ASSEMBLY_REJECTED missing_node_ids={missing}; reason={decision.rejection_reason}"
            )
            assert str(error.value) == expected
            if len(missing_indices) > 1:
                assert len(expected) > 250
            with closing(connect()) as observed:
                assert _fsm(observed) == ("FAILED_RETRYABLE", 2, 0)
                assert _row(observed)[0] == "FAILED"
                assert observed.execute(
                    "SELECT failure_reason FROM fsm_db.document_fsm "
                    "WHERE document_id='doc' AND ast_hash='ast'"
                ).fetchone() == (expected,)
                assert observed.execute(
                    "SELECT error_log FROM chunk_tasks WHERE worker_type='ASSEMBLER'"
                ).fetchone() == (expected,)
            assert not (tmp / "translated_doc.pdf").exists()
        assert not list(tmp.glob(".assembly_*.pdf"))
