"""Adaptador de admisión PDF para el OCR Router existente.

Este módulo no interpreta el PDF, no crea tareas G3 y no inicia inferencia.
La identidad se calcula sobre los bytes *copiados* y coincide con
OCRRouterDaemon._process_document(). Un enlace duro dentro del inbox
publica únicamente archivos completos, sin reemplazar una admisión existente.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import tempfile


class PDFInboxSubmissionError(RuntimeError):
    """La entrada no fue publicada de forma segura en el inbox."""


@dataclass(frozen=True, slots=True)
class PDFInboxSubmission:
    document_id: str
    inbox_path: Path
    already_present: bool


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def submit_pdf_to_inbox(source: Path, inbox_dir: Path) -> PDFInboxSubmission:
    """Admite un PDF por SHA-256 sin exponer archivos a medio copiar.

    Solo confirma que el archivo está en el inbox; NO significa que haya
    sido aceptado por el OCR Router, traducido ni ensamblado como PDF.

    La publicación usa hard link de un temporal completo al nombre final:
    `os.link` falla de forma atómica si ese nombre ya existe, por lo que no
    se sobrescribe una solicitud previa. El temporal y el destino están en
    el mismo directorio/filesystem. En un volumen sin hard links se falla
    explícitamente, en lugar de recurrir a un overwrite inseguro.
    """
    source = Path(source).expanduser()
    inbox_dir = Path(inbox_dir).expanduser()

    if not source.is_file():
        raise PDFInboxSubmissionError(f"PDF_INBOX_SOURCE_NOT_FILE: {source}")
    if source.suffix.lower() != ".pdf":
        raise PDFInboxSubmissionError(f"PDF_INBOX_SOURCE_NOT_PDF: {source}")

    inbox_dir.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_name = tempfile.mkstemp(
        prefix=".pdf-admission-", suffix=".partial", dir=inbox_dir
    )
    temp_path = Path(temp_name)
    try:
        digest = hashlib.sha256()
        bytes_copied = 0
        with os.fdopen(temp_fd, "wb") as output_stream, source.open("rb") as input_stream:
            for block in iter(lambda: input_stream.read(1024 * 1024), b""):
                digest.update(block)
                output_stream.write(block)
                bytes_copied += len(block)
            output_stream.flush()
            os.fsync(output_stream.fileno())

        if bytes_copied == 0:
            raise PDFInboxSubmissionError("PDF_INBOX_EMPTY_SOURCE")

        document_id = digest.hexdigest()
        destination = inbox_dir / f"{document_id}.pdf"
        try:
            os.link(temp_path, destination)
            already_present = False
        except FileExistsError:
            # No se asume que el nombre contenido en el inbox es honesto.
            try:
                existing_hash = _sha256_file(destination)
            except OSError as exc:
                raise PDFInboxSubmissionError(
                    "PDF_INBOX_EXISTING_FILE_UNVERIFIABLE"
                ) from exc
            if existing_hash != document_id:
                raise PDFInboxSubmissionError("PDF_INBOX_EXISTING_FILE_HASH_MISMATCH")
            already_present = True
        except OSError as exc:
            raise PDFInboxSubmissionError(
                "PDF_INBOX_ATOMIC_PUBLISH_UNAVAILABLE: " + str(exc)
            ) from exc

        return PDFInboxSubmission(document_id, destination, already_present)
    finally:
        temp_path.unlink(missing_ok=True)
