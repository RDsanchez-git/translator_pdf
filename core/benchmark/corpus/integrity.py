"""Verificación de integridad física de la baseline.

NADR-F17BIS-26 §5.2 R6-R10.

Functional Core: funciones puras sin I/O. Reciben datos ya cargados
(hashes, secuencias de documentos) y verifican correspondencia.
El Imperative Shell (run_regression.py) lee el filesystem y llama
a estas funciones.

Reutilización (ENGINEERING_PRINCIPLES §I):
- ManifestFingerprintCalculator.compute_hash() de core/benchmark/corpus/services.py
- compute_sha256_stream() de core/shared/crypto.py (usada por el caller)
"""
from __future__ import annotations

from typing import Sequence

from core.benchmark.corpus.models import CorpusDocumentMetadata, CorpusVersion
from core.benchmark.corpus.services import ManifestFingerprintCalculator


# ── Errores de dominio ────────────────────────────────────────────────────────


class BaselineIntegrityError(Exception):
    """Error de integridad de la baseline (NADR-F17BIS-26 §5.6 R23-R25).

    Un fallo de integridad de la baseline se distingue semánticamente de
    una divergencia producida por el production pipeline. La detección de
    un fallo de integridad no se interpreta como regresión científica.
    """


class ManifestHashMismatchError(BaselineIntegrityError):
    """manifest_hash declarado difiere del recalculado (NADR-26 §5.2 R8)."""

    def __init__(self, expected: str, actual: str) -> None:
        self.expected_hash = expected
        self.actual_hash = actual
        super().__init__(
            f"Manifest hash mismatch: declared '{expected[:16]}...' "
            f"but recalculated '{actual[:16]}...'. "
            f"The manifest may have been tampered with."
        )


class PdfIntegrityError(BaselineIntegrityError):
    """sha256 de PDF difiere del declarado en el manifest (NADR-26 §5.2 R9)."""

    def __init__(self, document_id: str, expected: str, actual: str) -> None:
        self.document_id = document_id
        self.expected_sha256 = expected
        self.actual_sha256 = actual
        super().__init__(
            f"PDF integrity violation for '{document_id}': "
            f"manifest declares sha256 '{expected[:16]}...' "
            f"but file has '{actual[:16]}...'. "
            f"The PDF may have been tampered with."
        )


class PdfMissingError(BaselineIntegrityError):
    """PDF ausente requerido por el manifest (NADR-26 §5.3 R12)."""

    def __init__(self, document_id: str, pdf_path: str) -> None:
        self.document_id = document_id
        self.pdf_path = pdf_path
        super().__init__(
            f"PDF missing for '{document_id}': expected at '{pdf_path}'. "
            f"The baseline is incomplete and cannot be consumed."
        )

class GTUnreadableError(BaselineIntegrityError):
    """Ground Truth ilegible o corrupto (NADR-F17BIS-26 §5.3 R13).

    Un artefacto ilegible, corrupto o físicamente inconsistente con su
    identidad declarada MUST NOT ser tratado como un artefacto válido
    de la baseline.
    """

    def __init__(self, document_id: str, reason: str) -> None:
        self.document_id = document_id
        self.reason = reason
        super().__init__(
            f"Ground Truth unreadable for '{document_id}': {reason}. "
            f"The baseline is corrupt and cannot be consumed."
        )

# ── Funciones puras de verificación ──────────────────────────────────────────


def verify_manifest_hash(
    declared_hash: str,
    version: CorpusVersion,
    documents: Sequence[CorpusDocumentMetadata],
) -> None:
    """Verifica manifest_hash declarado contra recalculado.

    NADR-F17BIS-26 §5.2 R8: La integridad del manifest de la baseline
    MUST ser verificable antes de utilizarlo como fuente de referencia.

    NADR-F17BIS-26 §5.2 R10: Una discrepancia entre la identidad esperada
    y la observada MUST impedir el consumo de la baseline.

    Función pura: recibe datos ya cargados, no lee disco.
    Reutiliza ManifestFingerprintCalculator.compute_hash().

    Args:
        declared_hash: manifest_hash declarado en el manifest cargado.
        version: Versión del corpus.
        documents: Secuencia de documentos del manifest.

    Raises:
        ManifestHashMismatchError: Si los hashes no coinciden.
    """
    recalculated = ManifestFingerprintCalculator.compute_hash(
        version=version,
        documents=list(documents),
    )
    if recalculated != declared_hash:
        raise ManifestHashMismatchError(
            expected=declared_hash,
            actual=recalculated,
        )


def verify_pdf_hash(
    document_id: str,
    expected_sha256: str,
    actual_sha256: str,
) -> None:
    """Verifica sha256 de un PDF contra el declarado en el manifest.

    NADR-F17BIS-26 §5.2 R9: La identidad criptográfica declarada por la
    baseline MUST corresponder a la identidad criptográfica observada en
    los artefactos materializados.

    NADR-F17BIS-26 §5.2 R10: Una discrepancia MUST impedir el consumo.

    Función pura: recibe hashes ya calculados, no lee disco.

    Args:
        document_id: Identificador del documento.
        expected_sha256: sha256 declarado en el manifest.
        actual_sha256: sha256 calculado del archivo PDF.

    Raises:
        PdfIntegrityError: Si los hashes no coinciden.
    """
    if actual_sha256 != expected_sha256:
        raise PdfIntegrityError(
            document_id=document_id,
            expected=expected_sha256,
            actual=actual_sha256,
        )