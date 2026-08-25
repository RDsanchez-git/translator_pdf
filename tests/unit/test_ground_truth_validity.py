from __future__ import annotations
import pytest
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload, ImagePayload
from core.benchmark.ground_truth.errors import OracleValidityError
from core.benchmark.ground_truth.validity import OracleValidityContract


def _make_node(node_id: str, content: str) -> ASTNode:
    return ASTNode(
        node_id=node_id, sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content=content),
    )


def _make_image_node(node_id: str) -> ASTNode:
    return ASTNode(
        node_id=node_id, sequence_id=1,
        node_type=ContentNodeType.IMAGE,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ImagePayload(asset_path=f"{node_id}.png"),
    )


class TestOracleValidityContract:
    def test_valid_oracle_passes(self) -> None:
        OracleValidityContract.validate("doc-1", (_make_node("n1", "Contenido."),))

    def test_empty_list_raises(self) -> None:
        with pytest.raises(OracleValidityError):
            OracleValidityContract.validate("doc-1", ())

    def test_duplicate_node_ids_raises(self) -> None:
        with pytest.raises(OracleValidityError):
            OracleValidityContract.validate("doc-1", (_make_node("n1", "A"), _make_node("n1", "B")))

    def test_all_empty_content_raises(self) -> None:
        with pytest.raises(OracleValidityError, match="content non-emptiness"):
            OracleValidityContract.validate("doc-1", (_make_node("n1", ""), _make_node("n2", "")))

    def test_oracle_with_only_image_nodes_passes(self) -> None:
        # Corregido: un oráculo de solo imágenes no tiene nodos no-IMAGE,
        # por lo que pasa la validación de contenido.
        OracleValidityContract.validate("doc-1", (_make_image_node("img1"), _make_image_node("img2")))