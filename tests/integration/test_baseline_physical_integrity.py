"""Tests de orquestación de verificación de integridad física.

NADR-F17BIS-26 §5.2 R6-R10.

Tests de integración que verifican el flujo completo de verificación
de integridad física: manifest_hash + sha256 de PDFs.
Requieren filesystem temporal (tmp_path).
"""
from __future__ import annotations

import pathlib

import pytest

from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.integrity import (
    ManifestHashMismatchError,
    PdfIntegrityError,
    PdfMissingError,
)
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusManifest,
    CorpusVersion,
    DocumentFingerprint,
)
from core.benchmark.corpus.services import ManifestFingerprintCalculator
from core.shared.crypto import compute_sha256
from tools.evaluation.run_regression import verify_baseline_physical_integrity


def _make_valid_baseline(
    tmp_path: pathlib.Path,
) -> tuple[pathlib.Path, CorpusManifest, str]:
    """Crea una baseline válida con PDFs y manifest con hashes correctos.

    Returns:
        Tupla (pdf_dir, manifest, manifest_hash).
    """
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()

    pdf_content = b"%PDF-1.4 test content for integrity verification"
    (pdf_dir / "doc_01.pdf").write_bytes(pdf_content)

    pdf_sha256 = compute_sha256(pdf_content)

    doc = CorpusDocumentMetadata(
        document_id="doc_01",
        fingerprint=DocumentFingerprint(sha256=pdf_sha256),
        traits=frozenset({ExtractionChallengeTrait.HEAVY_MATH}),
        page_count=1,
    )

    version = CorpusVersion(value="test-v1")
    manifest = CorpusManifest(
        corpus_version=version,
        documents=[doc],
    )
    manifest_hash = ManifestFingerprintCalculator.compute_hash(
        version=version,
        documents=[doc],
    )

    return pdf_dir, manifest, manifest_hash


@pytest.mark.integration
class TestVerifyBaselinePhysicalIntegrity:
    """NADR-F17BIS-26 §5.2 R6-R10: Integridad física de la baseline."""

    def test_passes_with_valid_baseline(self, tmp_path: pathlib.Path) -> None:
        """Baseline válida → no lanza excepción."""
        pdf_dir, manifest, manifest_hash = _make_valid_baseline(tmp_path)
        verify_baseline_physical_integrity(manifest, manifest_hash, pdf_dir)

    def test_raises_on_manifest_hash_mismatch(self, tmp_path: pathlib.Path) -> None:
        """R8: manifest_hash incorrecto → ManifestHashMismatchError."""
        pdf_dir, manifest, _ = _make_valid_baseline(tmp_path)

        with pytest.raises(ManifestHashMismatchError, match="Manifest hash mismatch"):
            verify_baseline_physical_integrity(manifest, "0" * 64, pdf_dir)

    def test_raises_on_pdf_missing(self, tmp_path: pathlib.Path) -> None:
        """R6: PDF ausente → PdfMissingError."""
        pdf_dir, manifest, manifest_hash = _make_valid_baseline(tmp_path)
        (pdf_dir / "doc_01.pdf").unlink()

        with pytest.raises(PdfMissingError, match="PDF missing"):
            verify_baseline_physical_integrity(manifest, manifest_hash, pdf_dir)

    def test_raises_on_pdf_tampered(self, tmp_path: pathlib.Path) -> None:
        """R9: PDF mutado → PdfIntegrityError."""
        pdf_dir, manifest, manifest_hash = _make_valid_baseline(tmp_path)
        (pdf_dir / "doc_01.pdf").write_bytes(b"TAMPERED CONTENT")

        with pytest.raises(PdfIntegrityError, match="PDF integrity violation"):
            verify_baseline_physical_integrity(manifest, manifest_hash, pdf_dir)