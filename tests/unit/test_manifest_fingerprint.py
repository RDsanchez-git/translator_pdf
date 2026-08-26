"""Tests de regresión y propiedades del hash del manifiesto (Wave 4.2).

Verifica:
- DF-19: el formato del hash cambió (oracle_hash + ground_truth_state incluidos)
- Determinismo: mismo input → mismo hash
- Sensibilidad a oracle_hash: cambio de identidad semántica → hash diferente
- Sensibilidad a ground_truth_state: cambio de estado → hash diferente (DF-17)
- Preservación de valores anteriores (Matiz 1)
"""

from __future__ import annotations

from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusVersion,
    DocumentFingerprint,
)
from core.benchmark.corpus.services import (
    ManifestFingerprintCalculator,
    ManifestLineageSealer,
)


_VALID_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _make_metadata(
    doc_id: str = "doc-1",
    oracle_hash: str | None = None,
    gt_state: str | None = None,
) -> CorpusDocumentMetadata:
    return CorpusDocumentMetadata(
        document_id=doc_id,
        fingerprint=DocumentFingerprint(sha256=_VALID_SHA256),
        traits=frozenset({ExtractionChallengeTrait.NATIVE_PDF}),
        page_count=1,
        oracle_hash=oracle_hash,
        ground_truth_state=gt_state,
    )


def _make_entry(
    doc_id: str = "doc-1",
    oracle_hash: str | None = None,
    gt_state: str | None = None,
) -> RawDocumentEntryDTO:
    return RawDocumentEntryDTO(
        document_id=doc_id,
        sha256=_VALID_SHA256,
        traits=["native_pdf"],
        page_count=1,
        oracle_hash=oracle_hash,
        ground_truth_state=gt_state,
    )


class TestManifestFingerprintDeterminism:
    def test_identical_manifests_produce_identical_hash(self) -> None:
        """Determinismo: mismo input → mismo hash."""
        docs = [_make_metadata("doc-1", oracle_hash="abc123", gt_state="sealed")]
        v = CorpusVersion(value="v1.0")

        hash_a = ManifestFingerprintCalculator.compute_hash(v, docs)
        hash_b = ManifestFingerprintCalculator.compute_hash(v, docs)

        assert hash_a == hash_b

    def test_hash_is_valid_sha256(self) -> None:
        """El hash resultante es un SHA-256 válido."""
        docs = [_make_metadata()]
        h = ManifestFingerprintCalculator.compute_hash(CorpusVersion(value="v1.0"), docs)

        assert isinstance(h, str)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestManifestFingerprintSensitivity:
    def test_oracle_hash_change_produces_different_hash(self) -> None:
        """DF-17/DF-19: cambio de oracle_hash → hash diferente."""
        v = CorpusVersion(value="v1.0")
        docs_a = [_make_metadata("doc-1", oracle_hash="hash_v1", gt_state="sealed")]
        docs_b = [_make_metadata("doc-1", oracle_hash="hash_v2", gt_state="sealed")]

        hash_a = ManifestFingerprintCalculator.compute_hash(v, docs_a)
        hash_b = ManifestFingerprintCalculator.compute_hash(v, docs_b)

        assert hash_a != hash_b

    def test_ground_truth_state_change_produces_different_hash(self) -> None:
        """DF-17: cambio de ground_truth_state → hash diferente.

        Esto cierra la ventana de vulnerabilidad de DF-17: el estado
        sellado ahora está protegido por el hash del manifiesto.
        """
        v = CorpusVersion(value="v1.0")
        docs_a = [_make_metadata("doc-1", oracle_hash="h1", gt_state="draft")]
        docs_b = [_make_metadata("doc-1", oracle_hash="h1", gt_state="sealed")]

        hash_a = ManifestFingerprintCalculator.compute_hash(v, docs_a)
        hash_b = ManifestFingerprintCalculator.compute_hash(v, docs_b)

        assert hash_a != hash_b

    def test_oracle_hash_none_vs_value_produces_different_hash(self) -> None:
        """oracle_hash=None vs oracle_hash=valor → hash diferente."""
        v = CorpusVersion(value="v1.0")
        docs_a = [_make_metadata("doc-1", oracle_hash=None, gt_state="sealed")]
        docs_b = [_make_metadata("doc-1", oracle_hash="abc", gt_state="sealed")]

        hash_a = ManifestFingerprintCalculator.compute_hash(v, docs_a)
        hash_b = ManifestFingerprintCalculator.compute_hash(v, docs_b)

        assert hash_a != hash_b


class TestManifestLineageSealer:
    def test_sealer_propagates_oracle_hash_and_state(self) -> None:
        """ManifestLineageSealer propaga oracle_hash y ground_truth_state."""
        manifest = RawCorpusManifestDTO(
            corpus_version="v1.0",
            manifest_hash="",
            documents=[_make_entry("doc-1")],
        )

        sealed = ManifestLineageSealer.seal_manifest_with_ground_truth(
            current_manifest=manifest,
            detected_hashes={"doc-1": "new_hash"},
            target_version="v1.0",
            oracle_hashes={"doc-1": "semantic_hash_abc"},
            ground_truth_states={"doc-1": "sealed"},
        )

        doc = sealed.documents[0]
        assert doc.oracle_hash == "semantic_hash_abc"
        assert doc.ground_truth_state == "sealed"
        assert doc.ground_truth_sha256 == "new_hash"
        assert doc.ground_truth_version == "v1.0"

    def test_sealer_preserves_previous_oracle_hash(self) -> None:
        """Matiz 1: documentos sin oráculo en este ciclo preservan oracle_hash anterior."""
        manifest = RawCorpusManifestDTO(
            corpus_version="v1.0",
            manifest_hash="",
            documents=[
                _make_entry("doc-1", oracle_hash="old_semantic_hash", gt_state="sealed"),
                _make_entry("doc-2", oracle_hash="doc2_hash", gt_state="sealed"),
            ],
        )

        # Solo doc-1 se sella en este ciclo; doc-2 no está en detected_hashes
        sealed = ManifestLineageSealer.seal_manifest_with_ground_truth(
            current_manifest=manifest,
            detected_hashes={"doc-1": "new_physical_hash"},
            target_version="v2.0",
            oracle_hashes={"doc-1": "new_semantic_hash"},
            ground_truth_states={"doc-1": "sealed"},
        )

        doc1 = next(d for d in sealed.documents if d.document_id == "doc-1")
        doc2 = next(d for d in sealed.documents if d.document_id == "doc-2")

        # doc-1: valores actualizados
        assert doc1.oracle_hash == "new_semantic_hash"
        assert doc1.ground_truth_state == "sealed"

        # doc-2: valores preservados (Matiz 1)
        assert doc2.oracle_hash == "doc2_hash"
        assert doc2.ground_truth_state == "sealed"

    def test_sealer_uses_none_as_default_for_new_documents(self) -> None:
        """Documentos nuevos (sin valores previos) quedan con None."""
        manifest = RawCorpusManifestDTO(
            corpus_version="v1.0",
            manifest_hash="",
            documents=[_make_entry("doc-new")],
        )

        sealed = ManifestLineageSealer.seal_manifest_with_ground_truth(
            current_manifest=manifest,
            detected_hashes={},
            target_version="v1.0",
        )

        doc = sealed.documents[0]
        assert doc.oracle_hash is None
        assert doc.ground_truth_state is None


class TestDF19FormatChange:
    """Verifica DF-19: el formato del hash cambió en Wave 4.2."""

    def test_format_includes_oracle_hash_and_state(self) -> None:
        """El hash es sensible a oracle_hash y ground_truth_state (formato nuevo)."""
        v = CorpusVersion(value="v1.0")

        # Mismos campos físicos, diferentes oracle_hash
        docs_a = [_make_metadata("doc-1", oracle_hash=None, gt_state=None)]
        docs_b = [_make_metadata("doc-1", oracle_hash="h", gt_state="sealed")]

        hash_a = ManifestFingerprintCalculator.compute_hash(v, docs_a)
        hash_b = ManifestFingerprintCalculator.compute_hash(v, docs_b)

        # Si el formato antiguo no incluyera estos campos, los hashes serían iguales.
        # El formato nuevo garantiza que sean diferentes.
        assert hash_a != hash_b, (
            "DF-19: el formato del hash debe incluir oracle_hash y ground_truth_state"
        )

    def test_df19_regression_old_format_differs_from_new_format(self) -> None:
        """DF-19: El formato nuevo produce hash diferente al antiguo (mismo input base).

        Este test documenta la ruptura de formato con evidencia empírica.
        Un manifiesto sellado con el formato antiguo (4 dimensiones) debe
        re-sellarse con el nuevo formato (6 dimensiones) para mantener la
        protección criptográfica completa.
        """
        from core.shared.crypto import compute_sha256

        v = CorpusVersion(value="v1.0")
        doc = _make_metadata("doc-1", oracle_hash=None, gt_state=None)

        # Formato nuevo (Wave 4.2): incluye oracle_hash y ground_truth_state
        new_hash = ManifestFingerprintCalculator.compute_hash(v, [doc])

        # Formato antiguo (pre-Wave 4.2): solo 4 campos
        old_format_parts = [v.value.encode("utf-8")]
        traits_str = ",".join(sorted(t.value for t in doc.traits))
        old_payload = (
            f"{doc.document_id}:{doc.fingerprint.sha256}:"
            f"{traits_str}:{doc.page_count}"
        )
        old_format_parts.append(old_payload.encode("utf-8"))
        old_hash = compute_sha256(b"".join(old_format_parts))

        # El cambio de formato garantiza hashes diferentes
        assert new_hash != old_hash, (
            "DF-19: el formato nuevo debe producir hash diferente al antiguo. "
            "Manifiestos con formato antiguo deben re-sellarse."
        )