"""Tests de protección contra sobrescritura de oráculos sellados (Wave 3.3).

Verifica:
- DF-14: GenerateGoldenDraftUseCase verifica estado sellado antes de escribir
- NADR-14 §5.3 R7: oráculo sellado no puede ser alterado por curaduría
- NADR-14 §5.3 R8: fallos de integridad como errores explícitos
"""

from __future__ import annotations

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from core.benchmark.ground_truth.errors import (
    EmptyGroundTruthDraftError,
    SealedOracleOverwriteError,
)
from core.benchmark.ground_truth.models import GroundTruthLifecycleState
from core.benchmark.ground_truth.use_cases import GenerateGoldenDraftUseCase


_VALID_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _make_node(node_id: str) -> ASTNode:
    return ASTNode(
        node_id=node_id,
        sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content="Contenido."),
    )


class FakeCorpusReader:
    def __init__(self, entries: list[RawDocumentEntryDTO]):
        self._entries = entries

    def load_raw_manifest(self) -> RawCorpusManifestDTO:
        return RawCorpusManifestDTO(
            corpus_version="v1.0",
            manifest_hash="abc",
            documents=self._entries,
        )


class FakeExtractor:
    def __init__(self, nodes):
        self._nodes = nodes

    def extract_ast(self, document_id: str):
        return self._nodes


class FakeWriter:
    def __init__(self):
        self.saved: list[tuple[str, tuple]] = []

    def save_draft_ast(self, document_id: str, nodes: tuple) -> None:
        self.saved.append((document_id, nodes))


class TestSealedOracleProtection:
    def _make_entry(self, doc_id: str, state: str | None = None) -> RawDocumentEntryDTO:
        return RawDocumentEntryDTO(
            document_id=doc_id,
            sha256=_VALID_SHA256,
            traits=["native_pdf"],
            page_count=1,
            ground_truth_state=state,
        )

    def test_sealed_oracle_raises_overwrite_error(self) -> None:
        """DF-14: oráculo sellado lanza SealedOracleOverwriteError."""
        reader = FakeCorpusReader([
            self._make_entry("doc-1", state=GroundTruthLifecycleState.SEALED.value)
        ])
        extractor = FakeExtractor((_make_node("n1"),))
        writer = FakeWriter()

        use_case = GenerateGoldenDraftUseCase(
            extractor=extractor, writer=writer, corpus_reader=reader,
        )

        with pytest.raises(SealedOracleOverwriteError, match="sealed oracle"):
            use_case.execute("doc-1")

        # El writer NO debe haber sido llamado
        assert len(writer.saved) == 0

    def test_draft_state_allows_regeneration(self) -> None:
        """Documento en estado DRAFT permite regeneración del draft."""
        reader = FakeCorpusReader([
            self._make_entry("doc-1", state=GroundTruthLifecycleState.DRAFT.value)
        ])
        extractor = FakeExtractor((_make_node("n1"),))
        writer = FakeWriter()

        use_case = GenerateGoldenDraftUseCase(
            extractor=extractor, writer=writer, corpus_reader=reader,
        )
        use_case.execute("doc-1")

        assert len(writer.saved) == 1
        assert writer.saved[0][0] == "doc-1"

    def test_document_not_in_manifest_allows_draft(self) -> None:
        """Documento no encontrado en manifiesto permite draft (documento nuevo)."""
        reader = FakeCorpusReader([self._make_entry("doc-other", state=None)])
        extractor = FakeExtractor((_make_node("n1"),))
        writer = FakeWriter()

        use_case = GenerateGoldenDraftUseCase(
            extractor=extractor, writer=writer, corpus_reader=reader,
        )
        # doc-new no está en el manifiesto (solo doc-other está)
        use_case.execute("doc-new")

        assert len(writer.saved) == 1

    def test_no_ground_truth_state_field_allows_draft(self) -> None:
        """Documento sin campo ground_truth_state (legacy) permite draft."""
        reader = FakeCorpusReader([self._make_entry("doc-1", state=None)])
        extractor = FakeExtractor((_make_node("n1"),))
        writer = FakeWriter()

        use_case = GenerateGoldenDraftUseCase(
            extractor=extractor, writer=writer, corpus_reader=reader,
        )
        use_case.execute("doc-1")

        assert len(writer.saved) == 1

    def test_empty_extraction_raises_empty_draft_error(self) -> None:
        """Extracción vacía lanza EmptyGroundTruthDraftError (no SealedOracleOverwriteError)."""
        reader = FakeCorpusReader([self._make_entry("doc-1", state=None)])
        extractor = FakeExtractor(())  # nodos vacíos
        writer = FakeWriter()

        use_case = GenerateGoldenDraftUseCase(
            extractor=extractor, writer=writer, corpus_reader=reader,
        )

        with pytest.raises(EmptyGroundTruthDraftError):
            use_case.execute("doc-1")

        assert len(writer.saved) == 0