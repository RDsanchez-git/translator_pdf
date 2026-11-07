"""Foreground product contract: no remote APIs, physical compiler or daemons."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import pytest

from apps.cli.pdf_inbox import PDFInboxSubmission
from apps.cli import pdf_product as product


def admitted(tmp_path: Path) -> PDFInboxSubmission:
    inbox = tmp_path / "data" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    payload = b"%PDF-1.4\nlocal-check"
    pdf = inbox / (hashlib.sha256(payload).hexdigest() + ".pdf")
    pdf.write_bytes(payload)
    return PDFInboxSubmission(hashlib.sha256(payload).hexdigest(), pdf, False)


def mock_pipeline(monkeypatch, tmp_path, *, initial=None, after_ocr="PROCESSING",
                  after_g3="READY_FOR_ASSEMBLY", after_g5="COMPLETED", pdf=True):
    states = {"current": initial}
    events = []
    receipt = admitted(tmp_path)

    def read(_id):
        assert _id == receipt.document_id
        return (SimpleNamespace(current_state=states["current"], ast_hash="ast-code")
                if states["current"] else None)

    def ocr(path, root):
        events.append("OCR")
        assert path == receipt.inbox_path and root == tmp_path
        states["current"] = after_ocr

    def g3(doc_id, ast_hash):
        events.append("G3")
        assert doc_id == receipt.document_id and ast_hash == "ast-code"
        states["current"] = after_g3

    def g5(doc_id, ast_hash):
        events.append("G5")
        assert doc_id == receipt.document_id and ast_hash == "ast-code"
        states["current"] = after_g5
        if pdf:
            out = tmp_path / "output"
            out.mkdir(exist_ok=True)
            (out / f"translated_{doc_id}.pdf").write_bytes(b"%PDF-1.7\nfinished-pdf")

    monkeypatch.setattr(product, "_read_status", read)
    monkeypatch.setattr(product, "_ingest", ocr)
    monkeypatch.setattr(product, "_run_g3", g3)
    monkeypatch.setattr(product, "_run_g5", g5)
    monkeypatch.delenv("COMPILER_OUTPUT_DIR", raising=False)
    return receipt, events, states


def test_foreground_runs_ocr_g3_g5_then_requires_published_pdf(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path)
    result = product.run_admitted_pdf(receipt, tmp_path)
    assert events == ["OCR", "G3", "G5"]
    assert result.execution_status == "COMPLETED"
    assert result.scientific_status == "NOT_CERTIFIED"
    assert result.output_pdf.is_file()


def test_foreground_resumes_processing_without_repeat_ocr(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path, initial="PROCESSING")
    product.run_admitted_pdf(receipt, tmp_path)
    assert events == ["G3", "G5"]


def test_foreground_resumes_ready_for_assembly_without_llm(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path, initial="READY_FOR_ASSEMBLY")
    product.run_admitted_pdf(receipt, tmp_path)
    assert events == ["G5"]


def test_foreground_fails_after_ocr_error_no_false_success(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path, after_ocr=None)
    with pytest.raises(product.PDFProductError, match="OCR_NO_FSM_STATE"):
        product.run_admitted_pdf(receipt, tmp_path)
    assert events == ["OCR"]


def test_foreground_fails_on_incomplete_g3_before_g5(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path, after_g3="PROCESSING")
    with pytest.raises(product.PDFProductError, match="STAGE_NOT_COMPLETE"):
        product.run_admitted_pdf(receipt, tmp_path)
    assert events == ["OCR", "G3"]


def test_foreground_fails_when_g5_did_not_publish(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path, pdf=False)
    with pytest.raises(product.PDFProductError, match="WITHOUT_PUBLISHED_PDF"):
        product.run_admitted_pdf(receipt, tmp_path)
    assert events == ["OCR", "G3", "G5"]


def test_foreground_rejects_unrelated_state_without_work(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path, initial="FAILED_FATAL")
    with pytest.raises(product.PDFProductError, match="UNSUPPORTED_STATE"):
        product.run_admitted_pdf(receipt, tmp_path)
    assert events == []


def test_foreground_rejects_invalid_document_id(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path)
    bad = PDFInboxSubmission("untrusted-id", receipt.inbox_path, False)
    with pytest.raises(product.PDFProductError, match="INVALID_DOCUMENT_ID"):
        product.run_admitted_pdf(bad, tmp_path)
    assert events == []


def test_foreground_requires_pdf_header_even_when_fsm_completed(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path, initial="COMPLETED")
    out = tmp_path / "output"; out.mkdir()
    (out / f"translated_{receipt.document_id}.pdf").write_bytes(b"not a pdf in the output")
    with pytest.raises(product.PDFProductError, match="INVALID_PUBLISHED_PDF"):
        product.run_admitted_pdf(receipt, tmp_path)
    assert events == []


def test_preflight_rejects_custom_inbox_before_io(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(product.PDFProductError, match="INBOX_MISMATCH"):
        product.preflight_product_run(tmp_path, tmp_path / "wrong")


def test_preflight_rejects_missing_sqlite_without_creating_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("APP_ROOT", raising=False)
    from infra.db import connection
    monkeypatch.setattr(connection, "resolve_sqlite_path",
                        lambda rel: str(tmp_path / rel))
    with pytest.raises(product.PDFProductError, match="DB_NOT_INITIALIZED"):
        product.preflight_product_run(tmp_path, tmp_path / "data" / "inbox")
    assert not (tmp_path / "infra" / "db").exists()


def test_preflight_rejects_missing_compiler(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("APP_ROOT", raising=False)
    state = tmp_path / "infra" / "db"; state.mkdir(parents=True)
    for db in ("fsm.db", "queue.db", "materialized.db"):
        (state / db).write_bytes(b"dummy")
    from infra.db import connection
    monkeypatch.setattr(connection, "resolve_sqlite_path", lambda rel: str(tmp_path / rel))
    monkeypatch.setattr(product.shutil, "which", lambda _: None)
    with pytest.raises(product.PDFProductError, match="TECTONIC_UNAVAILABLE"):
        product.preflight_product_run(tmp_path, tmp_path / "data" / "inbox")


def test_g3_exception_is_operational_error(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path)
    def broken_g3(*args):
        raise RuntimeError("provider failure")
    monkeypatch.setattr(product, "_run_g3", broken_g3)
    with pytest.raises(product.PDFProductError, match="PDF_RUN_G3_EXECUTION_FAILED"):
        product.run_admitted_pdf(receipt, tmp_path)
    assert events == ["OCR"]


def test_g5_exception_is_operational_error(tmp_path, monkeypatch):
    receipt, events, _ = mock_pipeline(monkeypatch, tmp_path)
    def broken_g5(*args):
        raise RuntimeError("tectonic failure")
    monkeypatch.setattr(product, "_run_g5", broken_g5)
    with pytest.raises(product.PDFProductError, match="PDF_RUN_G5_EXECUTION_FAILED"):
        product.run_admitted_pdf(receipt, tmp_path)
    assert events == ["OCR", "G3"]
