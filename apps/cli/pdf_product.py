"""Foreground PDF->PDF product adapter over the canonical OCR/G3/G5 route.

The completion predicate is operational: FSM COMPLETED + a published PDF.
Scientific equation fidelity remains an OPEN limitation (B02.5/B02.6).
This module does not bypass G3, invent translations or certify mathematics.

All expensive imports are local to stage adapters. The original daemons can
still run independently; this foreground adapter executes one requested
content-addressed document in sequence instead of starting infinite loops.
"""
from __future__ import annotations

from contextlib import ExitStack, closing
from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil

from apps.cli.pdf_inbox import PDFInboxSubmission


class PDFProductError(RuntimeError):
    """An operational prerequisite or stage failed; never report PDF success."""


@dataclass(frozen=True, slots=True)
class PDFProductResult:
    document_id: str
    ast_hash: str
    output_pdf: Path
    # This intentionally does NOT represent scientific certification.
    execution_status: str = "COMPLETED"
    scientific_status: str = "NOT_CERTIFIED"


def preflight_product_run(root: Path, inbox_dir: Path) -> None:
    """Reject unexpected workspace, missing state and missing compiler before admission.

    The existing R2 code uses some cwd-relative paths (OCR inbox, runtime DB,
    AST registry). Until their configuration is unified, never run from a
    different cwd or target a non-canonical inbox and silently split a job.
    """
    root = root.resolve()
    if Path.cwd().resolve() != root:
        raise PDFProductError(
            "PDF_RUN_WORKSPACE_MISMATCH: ejecutar desde la raiz del repositorio"
        )
    if inbox_dir.resolve() != (root / "data" / "inbox").resolve():
        raise PDFProductError(
            "PDF_RUN_INBOX_MISMATCH: --run exige data/inbox canonico"
        )
    configured_root = os.getenv("APP_ROOT")
    if configured_root and Path(configured_root).resolve() != root:
        raise PDFProductError("PDF_RUN_APP_ROOT_MISMATCH")

    # No implicit schema migration or destructive startup against live SQLite.
    from infra.db.connection import resolve_sqlite_path
    required = ("fsm.db", "queue.db", "materialized.db")
    missing = [str(Path(resolve_sqlite_path(f"infra/db/{name}")))
               for name in required
               if not Path(resolve_sqlite_path(f"infra/db/{name}")).is_file()]
    if missing:
        raise PDFProductError(
            "PDF_RUN_DB_NOT_INITIALIZED: ejecutar una vez "
            "'python -m infra.db.bootstrap'; faltan: " + ", ".join(missing)
        )
    if shutil.which("tectonic") is None:
        raise PDFProductError(
            "PDF_RUN_TECTONIC_UNAVAILABLE: Tectonic no esta disponible en PATH"
        )


def _read_status(document_id: str):
    from infra.db.connection import get_connection
    from infra.db.fsm_repository import FSMRepository
    with closing(get_connection("infra/db/fsm.db", timeout=30)) as conn:
        return FSMRepository(conn).get_by_document_id(document_id)


def _ingest(pdf_path: Path, root: Path) -> None:
    """One OCR admission using exactly the daemon's canonical implementation."""
    from apps.ocr_router.__main__ import OCRRouterDaemon
    from apps.bootstrap.pipeline_factory import build_document_profiler, build_extraction_pipeline
    from infra.db.connection import get_connection
    from infra.db.fsm_repository import FSMRepository
    from infra.db.control_repo import ControlPlaneRepository
    from infra.db.profile_store import SQLiteProfileStore
    from core.ast.registry import ASTRegistry
    from core.execution.handlers import DocumentCommandHandler

    with ExitStack() as stack:
        fsm_conn = stack.enter_context(closing(get_connection("infra/db/fsm.db", timeout=30)))
        queue_conn = stack.enter_context(closing(get_connection("infra/db/queue.db", timeout=30)))
        docs_conn = stack.enter_context(closing(get_connection("infra/db/documents.db", timeout=30)))
        fsm_repo = FSMRepository(fsm_conn)
        queue_repo = ControlPlaneRepository(queue_conn)
        router = OCRRouterDaemon(
            fsm_repo=fsm_repo, task_repo=queue_repo,
            cmd_handler=DocumentCommandHandler(fsm_repo, task_repo=queue_repo),
            ast_registry=ASTRegistry(workspace_dir=str(root)),
            document_profiler=build_document_profiler(),
            profile_store=SQLiteProfileStore(docs_conn),
            parser=build_extraction_pipeline(), workspace_dir=str(root),
        )
        # OCRRouterDaemon quarantines its own failures rather than raising.
        # Callers MUST verify the durable FSM state afterwards.
        router._process_document(pdf_path)


def _run_g3(document_id: str, ast_hash: str) -> None:
    from runtime.engine import run_pipeline
    run_pipeline(document_id, ast_hash)


def _run_g5(document_id: str, ast_hash: str) -> None:
    """One authorized G5 attempt using existing assembler, lease and publisher."""
    from infra.db.connection import get_connection
    from infra.db.control_repo import ControlPlaneRepository
    from infra.db.fsm_repository import FSMRepository
    from infra.db.materialized_repo import MaterializedPlaneRepository
    from infra.db.profile_store import SQLiteProfileStore
    from infra.db.document_repository import SQLiteDocumentRepository
    from core.ast.registry import ASTRegistry
    from core.execution.handlers import DocumentCommandHandler
    from core.compiler.assembler import DocumentAssembler, AssemblyPolicy
    from core.compiler.context_resolver import CQRSAssemblyContextResolver
    from core.compiler.rendering.mapper import DefaultRenderUnitMapper
    from core.compiler.service import CompilationService
    from apps.compiler.tectonic_runner import HostTectonicRunner
    from apps.compiler.__main__ import (
        AssemblerWorkerDaemon, RenderGeometryAdapter, RenderAssetAdapter,
    )

    with ExitStack() as stack:
        fsm_conn = stack.enter_context(closing(get_connection("infra/db/fsm.db", timeout=30)))
        queue_conn = stack.enter_context(closing(get_connection("infra/db/queue.db", timeout=30)))
        mat_conn = stack.enter_context(closing(get_connection("infra/db/materialized.db", timeout=30)))
        docs_conn = stack.enter_context(closing(get_connection("infra/db/documents.db", timeout=30)))
        fsm_repo = FSMRepository(fsm_conn)
        queue_repo = ControlPlaneRepository(queue_conn)
        materialized = MaterializedPlaneRepository(mat_conn)
        ast_registry = ASTRegistry()
        docs_repo = SQLiteDocumentRepository(docs_conn)
        policy = AssemblyPolicy(tolerance_ratio=0.05, allow_fallback=True,
                                degradable_failures=frozenset())
        assembler = DocumentAssembler(repository=docs_repo, separator="\n\n", policy=policy)
        mapper = DefaultRenderUnitMapper(RenderGeometryAdapter(), RenderAssetAdapter())
        compilation = CompilationService(
            assembler=assembler, payload_repository=docs_repo,
            profile_store=SQLiteProfileStore(docs_conn), mapper=mapper,
        )
        resolver = CQRSAssemblyContextResolver(ast_provider=ast_registry,
                                                materialized_plane=materialized)
        worker = AssemblerWorkerDaemon(
            control_repo=queue_repo, fsm_repo=fsm_repo,
            cmd_handler=DocumentCommandHandler(fsm_repo, task_repo=queue_repo),
            mat_repo=materialized, ast_registry=ast_registry,
            runner=HostTectonicRunner(), compilation_service=compilation,
            context_resolver=resolver,
        )
        worker._process_assembly_task(document_id, ast_hash)


def _verify_published_pdf(root: Path, document_id: str, ast_hash: str) -> PDFProductResult:
    destination = Path(os.getenv("COMPILER_OUTPUT_DIR", "output"))
    if not destination.is_absolute():
        destination = root / destination
    path = destination / f"translated_{document_id}.pdf"
    if path.is_symlink() or not path.is_file() or path.stat().st_size < 8:
        raise PDFProductError("PDF_RUN_COMPLETED_WITHOUT_PUBLISHED_PDF: " + str(path))
    with path.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            raise PDFProductError("PDF_RUN_INVALID_PUBLISHED_PDF: " + str(path))
    return PDFProductResult(document_id=document_id, ast_hash=ast_hash,
                            output_pdf=path.resolve())


def _require_state(document_id: str, expected: str):
    current = _read_status(document_id)
    if current is None:
        raise PDFProductError("PDF_RUN_FSM_STATE_MISSING: " + document_id)
    if current.current_state != expected:
        raise PDFProductError(
            f"PDF_RUN_STAGE_NOT_COMPLETE: expected={expected} actual={current.current_state} "
            f"document_id={document_id}"
        )
    return current


def run_admitted_pdf(receipt: PDFInboxSubmission, root: Path) -> PDFProductResult:
    """Run one admitted PDF through OCR -> G3 -> G5, or resume at its durable state.

    A successful return proves only operational completion: no scientific
    fidelity verdict is inferred from the presence of a PDF or from FSM state.
    No automatic retries of failed, stalled, or foreign-owned generations.
    """
    root = root.resolve()
    document_id = receipt.document_id
    if not re.fullmatch(r"[0-9a-f]{64}", document_id):
        raise PDFProductError("PDF_RUN_INVALID_DOCUMENT_ID")
    state = _read_status(document_id)
    if state is None or state.current_state in ("CREATED", "PARSING"):
        if not receipt.inbox_path.is_file():
            raise PDFProductError("PDF_RUN_INBOX_FILE_NOT_AVAILABLE: " + str(receipt.inbox_path))
        try:
            _ingest(receipt.inbox_path, root)
        except Exception as exc:
            raise PDFProductError(f'PDF_RUN_OCR_EXECUTION_FAILED: {exc}') from exc
        state = _read_status(document_id)
    if state is None:
        raise PDFProductError("PDF_RUN_OCR_NO_FSM_STATE: consultar data/error")
    if state.current_state == "COMPLETED":
        return _verify_published_pdf(root, document_id, state.ast_hash)
    if state.current_state == "PROCESSING":
        try:
            _run_g3(document_id, state.ast_hash)
        except Exception as exc:
            raise PDFProductError(f'PDF_RUN_G3_EXECUTION_FAILED: {exc}') from exc
        state = _require_state(document_id, "READY_FOR_ASSEMBLY")
    if state.current_state == "READY_FOR_ASSEMBLY":
        try:
            _run_g5(document_id, state.ast_hash)
        except Exception as exc:
            raise PDFProductError(f'PDF_RUN_G5_EXECUTION_FAILED: {exc}') from exc
        state = _require_state(document_id, "COMPLETED")
        return _verify_published_pdf(root, document_id, state.ast_hash)
    raise PDFProductError(
        f"PDF_RUN_UNSUPPORTED_STATE: {state.current_state}; "
        "la generacion requiere diagnostico o reanudacion explicita"
    )
