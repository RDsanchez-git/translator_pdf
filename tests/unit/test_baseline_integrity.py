"""Tests de verificación de integridad de la baseline (NADR-F17BIS-26 §5.2 R6-R10).

Tests unitarios para las funciones puras del core.
No requieren filesystem ni PDFs reales.
"""
from __future__ import annotations

import pytest

from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.integrity import (
    ManifestHashMismatchError,
    PdfIntegrityError,
    verify_manifest_hash,
    verify_pdf_hash,
)
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusVersion,
    DocumentFingerprint,
)
from core.benchmark.corpus.services import ManifestFingerprintCalculator


def _make_metadata(doc_id: str, sha256: str = "a" * 64) -> CorpusDocumentMetadata:
    """Crea metadata de documento de prueba."""
    return CorpusDocumentMetadata(
        document_id=doc_id,
        fingerprint=DocumentFingerprint(sha256=sha256),
        traits=frozenset({ExtractionChallengeTrait.HEAVY_MATH}),
        page_count=1,
    )


@pytest.mark.unit
class TestVerifyManifestHash:
    """NADR-F17BIS-26 §5.2 R8: manifest_hash declarado == recalculado."""

    def test_passes_when_hash_matches(self) -> None:
        """Hash correcto → no lanza excepción."""
        docs = [_make_metadata("doc_01")]
        version = CorpusVersion(value="test-v1")
        expected_hash = ManifestFingerprintCalculator.compute_hash(
            version=version, documents=docs
        )
        verify_manifest_hash(
            declared_hash=expected_hash,
            version=version,
            documents=docs,
        )

    def test_raises_on_hash_mismatch(self) -> None:
        """Hash incorrecto → ManifestHashMismatchError."""
        docs = [_make_metadata("doc_01")]
        version = CorpusVersion(value="test-v1")
        with pytest.raises(ManifestHashMismatchError, match="Manifest hash mismatch"):
            verify_manifest_hash(
                declared_hash="0" * 64,
                version=version,
                documents=docs,
            )

    def test_error_contains_both_hashes(self) -> None:
        """El mensaje de error contiene ambos hashes (truncados)."""
        docs = [_make_metadata("doc_01")]
        version = CorpusVersion(value="test-v1")
        with pytest.raises(ManifestHashMismatchError) as exc_info:
            verify_manifest_hash(
                declared_hash="0" * 64,
                version=version,
                documents=docs,
            )
        assert exc_info.value.expected_hash == "0" * 64
        assert exc_info.value.actual_hash != "0" * 64


@pytest.mark.unit
class TestVerifyPdfHash:
    """NADR-F17BIS-26 §5.2 R9: sha256 del PDF == sha256 del manifest."""

    def test_passes_when_hash_matches(self) -> None:
        """Hash correcto → no lanza excepción."""
        verify_pdf_hash(
            document_id="doc_01",
            expected_sha256="a" * 64,
            actual_sha256="a" * 64,
        )

    def test_raises_on_hash_mismatch(self) -> None:
        """Hash incorrecto → PdfIntegrityError."""
        with pytest.raises(PdfIntegrityError, match="PDF integrity violation"):
            verify_pdf_hash(
                document_id="doc_01",
                expected_sha256="a" * 64,
                actual_sha256="b" * 64,
            )

    def test_error_contains_document_id(self) -> None:
        """El mensaje de error contiene el document_id."""
        with pytest.raises(PdfIntegrityError) as exc_info:
            verify_pdf_hash(
                document_id="doc_42",
                expected_sha256="a" * 64,
                actual_sha256="b" * 64,
            )
        assert exc_info.value.document_id == "doc_42"
        assert exc_info.value.expected_sha256 == "a" * 64
        assert exc_info.value.actual_sha256 == "b" * 64