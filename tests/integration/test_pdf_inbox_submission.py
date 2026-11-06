"""Pruebas de frontera del filesystem con PDF real; sin SQLite, Docker ni LLM."""

import hashlib
import os
from pathlib import Path

import fitz
import pytest

from apps.cli.pdf_inbox import PDFInboxSubmissionError, submit_pdf_to_inbox

pytestmark = pytest.mark.integration  # Requiere PDF real y filesystem temporal.


@pytest.fixture
def pdf_bytes() -> bytes:
    document = fitz.open()
    try:
        page = document.new_page()
        page.insert_text((72, 72), "scientific content example")
        return document.tobytes()
    finally:
        document.close()


def test_atomic_submission_uses_ocr_byte_identity(tmp_path: Path, pdf_bytes: bytes) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(pdf_bytes)
    inbox = tmp_path / "data" / "inbox"

    receipt = submit_pdf_to_inbox(source, inbox)

    assert receipt.document_id == hashlib.sha256(pdf_bytes).hexdigest()
    assert receipt.inbox_path == inbox / f"{receipt.document_id}.pdf"
    assert receipt.inbox_path.read_bytes() == pdf_bytes
    assert not receipt.already_present
    assert not list(inbox.glob("*.partial"))
    assert not list(inbox.glob(".pdf-admission-*"))


def test_identical_pdf_does_not_overwrite_existing_inbox_item(tmp_path: Path, pdf_bytes: bytes) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(pdf_bytes)
    inbox = tmp_path / "inbox"

    first = submit_pdf_to_inbox(source, inbox)
    second = submit_pdf_to_inbox(source, inbox)

    assert first.document_id == second.document_id
    assert second.already_present
    assert first.inbox_path.read_bytes() == pdf_bytes
    assert len(list(inbox.glob("*.pdf"))) == 1


def test_named_collision_with_different_content_fails_closed(tmp_path: Path, pdf_bytes: bytes) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(pdf_bytes)
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    expected_name = hashlib.sha256(pdf_bytes).hexdigest() + ".pdf"
    (inbox / expected_name).write_bytes(b"not the same PDF")

    with pytest.raises(PDFInboxSubmissionError, match="HASH_MISMATCH"):
        submit_pdf_to_inbox(source, inbox)
    assert (inbox / expected_name).read_bytes() == b"not the same PDF"
    assert not list(inbox.glob(".pdf-admission-*"))


def test_rejects_non_pdf_filename_without_copying(tmp_path: Path, pdf_bytes: bytes) -> None:
    source = tmp_path / "paper.txt"
    source.write_bytes(pdf_bytes)
    inbox = tmp_path / "inbox"

    with pytest.raises(PDFInboxSubmissionError, match="NOT_PDF"):
        submit_pdf_to_inbox(source, inbox)
    assert not inbox.exists()


def test_empty_input_not_published(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"")
    inbox = tmp_path / "inbox"

    with pytest.raises(PDFInboxSubmissionError, match="EMPTY_SOURCE"):
        submit_pdf_to_inbox(source, inbox)
    assert not list(inbox.glob("*.pdf"))
    assert not list(inbox.glob(".pdf-admission-*"))


def test_no_nonatomic_fallback_if_hard_links_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pdf_bytes: bytes
) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(pdf_bytes)
    inbox = tmp_path / "inbox"

    def fail_link(source: os.PathLike[str], destination: os.PathLike[str]) -> None:
        raise OSError("hard links unsupported")

    monkeypatch.setattr(os, "link", fail_link)
    with pytest.raises(PDFInboxSubmissionError, match="ATOMIC_PUBLISH_UNAVAILABLE"):
        submit_pdf_to_inbox(source, inbox)
    assert not list(inbox.glob("*.pdf"))
    assert not list(inbox.glob(".pdf-admission-*"))


def test_cli_translate_never_invokes_legacy_r1_pipeline(
    tmp_path: Path, pdf_bytes: bytes, monkeypatch: pytest.MonkeyPatch
) -> None:
    from argparse import Namespace
    from unittest.mock import Mock
    import apps.cli.main as cli

    source = tmp_path / "paper.pdf"
    source.write_bytes(pdf_bytes)
    inbox = tmp_path / "inbox"
    forbidden_legacy = Mock(side_effect=AssertionError("R1 must not execute"))
    monkeypatch.setattr(cli, "handle_translate_async", forbidden_legacy)

    cli.handle_translate(Namespace(file_path=str(source), job_id=None, inbox_dir=str(inbox)))

    forbidden_legacy.assert_not_called()
    assert list(inbox.glob("*.pdf"))


def test_cli_legacy_job_id_is_rejected_before_writing(
    tmp_path: Path, pdf_bytes: bytes
) -> None:
    from argparse import Namespace
    import apps.cli.main as cli

    source = tmp_path / "paper.pdf"
    source.write_bytes(pdf_bytes)
    inbox = tmp_path / "inbox"
    with pytest.raises(SystemExit) as raised:
        cli.handle_translate(Namespace(file_path=str(source), job_id="legacy_alias", inbox_dir=str(inbox)))

    assert raised.value.code == 2
    assert not inbox.exists()
