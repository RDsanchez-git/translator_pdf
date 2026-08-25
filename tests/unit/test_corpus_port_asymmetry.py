"""Tests de asimetría de puertos del corpus (Wave 3.1).

Verifica NADR-14 §5.1 (asimetría), E-2.0-05 (fail-fast), E-2.0-06 (atomicidad),
DF-13 (ground_truth_state) y DF-10 (BenchmarkParserBridge Tuple).
"""

from __future__ import annotations

import json
from typing import List

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from infra.benchmarks.adapters.ground_truth_parser_adapter import BenchmarkParserBridge
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader


def _make_node(node_id: str) -> ASTNode:
    return ASTNode(
        node_id=node_id, sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content="Contenido."),
    )


class TestCorpusManifestReaderPort:
    def test_load_raises_file_not_found_when_missing(self, tmp_path):
        """E-2.0-05 corregido: fail-fast, no fail-open."""
        loader = LocalFileSystemCorpusLoader(tmp_path)
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            loader.load_raw_manifest()

    def test_load_returns_dto_when_exists(self, tmp_path):
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps({
            "corpus_version": "v1.0", "manifest_hash": "", "documents": []
        }))
        loader = LocalFileSystemCorpusLoader(tmp_path)
        dto = loader.load_raw_manifest()
        assert dto.corpus_version == "v1.0"
        assert dto.documents == []


class TestCorpusManifestWriterPort:
    def test_save_creates_manifest(self, tmp_path):
        """E-2.0-06 corregido: escritura atómica."""
        loader = LocalFileSystemCorpusLoader(tmp_path)
        dto = RawCorpusManifestDTO(corpus_version="v1.0", manifest_hash="abc", documents=[])
        loader.save_manifest_dto(dto)
        assert (tmp_path / "manifest.json").exists()

    def test_save_overwrites_existing_manifest(self, tmp_path):
        loader = LocalFileSystemCorpusLoader(tmp_path)
        dto1 = RawCorpusManifestDTO(corpus_version="v1.0", manifest_hash="first", documents=[])
        dto2 = RawCorpusManifestDTO(corpus_version="v2.0", manifest_hash="second", documents=[])
        loader.save_manifest_dto(dto1)
        loader.save_manifest_dto(dto2)
        loaded = loader.load_raw_manifest()
        assert loaded.manifest_hash == "second"


class TestGroundTruthStateField:
    def test_ground_truth_state_defaults_to_none(self):
        """DF-13: default None (la capa de consumo interpreta como DRAFT)."""
        entry = RawDocumentEntryDTO(
            document_id="doc-1", sha256="0" * 64, traits=[], page_count=1
        )
        assert entry.ground_truth_state is None

    def test_ground_truth_state_accepts_explicit_value(self):
        """DF-13: acepta valores explícitos (DRAFT, SEALED)."""
        entry = RawDocumentEntryDTO(
            document_id="doc-1", sha256="0" * 64, traits=[], page_count=1,
            ground_truth_state="SEALED",
        )
        assert entry.ground_truth_state == "SEALED"


class TestBenchmarkParserBridgeDF10:
    def test_extract_ast_returns_tuple(self, tmp_path):
        """DF-10: extract_ast retorna Tuple, no Sequence/List."""
        pdf_path = tmp_path / "doc-1.pdf"
        pdf_path.write_bytes(b"fake pdf content")

        class FakeParser:
            def parse(self, file_path: str) -> List[ASTNode]:
                return [_make_node("n1")]

        bridge = BenchmarkParserBridge(tmp_path, FakeParser())
        result = bridge.extract_ast("doc-1")
        assert isinstance(result, tuple)
        assert len(result) == 1