"""Tests de contrato de puertos del Ground Truth (Task 1.1.3).

Verifica NADR-F17BIS-12 §5.1 R3: hidratación vía contrato canónico y
retorno inmutable (Tuple) en la frontera de lectura.
"""

from __future__ import annotations

import pathlib

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from infra.fs.ground_truth_store import (
    LocalFileSystemGroundTruthDraftWriter,
    LocalFileSystemGroundTruthReader,
)


def _make_node(node_id: str) -> ASTNode:
    return ASTNode(
        node_id=node_id,
        sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content="Contenido de prueba."),
    )


class TestLocalFileSystemGroundTruthReader:
    def test_load_returns_tuple_not_list(self, tmp_path: pathlib.Path) -> None:
        """Verifica que el adaptador retorna Tuple (inmutable), no List."""
        writer = LocalFileSystemGroundTruthDraftWriter(tmp_path)
        reader = LocalFileSystemGroundTruthReader(tmp_path)
        nodes = (_make_node("n1"), _make_node("n2"))
        writer.save_draft_ast("doc-123", nodes)

        loaded = reader.load_ground_truth("doc-123")
        assert isinstance(loaded, tuple)
        assert loaded == nodes

    def test_load_missing_artifact_raises_file_not_found(self, tmp_path: pathlib.Path) -> None:
        reader = LocalFileSystemGroundTruthReader(tmp_path)
        with pytest.raises(FileNotFoundError, match="Oracle consistency error"):
            reader.load_ground_truth("nonexistent")


class TestLocalFileSystemGroundTruthDraftWriter:
    def test_save_accepts_tuple(self, tmp_path: pathlib.Path) -> None:
        writer = LocalFileSystemGroundTruthDraftWriter(tmp_path)
        nodes = (_make_node("n1"),)
        writer.save_draft_ast("doc-123", nodes)
        assert (tmp_path / "ground_truth" / "doc-123.json").exists()


    def test_draft_writer_overwrites_existing_file(self, tmp_path: pathlib.Path) -> None:
        """R8: El escritor sobrescribe el archivo del mismo document_id.

        Esto materializa el reemplazo permitido durante la curaduría.
        El mecanismo de sobrescritura es el rename atómico de write_ast_json_atomic.
        """
        writer = LocalFileSystemGroundTruthDraftWriter(tmp_path)
        reader = LocalFileSystemGroundTruthReader(tmp_path)

        # Escribir draft inicial con contenido A
        nodes_a = (_make_node("n1"),)
        writer.save_draft_ast("doc-123", nodes_a)
        loaded_a = reader.load_ground_truth("doc-123")
        assert loaded_a == nodes_a

        # Escribir segundo draft con contenido B (mismo document_id)
        nodes_b = (_make_node("n2"),)
        writer.save_draft_ast("doc-123", nodes_b)
        loaded_b = reader.load_ground_truth("doc-123")

        # El archivo fue sobrescrito: el contenido es B, no A
        assert loaded_b == nodes_b
        assert loaded_b != nodes_a