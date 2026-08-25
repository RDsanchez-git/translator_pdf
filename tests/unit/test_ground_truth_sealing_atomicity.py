"""Tests de atomicidad del sellado (Wave 2.3).

Verifica NADR-F17BIS-13 §5.3 R9-R10: el sellado es atómico y un aborto
no deja una baseline parcialmente certificada ni manifiesto inconsistente.
Usa fakes de puertos (Functional Core: el caso de uso recibe dependencias).
"""

from __future__ import annotations

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from core.benchmark.ground_truth.errors import BaselineContractError
from core.benchmark.ground_truth.use_cases import SealGroundTruthUseCase


def _make_node(node_id: str, content: str) -> ASTNode:
    return ASTNode(
        node_id=node_id,
        sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content=content),
    )


# Hash SHA-256 real de la cadena vacía, usado como valor por defecto válido
# en los fakes. Evita problemas de validación de Pydantic con dataclasses
# anidados (DocumentFingerprint).
_VALID_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class FakeCorpusLoader:
    def __init__(self, doc_ids):
        self._doc_ids = doc_ids
        self.saved_manifests = []

    def load_raw_manifest(self):
        documents = [
            RawDocumentEntryDTO(
                document_id=d,
                sha256=_VALID_SHA256,
                traits=["native_pdf"],  # Al menos un trait (CorpusDocumentMetadata requiere min_length=1)
                page_count=1
            )
            for d in self._doc_ids
        ]
        return RawCorpusManifestDTO(
            corpus_version="v1.0", manifest_hash="", documents=documents
        )

    def save_manifest_dto(self, dto):
        self.saved_manifests.append(dto)


class FakeArtifactPort:
    def __init__(self, artifact_ids):
        self._artifact_ids = set(artifact_ids)

    def artifact_exists(self, document_id):
        return document_id in self._artifact_ids

    def read_artifact_bytes(self, document_id):
        return b"{}"

    def list_artifact_ids(self):
        return tuple(sorted(self._artifact_ids))


class FakeReader:
    def __init__(self, oracle_nodes_by_doc):
        self._oracles = oracle_nodes_by_doc

    def load_ground_truth(self, document_id):
        return self._oracles[document_id]


class TestSealAtomicity:
    def _make_use_case(self, doc_ids, artifact_ids, oracles):
        loader = FakeCorpusLoader(doc_ids)
        artifact_port = FakeArtifactPort(artifact_ids)
        reader = FakeReader(oracles)
        return SealGroundTruthUseCase(
            corpus_loader=loader,
            artifact_port=artifact_port,
            reader=reader,
        ), loader

    def test_successful_seal_saves_manifest(self) -> None:
        nodes = (_make_node("n1", "Contenido válido."),)
        use_case, loader = self._make_use_case(
            doc_ids=["doc-1"],
            artifact_ids=["doc-1"],
            oracles={"doc-1": nodes},
        )
        result_hash = use_case.execute(target_version="v1.0")
        assert isinstance(result_hash, str)
        assert len(loader.saved_manifests) == 1

    def test_missing_oracle_aborts_without_saving_manifest(self) -> None:
        """R9/R10: aborto por completitud no deja manifiesto guardado."""
        use_case, loader = self._make_use_case(
            doc_ids=["doc-1", "doc-2"],
            artifact_ids=["doc-1"],
            oracles={"doc-1": (_make_node("n1", "Ok."),)},
        )
        with pytest.raises(BaselineContractError):
            use_case.execute(target_version="v1.0")
        assert loader.saved_manifests == []

    def test_invalid_oracle_aborts_without_saving_manifest(self) -> None:
        """R9/R10: aborto por validez no deja manifiesto guardado."""
        use_case, loader = self._make_use_case(
            doc_ids=["doc-1"],
            artifact_ids=["doc-1"],
            oracles={"doc-1": (_make_node("n1", ""),)},  # contenido vacío
        )
        with pytest.raises(BaselineContractError):
            use_case.execute(target_version="v1.0")
        assert loader.saved_manifests == []

    def test_aggregate_error_contains_completeness_and_validity(self) -> None:
        """Reporte agregado: ambos tipos de error se recolectan juntos."""
        use_case, _ = self._make_use_case(
            doc_ids=["doc-missing", "doc-invalid"],
            artifact_ids=["doc-invalid"],
            oracles={"doc-invalid": (_make_node("n1", ""),)},
        )
        with pytest.raises(BaselineContractError) as exc_info:
            use_case.execute(target_version="v1.0")
        err = exc_info.value
        assert len(err.completeness_errors) == 1  # doc-missing
        assert len(err.validity_errors) == 1  # doc-invalid