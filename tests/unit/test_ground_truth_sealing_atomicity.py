"""Tests de atomicidad y autoridad única de sellado (Wave 3.2).

Verifica:
- NADR-14 §5.2 R4-R6: autoridad única de sellado
- NADR-13 §5.3 R9-R10: atomicidad del sellado
- Integración con LifecycleTransitionAuthority (Gate 1)
- Persistencia del estado SEALED (DF-13)
- Completitud bidireccional defensiva

DC-08 (resuelto): Se eliminó el parámetro `target_version` de las llamadas
a `execute()` y las aserciones sobre `ground_truth_version` /
`ground_truth_sha256`, ya que estos campos fueron eliminados del DTO
como parte de la limpieza radical de campos huérfanos.
"""

from __future__ import annotations

from typing import List

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from core.benchmark.ground_truth.errors import BaselineContractError
from core.benchmark.ground_truth.lifecycle import LifecycleTransitionAuthority
from core.benchmark.ground_truth.models import (
    DraftSubState,
    GroundTruthDraft,
    GroundTruthLifecycleState,
)
from core.benchmark.ground_truth.use_cases import SealGroundTruthUseCase


# Hash SHA-256 real de la cadena vacía (hex válido, minúsculas)
_VALID_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _make_node(node_id: str, content: str) -> ASTNode:
    return ASTNode(
        node_id=node_id,
        sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content=content),
    )


def _make_validated_draft(doc_id: str) -> GroundTruthDraft:
    """Construye un draft en estado VALIDATED."""
    draft = GroundTruthDraft(
        document_id=doc_id,
        nodes=(_make_node("n1", "Contenido válido."),),
        sub_state=DraftSubState.DRAFT,
    )
    audited = LifecycleTransitionAuthority.audit(draft)
    return LifecycleTransitionAuthority.validate(audited)


class FakeCorpusLoader:
    def __init__(self, doc_ids):
        self._doc_ids = doc_ids
        self.saved_manifests: List[RawCorpusManifestDTO] = []

    def load_raw_manifest(self) -> RawCorpusManifestDTO:
        # DC-08: RawDocumentEntryDTO ya no lleva ground_truth_version
        # ni ground_truth_sha256.
        documents = [
            RawDocumentEntryDTO(
                document_id=d,
                sha256=_VALID_SHA256,
                traits=["native_pdf"],
                page_count=1,
            )
            for d in self._doc_ids
        ]
        return RawCorpusManifestDTO(
            corpus_version="v1.0", manifest_hash="", documents=documents
        )

    def save_manifest_dto(self, dto: RawCorpusManifestDTO) -> None:
        self.saved_manifests.append(dto)


class FakeArtifactPort:
    """Fake del puerto de artefactos de Ground Truth.

    DC-08: `read_artifact_bytes` ya no es invocado por
    SealGroundTruthUseCase.execute() tras la eliminación del cálculo
    de `detected_hashes`. Se mantiene la implementación para cumplir
    el protocolo GroundTruthArtifactPort.
    """

    def __init__(self, artifact_ids):
        self._artifact_ids = set(artifact_ids)

    def artifact_exists(self, document_id: str) -> bool:
        return document_id in self._artifact_ids

    def read_artifact_bytes(self, document_id: str) -> bytes:
        return b"{}"

    def list_artifact_ids(self):
        return tuple(sorted(self._artifact_ids))


class TestSealAuthorityAndAtomicity:
    def _make_use_case(self, doc_ids, artifact_ids):
        loader = FakeCorpusLoader(doc_ids)
        artifact_port = FakeArtifactPort(artifact_ids)
        return (
            SealGroundTruthUseCase(
                corpus_reader=loader,
                corpus_writer=loader,
                artifact_port=artifact_port,
            ),
            loader,
        )

    def test_successful_seal_saves_manifest_with_sealed_state_and_oracle_hash(self) -> None:
        """Sellado exitoso: persiste manifiesto con ground_truth_state=sealed y oracle_hash válido."""
        use_case, loader = self._make_use_case(
            doc_ids=["doc-1"],
            artifact_ids=["doc-1"],
        )
        validated = _make_validated_draft("doc-1")

        # DC-08: llamada simplificada sin target_version (parámetro eliminado)
        result_hash = use_case.execute(
            validated_drafts=(validated,),
        )

        # Verificación del contrato de execute(): retorna un SHA-256 válido
        assert isinstance(result_hash, str)
        assert len(result_hash) == 64
        assert all(c in "0123456789abcdef" for c in result_hash)

        # DC-08: se eliminó la aserción sobre ground_truth_version
        saved = loader.saved_manifests[0]
        assert saved.corpus_version == "v1.0"
        assert saved.manifest_hash != ""
        assert len(saved.documents) == 1
        assert saved.documents[0].document_id == "doc-1"
        assert saved.documents[0].ground_truth_state == "sealed"
        assert saved.documents[0].oracle_hash is not None

        # Verificación de consistencia: el hash retornado coincide con el persistido
        assert result_hash == saved.manifest_hash

    def test_draft_not_in_validated_state_aborts(self) -> None:
        """El caso de uso rechaza drafts no-VALIDATED."""
        use_case, loader = self._make_use_case(
            doc_ids=["doc-1"],
            artifact_ids=["doc-1"],
        )
        draft_in_draft_state = GroundTruthDraft(
            document_id="doc-1",
            nodes=(_make_node("n1", "Ok"),),
            sub_state=DraftSubState.DRAFT,
        )

        with pytest.raises(BaselineContractError) as exc_info:
            use_case.execute(validated_drafts=(draft_in_draft_state,))

        err = exc_info.value
        assert len(err.validity_errors) == 1
        assert "VALIDATED state" in err.validity_errors[0]
        assert loader.saved_manifests == []

    def test_validated_draft_not_in_manifest_aborts(self) -> None:
        """Draft validado con doc_id que no está en manifiesto aborta."""
        use_case, loader = self._make_use_case(
            doc_ids=["doc-1"],
            artifact_ids=["doc-1", "doc-orphan"],
        )
        # doc-1 cubre el manifiesto; doc-orphan es huérfano
        validated = (
            _make_validated_draft("doc-1"),
            _make_validated_draft("doc-orphan"),
        )

        with pytest.raises(BaselineContractError) as exc_info:
            use_case.execute(validated_drafts=validated)

        err = exc_info.value
        assert len(err.completeness_errors) == 1
        assert "doc-orphan" in err.completeness_errors[0]
        assert loader.saved_manifests == []

    def test_manifest_document_without_validated_draft_aborts(self) -> None:
        """Caso de uso aborta si hay documentos del manifiesto sin draft validado."""
        use_case, loader = self._make_use_case(
            doc_ids=["doc-1", "doc-2"],
            artifact_ids=["doc-1", "doc-2"],
        )
        # Solo validamos doc-1; doc-2 queda sin draft validado
        validated = _make_validated_draft("doc-1")

        with pytest.raises(BaselineContractError) as exc_info:
            use_case.execute(validated_drafts=(validated,))

        err = exc_info.value
        assert len(err.completeness_errors) == 1
        assert "doc-2" in err.completeness_errors[0]
        assert loader.saved_manifests == []

    def test_multiple_documents_seal_atomically(self) -> None:
        """Atomicidad: todos los documentos se sellan juntos."""
        use_case, loader = self._make_use_case(
            doc_ids=["doc-a", "doc-b", "doc-c"],
            artifact_ids=["doc-a", "doc-b", "doc-c"],
        )
        validated = (
            _make_validated_draft("doc-a"),
            _make_validated_draft("doc-b"),
            _make_validated_draft("doc-c"),
        )

        # DC-08: llamada simplificada sin target_version (parámetro eliminado)
        use_case.execute(validated_drafts=validated)

        assert len(loader.saved_manifests) == 1
        saved = loader.saved_manifests[0]
        assert len(saved.documents) == 3
        for doc in saved.documents:
            assert doc.ground_truth_state == GroundTruthLifecycleState.SEALED.value

    def test_oracle_hash_is_deterministic_across_seals(self) -> None:
        """Gate 4 (Wave 4.3): el oracle_hash es determinista (mismo contenido → mismo hash)."""
        use_case, loader = self._make_use_case(
            doc_ids=["doc-1"],
            artifact_ids=["doc-1"],
        )
        validated = _make_validated_draft("doc-1")

        # DC-08: Primer sellado sin target_version
        use_case.execute(validated_drafts=(validated,))
        first_oracle_hash = loader.saved_manifests[0].documents[0].oracle_hash

        # Resetear el loader para un segundo sellado
        loader.saved_manifests = []

        # DC-08: Segundo sellado (mismo contenido) sin target_version
        use_case.execute(validated_drafts=(validated,))
        second_oracle_hash = loader.saved_manifests[0].documents[0].oracle_hash

        # El oracle_hash debe ser idéntico (determinismo, NADR-15 §5.1)
        assert first_oracle_hash == second_oracle_hash


class TestSingleAuthorityOfSealing:
    def test_manifest_ground_truth_updater_removed(self) -> None:
        """ManifestGroundTruthUpdater fue eliminado (Zero Debt, E-2.0-03)."""
        from core.benchmark.ground_truth import services
        assert not hasattr(
            services, "ManifestGroundTruthUpdater"
        ), "ManifestGroundTruthUpdater was removed (E-2.0-03, Zero Debt)"