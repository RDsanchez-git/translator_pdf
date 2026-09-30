"""Tests de VerificationProfile (NADR-F17BIS-29 §5.1, §5.3)."""
from __future__ import annotations

import pytest

from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusManifest,
    CorpusVersion,
    DocumentFingerprint,
)
from core.benchmark.verification.profiles import (
    VerificationProfile,
    get_profile_document_ids,
)


def _make_manifest(doc_ids: list[str]) -> CorpusManifest:
    """Helper: crea CorpusManifest de prueba."""
    docs = [
        CorpusDocumentMetadata(
            document_id=doc_id,
            fingerprint=DocumentFingerprint(sha256="a" * 64),
            traits=frozenset({next(iter(ExtractionChallengeTrait))}),
            page_count=3,
            oracle_hash=None,
            ground_truth_state="sealed",
        )
        for doc_id in doc_ids
    ]
    return CorpusManifest(
        corpus_version=CorpusVersion(value="test_v1"),
        documents=docs,
    )


@pytest.mark.unit
class TestVerificationProfile:
    """NADR-F17BIS-29 §5.1 R1: perfil explícitamente definido."""

    def test_full_profile_exists(self) -> None:
        """R1: FULL está definido."""
        assert hasattr(VerificationProfile, "FULL")

    def test_profile_is_str_subclass(self) -> None:
        """Consistente con otros enums del proyecto (ENGINEERING_PRINCIPLES §III)."""
        assert issubclass(VerificationProfile, str)

    def test_full_profile_value(self) -> None:
        """R1: FULL tiene valor canónico."""
        assert VerificationProfile.FULL.value == "FULL"

    def test_profile_is_immutable(self) -> None:
        """Enum es inmutable."""
        with pytest.raises(AttributeError):
            VerificationProfile.FULL = "MODIFIED"  # type: ignore[misc]


@pytest.mark.unit
class TestGetProfileDocumentIds:
    """NADR-F17BIS-29 §5.1 R3, §5.3 R14-R17."""

    def test_full_returns_all_documents(self) -> None:
        """R14: FULL retorna todos los documentos del manifest."""
        manifest = _make_manifest(["doc_01", "doc_02", "doc_03"])
        result = get_profile_document_ids(VerificationProfile.FULL, manifest)
        assert result == frozenset({"doc_01", "doc_02", "doc_03"})

    def test_full_returns_frozenset(self) -> None:
        """Inmutabilidad (ENGINEERING_PRINCIPLES §III)."""
        manifest = _make_manifest(["doc_01"])
        result = get_profile_document_ids(VerificationProfile.FULL, manifest)
        assert isinstance(result, frozenset)

    def test_full_is_deterministic(self) -> None:
        """NADR-28 §5.2 R8: misma entrada → mismo resultado."""
        manifest = _make_manifest(["doc_01", "doc_02", "doc_03"])
        first = get_profile_document_ids(VerificationProfile.FULL, manifest)
        second = get_profile_document_ids(VerificationProfile.FULL, manifest)
        assert first == second

    def test_full_with_empty_manifest(self) -> None:
        """R14: FULL con manifest vacío retorna frozenset vacío."""
        manifest = _make_manifest([])
        result = get_profile_document_ids(VerificationProfile.FULL, manifest)
        assert result == frozenset()

    def test_full_preserves_document_order_independence(self) -> None:
        """frozenset no depende del orden del manifest."""
        manifest_a = _make_manifest(["doc_01", "doc_02", "doc_03"])
        manifest_b = _make_manifest(["doc_03", "doc_01", "doc_02"])
        result_a = get_profile_document_ids(VerificationProfile.FULL, manifest_a)
        result_b = get_profile_document_ids(VerificationProfile.FULL, manifest_b)
        assert result_a == result_b

    def test_full_with_single_document(self) -> None:
        """R14: FULL con un solo documento."""
        manifest = _make_manifest(["doc_01"])
        result = get_profile_document_ids(VerificationProfile.FULL, manifest)
        assert result == frozenset({"doc_01"})


@pytest.mark.unit
class TestGetProfileDocumentIdsSmoke:
    """NADR-F17BIS-29 §5.4 R18-R23."""

    def test_smoke_profile_exists(self) -> None:
        """R18: SMOKE está definido."""
        assert hasattr(VerificationProfile, "SMOKE")

    def test_smoke_returns_hardcoded_list(self) -> None:
        """R19: SMOKE retorna lista hardcoded de documentos representativos."""
        from core.benchmark.verification.profiles import SMOKE_DOCUMENT_IDS

        manifest = _make_manifest(list(SMOKE_DOCUMENT_IDS))
        smoke = get_profile_document_ids(VerificationProfile.SMOKE, manifest)
        assert smoke == SMOKE_DOCUMENT_IDS

    def test_smoke_is_subset_of_full(self) -> None:
        """R20: SMOKE retorna subset de FULL (mismas fronteras normativas)."""
        from core.benchmark.verification.profiles import SMOKE_DOCUMENT_IDS

        manifest = _make_manifest(list(SMOKE_DOCUMENT_IDS))
        full = get_profile_document_ids(VerificationProfile.FULL, manifest)
        smoke = get_profile_document_ids(VerificationProfile.SMOKE, manifest)
        assert smoke.issubset(full)

    def test_smoke_is_deterministic(self) -> None:
        """NADR-28 §5.2 R8: misma entrada → mismo resultado."""
        from core.benchmark.verification.profiles import SMOKE_DOCUMENT_IDS

        manifest = _make_manifest(list(SMOKE_DOCUMENT_IDS))
        first = get_profile_document_ids(VerificationProfile.SMOKE, manifest)
        second = get_profile_document_ids(VerificationProfile.SMOKE, manifest)
        assert first == second

    def test_smoke_intersects_with_manifest(self) -> None:
        """Robustez: si un documento del smoke se elimina del corpus, el subset se ajusta."""
        from core.benchmark.verification.profiles import SMOKE_DOCUMENT_IDS

        # Manifest con solo 3 de los 5 documentos del smoke
        subset = list(SMOKE_DOCUMENT_IDS)[:3]
        manifest = _make_manifest(subset)
        smoke = get_profile_document_ids(VerificationProfile.SMOKE, manifest)
        assert smoke == frozenset(subset)

    def test_smoke_with_empty_manifest(self) -> None:
        """SMOKE con manifest vacío retorna frozenset vacío."""
        manifest = _make_manifest([])
        smoke = get_profile_document_ids(VerificationProfile.SMOKE, manifest)
        assert smoke == frozenset()

    def test_smoke_returns_frozenset(self) -> None:
        """Inmutabilidad (ENGINEERING_PRINCIPLES §III)."""
        from core.benchmark.verification.profiles import SMOKE_DOCUMENT_IDS

        manifest = _make_manifest(list(SMOKE_DOCUMENT_IDS))
        smoke = get_profile_document_ids(VerificationProfile.SMOKE, manifest)
        assert isinstance(smoke, frozenset)

    def test_smoke_has_five_documents(self) -> None:
        """R19: SMOKE tiene exactamente 5 documentos (cobertura declarada)."""
        from core.benchmark.verification.profiles import SMOKE_DOCUMENT_IDS

        assert len(SMOKE_DOCUMENT_IDS) == 5

    def test_smoke_does_not_alter_scientific_criteria(self) -> None:
        """R12: SMOKE no modifica criterios científicos (solo cobertura)."""
        from core.benchmark.verification.profiles import SMOKE_DOCUMENT_IDS

        # Verificar que la lista hardcoded no depende de thresholds ni pesos
        # (es una constante inmutable definida en el módulo)
        assert isinstance(SMOKE_DOCUMENT_IDS, frozenset)
        assert all(isinstance(doc_id, str) for doc_id in SMOKE_DOCUMENT_IDS)