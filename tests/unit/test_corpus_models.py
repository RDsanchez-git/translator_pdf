"""Tests de validación de dominio para modelos de corpus (Wave 2.1 Fase 3).

Verifica NADR-F17BIS-17 §5.1 R1-R4:
- Contratos de dominio formalmente definidos y validados
- Validación fail-fast en construcción del objeto de dominio
- Inyectividad del encoding: ':' prohibido en document_id
- Sentinel: document_id es obligatorio (no tiene sentinel)

Tasks 2.1.1 (validación), 2.1.2 (tests de fail-fast), 2.1.3 (documentación).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusManifest,
    CorpusVersion,
    DocumentFingerprint,
)

from core.benchmark.corpus.dtos import RawDocumentEntryDTO


# SHA-256 de cadena vacía (hash determinista conocido)
_VALID_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _make_fingerprint(sha256: str = _VALID_SHA256) -> DocumentFingerprint:
    return DocumentFingerprint(sha256=sha256)


def _make_metadata(
    doc_id: str = "doc-1",
    oracle_hash: str | None = None,
    gt_state: str | None = None,
) -> CorpusDocumentMetadata:
    """Factory helper para construir CorpusDocumentMetadata en tests."""
    return CorpusDocumentMetadata(
        document_id=doc_id,
        fingerprint=_make_fingerprint(),
        traits=frozenset({ExtractionChallengeTrait.NATIVE_PDF}),
        page_count=1,
        oracle_hash=oracle_hash,
        ground_truth_state=gt_state,
    )


class TestDocumentIdDomainContract:
    """Task 2.1.2: Tests de fail-fast para document_id inválido.

    NADR-F17BIS-17 §5.1 R3-R4: la validación de dominio MUST aplicarse
    mediante fail-fast (rechazo explícito en construcción), no mediante
    advertencias silenciosas.
    """

    def test_valid_document_id_with_alphanumeric_and_hyphens(self) -> None:
        """document_id con caracteres alfanuméricos y guiones se acepta."""
        metadata = _make_metadata("paper_ieee_2024")
        assert metadata.document_id == "paper_ieee_2024"

    def test_valid_document_id_with_dots_and_underscores(self) -> None:
        """document_id con puntos y guiones bajos se acepta."""
        metadata = _make_metadata("doc.v2_final")
        assert metadata.document_id == "doc.v2_final"

    def test_valid_document_id_with_spaces(self) -> None:
        """document_id con espacios se acepta (no contienen ':')."""
        metadata = _make_metadata("my document 01")
        assert metadata.document_id == "my document 01"

    def test_valid_document_id_single_char(self) -> None:
        """document_id de un solo carácter es válido (min_length=1)."""
        metadata = _make_metadata("a")
        assert metadata.document_id == "a"

    def test_colon_in_middle_of_document_id_raises_validation_error(self) -> None:
        """Fail-fast: document_id con ':' en el medio lanza ValidationError."""
        with pytest.raises(ValidationError, match="document_id"):
            _make_metadata("doc:invalid")

    def test_colon_at_start_of_document_id_raises_validation_error(self) -> None:
        """Fail-fast: ':' al inicio también es rechazado."""
        with pytest.raises(ValidationError, match="document_id"):
            _make_metadata(":doc")

    def test_colon_at_end_of_document_id_raises_validation_error(self) -> None:
        """Fail-fast: ':' al final también es rechazado."""
        with pytest.raises(ValidationError, match="document_id"):
            _make_metadata("doc:")

    def test_multiple_colons_in_document_id_raises_validation_error(self) -> None:
        """Fail-fast: múltiples ':' también son rechazados."""
        with pytest.raises(ValidationError, match="document_id"):
            _make_metadata("a:b:c")

    def test_only_colon_as_document_id_raises_validation_error(self) -> None:
        """Fail-fast: document_id que es solo ':' es rechazado."""
        with pytest.raises(ValidationError, match="document_id"):
            _make_metadata(":")

    def test_empty_document_id_raises_validation_error(self) -> None:
        """Fail-fast: document_id vacío es rechazado (min_length=1)."""
        with pytest.raises(ValidationError, match="document_id"):
            _make_metadata("")


class TestGroundTruthStateDomainContract:
    """Tests de contrato de dominio para ground_truth_state (DF-01, Wave 2.4).

    NADR-F17BIS-17 §5.1 R3-R4: la validación de dominio MUST aplicarse
    mediante fail-fast (rechazo explícito en construcción), no mediante
    advertencias silenciosas.

    ground_truth_state tiene el mismo contrato que document_id y node_id
    porque participa en el framing de manifest_hash. Cierre de asimetría
    defensiva con Waves 2.1 y 2.2.
    """

    def test_ground_truth_state_none_is_valid(self) -> None:
        """ground_truth_state=None es válido (sentinel DRAFT según DF-13)."""
        metadata = CorpusDocumentMetadata(
            document_id="doc-1",
            fingerprint=DocumentFingerprint(sha256=_VALID_SHA256),
            traits=frozenset({ExtractionChallengeTrait.NATIVE_PDF}),
            page_count=1,
            ground_truth_state=None,
        )
        assert metadata.ground_truth_state is None

    def test_ground_truth_state_with_valid_enum_value(self) -> None:
        """ground_truth_state con valor canónico del enum se acepta."""
        for state in ("draft", "audited", "validated", "sealed"):
            metadata = CorpusDocumentMetadata(
                document_id="doc-1",
                fingerprint=DocumentFingerprint(sha256=_VALID_SHA256),
                traits=frozenset({ExtractionChallengeTrait.NATIVE_PDF}),
                page_count=1,
                ground_truth_state=state,
            )
            assert metadata.ground_truth_state == state

    def test_ground_truth_state_with_colon_raises_validation_error(self) -> None:
        """Fail-fast: ground_truth_state con ':' lanza ValidationError."""
        with pytest.raises(ValidationError, match="ground_truth_state"):
            CorpusDocumentMetadata(
                document_id="doc-1",
                fingerprint=DocumentFingerprint(sha256=_VALID_SHA256),
                traits=frozenset({ExtractionChallengeTrait.NATIVE_PDF}),
                page_count=1,
                ground_truth_state="sealed:invalid",
            )

    def test_ground_truth_state_empty_string_raises_validation_error(self) -> None:
        """Fail-fast: ground_truth_state vacío es rechazado (min_length=1)."""
        with pytest.raises(ValidationError, match="ground_truth_state"):
            CorpusDocumentMetadata(
                document_id="doc-1",
                fingerprint=DocumentFingerprint(sha256=_VALID_SHA256),
                traits=frozenset({ExtractionChallengeTrait.NATIVE_PDF}),
                page_count=1,
                ground_truth_state="",
            )

    def test_ground_truth_state_with_multiple_colons_raises_validation_error(self) -> None:
        """Fail-fast: múltiples ':' también son rechazados."""
        with pytest.raises(ValidationError, match="ground_truth_state"):
            CorpusDocumentMetadata(
                document_id="doc-1",
                fingerprint=DocumentFingerprint(sha256=_VALID_SHA256),
                traits=frozenset({ExtractionChallengeTrait.NATIVE_PDF}),
                page_count=1,
                ground_truth_state="a:b:c",
            )

    def test_dto_ground_truth_state_with_colon_raises_validation_error(self) -> None:
        """Fail-fast en DTO de frontera: ground_truth_state con ':' rechazado.

        Verifica que el contrato se aplica en ambos puntos (modelo de dominio
        y DTO de frontera), garantizando Fail-Fast en la frontera más temprana.
        """
        with pytest.raises(ValidationError, match="ground_truth_state"):
            RawDocumentEntryDTO(
                document_id="doc-1",
                sha256=_VALID_SHA256,
                traits=["native_pdf"],
                page_count=1,
                ground_truth_state="sealed:invalid",
            )


class TestCorpusDocumentMetadataInvariants:
    """Tests de invariantes del modelo de dominio."""

    def test_metadata_is_immutable(self) -> None:
        """Inmutabilidad: intentar mutar un campo lanza error (frozen=True)."""
        metadata = _make_metadata("doc-1")
        with pytest.raises(ValidationError):
            metadata.document_id = "mutated"  # type: ignore[misc]

    def test_metadata_accepts_none_oracle_hash(self) -> None:
        """oracle_hash=None es válido (documento sin oráculo sellado)."""
        metadata = _make_metadata("doc-1", oracle_hash=None)
        assert metadata.oracle_hash is None

    def test_metadata_accepts_explicit_oracle_hash(self) -> None:
        """oracle_hash con valor explícito es válido."""
        metadata = _make_metadata("doc-1", oracle_hash="abc123def456")
        assert metadata.oracle_hash == "abc123def456"

    def test_metadata_accepts_none_ground_truth_state(self) -> None:
        """ground_truth_state=None es válido (interpretado como DRAFT)."""
        metadata = _make_metadata("doc-1", gt_state=None)
        assert metadata.ground_truth_state is None

    def test_metadata_accepts_sealed_ground_truth_state(self) -> None:
        """ground_truth_state='sealed' es válido."""
        metadata = _make_metadata("doc-1", gt_state="sealed")
        assert metadata.ground_truth_state == "sealed"

    def test_page_count_must_be_positive(self) -> None:
        """page_count debe ser > 0."""
        with pytest.raises(ValidationError, match="page_count"):
            CorpusDocumentMetadata(
                document_id="doc-1",
                fingerprint=_make_fingerprint(),
                traits=frozenset({ExtractionChallengeTrait.NATIVE_PDF}),
                page_count=0,
            )

    def test_traits_must_not_be_empty(self) -> None:
        """traits debe tener al menos un elemento."""
        with pytest.raises(ValidationError, match="traits"):
            CorpusDocumentMetadata(
                document_id="doc-1",
                fingerprint=_make_fingerprint(),
                traits=frozenset(),
                page_count=1,
            )


class TestDocumentFingerprintInvariants:
    """Tests de invariante de DocumentFingerprint (hex lowercase)."""

    def test_valid_sha256_accepted(self) -> None:
        """SHA-256 hex lowercase válido se acepta."""
        fp = DocumentFingerprint(sha256=_VALID_SHA256)
        assert fp.sha256 == _VALID_SHA256

    def test_uppercase_sha256_rejected(self) -> None:
        """SHA-256 en mayúsculas es rechazado.

        SOTA FIX: Pydantic V2 wrappea el ValueError del __post_init__ en un
        ValidationError. Capturamos ambos para compatibilidad. El regex acepta
        tanto 'hexadecimal' como 'hexadecimales' para robustez futura.
        """
        with pytest.raises((ValueError, ValidationError), match=r"hexadecimales? en minúsculas"):
            DocumentFingerprint(sha256=_VALID_SHA256.upper())

    def test_non_hex_sha256_rejected(self) -> None:
        """String no-hexadecimal es rechazado.

        SOTA FIX: Mismo patrón que test_uppercase_sha256_rejected.
        """
        with pytest.raises((ValueError, ValidationError), match=r"hexadecimales? en minúsculas"):
            DocumentFingerprint(sha256="g" * 64)

    def test_fingerprint_is_immutable(self) -> None:
        """DocumentFingerprint es inmutable (frozen=True, slots=True)."""
        fp = DocumentFingerprint(sha256=_VALID_SHA256)
        with pytest.raises(AttributeError):
            fp.sha256 = "0" * 64  # type: ignore[misc]


class TestCorpusManifestInvariants:
    """Tests de invariante del Aggregate Root CorpusManifest."""

    def test_manifest_construction_with_valid_documents(self) -> None:
        """CorpusManifest se construye con documentos válidos."""
        manifest = CorpusManifest(
            corpus_version=CorpusVersion(value="v1.0"),
            documents=[_make_metadata("doc-1"), _make_metadata("doc-2")],
        )
        assert manifest.corpus_version.value == "v1.0"
        assert len(manifest.documents) == 2

    def test_manifest_rejects_document_with_colon_in_id(self) -> None:
        """CorpusManifest propaga el fail-fast de document_id con ':'."""
        with pytest.raises(ValidationError, match="document_id"):
            CorpusManifest(
                corpus_version=CorpusVersion(value="v1.0"),
                documents=[_make_metadata("doc:invalid")],
            )

    def test_manifest_is_immutable(self) -> None:
        """CorpusManifest es inmutable (frozen=True)."""
        manifest = CorpusManifest(
            corpus_version=CorpusVersion(value="v1.0"),
            documents=[_make_metadata("doc-1")],
        )
        with pytest.raises(ValidationError):
            manifest.documents = []  # type: ignore[misc]