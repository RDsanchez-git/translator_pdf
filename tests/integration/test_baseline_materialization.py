"""
Baseline Materialization Tests (NADR-F17BIS-26 §5.1 R1-R5).

Verifica que verify_baseline_materialized() en run_regression.py
detecta correctamente la ausencia del directorio de PDFs y de PDFs
esperados antes de iniciar la evaluación.

Estos tests son de integración porque requieren filesystem temporal.
No ejecutan el pipeline de extracción ni consumen la baseline sellada.

NADR-F17BIS-26:
- R2: La baseline MUST estar físicamente materializada antes de la evaluación.
- R3: La materialización MUST conservar correspondencia verificable.
"""
from __future__ import annotations

import pathlib

import pytest

from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusManifest,
    CorpusVersion,
    DocumentFingerprint,
)
from tools.evaluation.run_regression import verify_baseline_materialized


def _make_manifest(doc_ids: list[str]) -> CorpusManifest:
    """Crea un manifest de prueba con los document_ids dados."""
    documents = [
        CorpusDocumentMetadata(
            document_id=doc_id,
            fingerprint=DocumentFingerprint(sha256="a" * 64),
            traits=frozenset({ExtractionChallengeTrait.HEAVY_MATH}),
            page_count=1,
        )
        for doc_id in doc_ids
    ]
    return CorpusManifest(
        corpus_version=CorpusVersion(value="test-v1"),
        documents=documents,
    )


def _create_pdf(pdf_dir: pathlib.Path, doc_id: str) -> None:
    """Crea un PDF dummy en el directorio dado."""
    (pdf_dir / f"{doc_id}.pdf").write_bytes(b"%PDF-1.4 dummy")


@pytest.mark.integration
class TestVerifyBaselineMaterialized:
    """NADR-F17BIS-26 §5.1 R2-R3: La baseline MUST estar materializada."""

    def test_passes_when_all_pdfs_present(
        self, tmp_path: pathlib.Path
    ) -> None:
        """R2-R3: Pasa cuando todos los PDFs están presentes."""
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()

        manifest = _make_manifest(["doc_01", "doc_02"])
        _create_pdf(pdf_dir, "doc_01")
        _create_pdf(pdf_dir, "doc_02")

        # No debe lanzar excepción
        verify_baseline_materialized(pdf_dir, manifest)

    def test_raises_when_pdf_dir_missing(
        self, tmp_path: pathlib.Path
    ) -> None:
        """R2: Lanza FileNotFoundError cuando el directorio de PDFs no existe."""
        pdf_dir = tmp_path / "nonexistent_pdfs"
        manifest = _make_manifest(["doc_01"])

        with pytest.raises(FileNotFoundError, match="PDF directory not found"):
            verify_baseline_materialized(pdf_dir, manifest)

    def test_raises_when_single_pdf_missing(
        self, tmp_path: pathlib.Path
    ) -> None:
        """R3: Lanza FileNotFoundError cuando falta un PDF esperado."""
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()

        manifest = _make_manifest(["doc_01", "doc_02"])
        _create_pdf(pdf_dir, "doc_01")
        # doc_02.pdf NO se crea

        with pytest.raises(FileNotFoundError, match="Missing PDFs"):
            verify_baseline_materialized(pdf_dir, manifest)

    def test_error_message_lists_all_missing_pdfs_sorted(
        self, tmp_path: pathlib.Path
    ) -> None:
        """R3: El mensaje de error lista todos los PDFs faltantes ordenados."""
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()

        manifest = _make_manifest(["doc_03", "doc_01", "doc_02"])
        _create_pdf(pdf_dir, "doc_01")
        # doc_02.pdf y doc_03.pdf NO se crean

        with pytest.raises(FileNotFoundError, match="doc_02.*doc_03"):
            verify_baseline_materialized(pdf_dir, manifest)

    def test_empty_manifest_passes_with_existing_dir(
        self, tmp_path: pathlib.Path
    ) -> None:
        """R2: Un manifest vacío pasa si el directorio de PDFs existe."""
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()

        manifest = _make_manifest([])

        # No debe lanzar excepción
        verify_baseline_materialized(pdf_dir, manifest)

    def test_extra_pdfs_in_dir_do_not_cause_failure(
        self, tmp_path: pathlib.Path
    ) -> None:
        """R3: PDFs extra en el directorio no causan fallo.

        La verificación de completitud de PDFs vs manifest es tarea
        de Task 1.2.3 (NADR-F17BIS-26 §5.3 R11-R15). Aquí solo se
        verifica que los PDFs esperados están presentes.
        """
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()

        manifest = _make_manifest(["doc_01"])
        _create_pdf(pdf_dir, "doc_01")
        _create_pdf(pdf_dir, "doc_extra")  # PDF no esperado

        # No debe lanzar excepción
        verify_baseline_materialized(pdf_dir, manifest)