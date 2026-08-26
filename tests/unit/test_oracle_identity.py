"""Tests de identidad semántica del oráculo (Wave 4.1).

Verifica NADR-15 §5.1: identidad semántica del oráculo ($H_{semantic}$).

Propiedades verificadas (8 tests):
- Determinismo: mismo contenido → mismo hash
- Sensibilidad al contenido: cambiar texto → hash diferente
- Sensibilidad al orden: cambiar orden de nodos → hash diferente
- Sensibilidad al node_id: cambiar ID → hash diferente
- Sensibilidad al node_type: cambiar tipo → hash diferente
- Sensibilidad a la estrategia: cambiar strategy → hash diferente
- Insensibilidad a metadata física: sequence_id NO afecta el hash
- Caso borde: oráculo vacío produce hash válido
"""

from __future__ import annotations

from core.ast.enums import ContentNodeType, HeadingLevel, TranslationStrategy
from core.ast.models import (
    ASTNode,
    HeadingPayload,
    ParagraphPayload,
)
from core.benchmark.ground_truth.identity import OracleSemanticIdentityCalculator


def _make_node(
    node_id: str,
    content: str = "Contenido.",
    sequence_id: int = 1,
) -> ASTNode:
    return ASTNode(
        node_id=node_id,
        sequence_id=sequence_id,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content=content),
    )


class TestOracleSemanticIdentity:
    def test_identical_oracles_produce_identical_hash(self) -> None:
        """Determinismo: mismo contenido → mismo hash."""
        oracle_a = (_make_node("n1", "Texto A"), _make_node("n2", "Texto B"))
        oracle_b = (_make_node("n1", "Texto A"), _make_node("n2", "Texto B"))

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a == hash_b

    def test_content_change_produces_different_hash(self) -> None:
        """Sensibilidad al contenido: cambiar texto → hash diferente."""
        oracle_a = (_make_node("n1", "Texto original"),)
        oracle_b = (_make_node("n1", "Texto modificado"),)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a != hash_b

    def test_node_order_change_produces_different_hash(self) -> None:
        """Sensibilidad al orden: cambiar orden → hash diferente."""
        node_1 = _make_node("n1", "Primero")
        node_2 = _make_node("n2", "Segundo")

        oracle_a = (node_1, node_2)
        oracle_b = (node_2, node_1)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a != hash_b

    def test_sequence_id_change_produces_same_hash(self) -> None:
        """Insensibilidad a metadata física: sequence_id NO afecta el hash."""
        oracle_a = (_make_node("n1", "Texto", sequence_id=1),)
        oracle_b = (_make_node("n1", "Texto", sequence_id=99),)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a == hash_b

    def test_empty_oracle_produces_valid_hash(self) -> None:
        """Caso borde: oráculo vacío produce hash válido (SHA-256 de bytes vacíos)."""
        hash_empty = OracleSemanticIdentityCalculator.calculate(())

        assert isinstance(hash_empty, str)
        assert len(hash_empty) == 64  # SHA-256 hex
        assert all(c in "0123456789abcdef" for c in hash_empty)

    def test_node_id_change_produces_different_hash(self) -> None:
        """Sensibilidad al node_id: cambiar node_id → hash diferente."""
        oracle_a = (_make_node("node-1", "Texto"),)
        oracle_b = (_make_node("node-2", "Texto"),)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a != hash_b

    def test_node_type_change_produces_different_hash(self) -> None:
        """Sensibilidad al tipo: cambiar node_type → hash diferente."""
        oracle_a = (_make_node("n1", "Texto"),)  # PARAGRAPH

        node_b = ASTNode(
            node_id="n1",
            sequence_id=1,
            node_type=ContentNodeType.HEADING,
            strategy=TranslationStrategy.TRANSLATE,
            payload=HeadingPayload(content="Texto", heading_level=HeadingLevel.H1),
        )
        oracle_b = (node_b,)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a != hash_b

    def test_strategy_change_produces_different_hash(self) -> None:
        """Sensibilidad a la estrategia: cambiar strategy → hash diferente."""
        oracle_a = (_make_node("n1", "Texto"),)  # TRANSLATE

        node_b = ASTNode(
            node_id="n1",
            sequence_id=1,
            node_type=ContentNodeType.PARAGRAPH,
            strategy=TranslationStrategy.PASSTHROUGH,  # ← Corregido: PASSTHROUGH existe
            payload=ParagraphPayload(content="Texto"),
        )
        oracle_b = (node_b,)

        hash_a = OracleSemanticIdentityCalculator.calculate(oracle_a)
        hash_b = OracleSemanticIdentityCalculator.calculate(oracle_b)

        assert hash_a != hash_b