"""Tests de validación de dominio para modelos AST (Wave 2.2 Fase 3).

Verifica NADR-F17BIS-17 §5.1 R1-R4:
- Contratos de dominio formalmente definidos y validados
- Validación fail-fast en construcción de ASTNode
- Inyectividad del encoding: ':' prohibido en node_id y parent_node_id
- Sentinel: node_id es obligatorio (no tiene sentinel)

Tests de fail-fast para node_id inválido (Task 2.2.2).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import (
    ASTNode,
    ImagePayload,
    ParagraphPayload,
)


def _make_node(
    node_id: str = "node-1",
    content: str = "Contenido válido.",
) -> ASTNode:
    """Factory helper para construir ASTNode en tests."""
    return ASTNode(
        node_id=node_id,
        sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content=content),
    )


class TestNodeIdDomainContract:
    """Task 2.2.2: Tests de fail-fast para node_id inválido.

    NADR-F17BIS-17 §5.1 R3-R4: la validación de dominio MUST aplicarse
    mediante fail-fast (rechazo explícito en construcción), no mediante
    advertencias silenciosas.
    """

    def test_valid_node_id_with_alphanumeric_and_hyphens(self) -> None:
        """node_id con caracteres válidos se acepta."""
        node = _make_node("node-abc-123")
        assert node.node_id == "node-abc-123"

    def test_valid_node_id_with_dots_and_underscores(self) -> None:
        """node_id con puntos y guiones bajos se acepta."""
        node = _make_node("node.v2_final")
        assert node.node_id == "node.v2_final"

    def test_valid_node_id_with_spaces(self) -> None:
        """node_id con espacios se acepta porque no contiene ':'."""
        node = _make_node("node 01")
        assert node.node_id == "node 01"

    def test_valid_node_id_single_char(self) -> None:
        """node_id de un solo carácter es válido si no contiene ':'."""
        node = _make_node("n")
        assert node.node_id == "n"

    def test_colon_in_middle_of_node_id_raises_validation_error(self) -> None:
        """Fail-fast: node_id con ':' en medio lanza ValidationError."""
        with pytest.raises(ValidationError, match="node_id"):
            _make_node("node:invalid")

    def test_colon_at_start_of_node_id_raises_validation_error(self) -> None:
        """Fail-fast: ':' al inicio también es rechazado."""
        with pytest.raises(ValidationError, match="node_id"):
            _make_node(":node")

    def test_colon_at_end_of_node_id_raises_validation_error(self) -> None:
        """Fail-fast: ':' al final también es rechazado."""
        with pytest.raises(ValidationError, match="node_id"):
            _make_node("node:")

    def test_multiple_colons_in_node_id_raises_validation_error(self) -> None:
        """Fail-fast: múltiples ':' también son rechazados."""
        with pytest.raises(ValidationError, match="node_id"):
            _make_node("a:b:c")

    def test_only_colon_as_node_id_raises_validation_error(self) -> None:
        """Fail-fast: node_id que es solo ':' es rechazado."""
        with pytest.raises(ValidationError, match="node_id"):
            _make_node(":")

    def test_empty_node_id_raises_validation_error(self) -> None:
        """Fail-fast: node_id vacío es rechazado (min_length=1)."""
        with pytest.raises(ValidationError, match="node_id"):
            _make_node("")


class TestParentNodeIdDomainContract:
    """Tests de contrato de dominio para parent_node_id.

    parent_node_id tiene el mismo contrato que node_id (Optional[NodeId])
    para garantizar consistencia de dominio: ninguna referencia a un node_id
    puede contener el delimitador ':'.
    """

    def test_parent_node_id_none_is_valid(self) -> None:
        """parent_node_id=None es válido (nodo raíz)."""
        node = _make_node("node-1")
        assert node.parent_node_id is None

    def test_parent_node_id_with_valid_value(self) -> None:
        """parent_node_id con valor válido se acepta."""
        node = ASTNode(
            node_id="child-1",
            sequence_id=1,
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Hijo."),
            parent_node_id="parent-1",
        )
        assert node.parent_node_id == "parent-1"

    def test_parent_node_id_with_colon_raises_validation_error(self) -> None:
        """Fail-fast: parent_node_id con ':' es rechazado."""
        with pytest.raises(ValidationError, match="parent_node_id"):
            ASTNode(
                node_id="child-1",
                sequence_id=1,
                node_type=ContentNodeType.PARAGRAPH,
                payload=ParagraphPayload(content="Hijo."),
                parent_node_id="parent:invalid",
            )

    def test_spawn_fragment_sets_parent_node_id_from_self(self) -> None:
        """spawn_fragment asigna parent_node_id=self.node_id (ya validado)."""
        parent = _make_node("parent-1")
        fragment = parent.spawn_fragment(
            new_id="fragment-1",
            new_payload=ParagraphPayload(content="Fragmento."),
            segment_index=1,
        )
        assert fragment.parent_node_id == "parent-1"


class TestASTNodeInvariants:
    """Tests de invariantes generales de ASTNode."""

    def test_ast_node_is_immutable(self) -> None:
        """Inmutabilidad: intentar mutar un campo lanza ValidationError."""
        node = _make_node("node-1")
        with pytest.raises(ValidationError):
            node.node_id = "mutated"  # type: ignore[misc]

    def test_text_content_returns_payload_content(self) -> None:
        """text_content expone el contenido textual del payload."""
        node = _make_node("node-1", content="Texto fuente.")
        assert node.text_content == "Texto fuente."

    def test_has_valid_sequence_true_when_sequence_id_positive(self) -> None:
        """has_valid_sequence=True si sequence_id >= 1."""
        node = _make_node("node-1")
        assert node.has_valid_sequence is True

    def test_has_valid_sequence_false_when_sequence_id_default(self) -> None:
        """has_valid_sequence=False si sequence_id < 1."""
        node = ASTNode(
            node_id="node-1",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Texto."),
        )
        assert node.sequence_id == -1
        assert node.has_valid_sequence is False

    def test_image_payload_has_empty_text_content(self) -> None:
        """Nodos IMAGE no exponen contenido textual."""
        node = ASTNode(
            node_id="image-1",
            sequence_id=1,
            node_type=ContentNodeType.IMAGE,
            strategy=TranslationStrategy.PASSTHROUGH,
            payload=ImagePayload(asset_path="figure.png"),
        )
        assert node.text_content == ""

    def test_payload_string_is_discriminated_to_paragraph_payload(self) -> None:
        """El validador before conserva compatibilidad con payload como string.

        Nota: El type hint del campo payload es ASTPayload, pero el validator
        _discriminate_payload acepta strings en runtime para compatibilidad
        con código legacy. Este test verifica ese comportamiento.
        """
        node = ASTNode(
            node_id="node-1",
            sequence_id=1,
            node_type=ContentNodeType.PARAGRAPH,
            payload="Texto como string",  # type: ignore[arg-type]
        )
        assert isinstance(node.payload, ParagraphPayload)
        assert node.text_content == "Texto como string"

    def test_with_strategy_returns_same_instance_when_strategy_unchanged(self) -> None:
        """with_strategy retorna self si la estrategia no cambia."""
        node = _make_node("node-1")
        result = node.with_strategy(TranslationStrategy.TRANSLATE)
        assert result is node

    def test_with_strategy_returns_new_instance_when_strategy_changes(self) -> None:
        """with_strategy retorna nueva instancia si la estrategia cambia."""
        node = _make_node("node-1")
        result = node.with_strategy(TranslationStrategy.PASSTHROUGH)

        assert result is not node
        assert result.node_id == node.node_id
        assert result.strategy == TranslationStrategy.PASSTHROUGH

    def test_with_sequence_id_returns_new_instance_with_updated_sequence(self) -> None:
        """with_sequence_id actualiza sequence_id preservando node_id válido."""
        node = _make_node("node-1")
        result = node.with_sequence_id(42)

        assert result is not node
        assert result.node_id == "node-1"
        assert result.sequence_id == 42


class TestASTNodeSpawnFragment:
    """Tests de spawn_fragment y preservación del contrato NodeId.

    SOTA: spawn_fragment debe pasar por el constructor validado porque
    model_copy(update=...) no revalida campos en Pydantic v2.
    """

    def test_spawn_fragment_with_valid_node_id_creates_child_node(self) -> None:
        """spawn_fragment crea un nodo hijo con node_id válido."""
        parent = _make_node("parent-1")
        fragment = parent.spawn_fragment(
            new_id="fragment-1",
            new_payload=ParagraphPayload(content="Fragmento."),
            segment_index=1,
        )

        assert fragment.node_id == "fragment-1"
        assert fragment.parent_node_id == "parent-1"
        assert fragment.segment_index == 1
        assert fragment.payload == ParagraphPayload(content="Fragmento.")
        assert fragment.node_type == parent.node_type
        assert fragment.strategy == parent.strategy
        assert fragment.sequence_id == parent.sequence_id

    def test_spawn_fragment_with_colon_in_node_id_raises_validation_error(self) -> None:
        """Fail-fast: spawn_fragment no puede saltarse el contrato NodeId."""
        parent = _make_node("parent-1")

        with pytest.raises(ValidationError, match="node_id"):
            parent.spawn_fragment(
                new_id="fragment:invalid",
                new_payload=ParagraphPayload(content="Fragmento."),
                segment_index=1,
            )

    def test_spawn_fragment_with_empty_node_id_raises_validation_error(self) -> None:
        """Fail-fast: spawn_fragment rechaza node_id vacío."""
        parent = _make_node("parent-1")

        with pytest.raises(ValidationError, match="node_id"):
            parent.spawn_fragment(
                new_id="",
                new_payload=ParagraphPayload(content="Fragmento."),
                segment_index=1,
            )

    def test_spawn_fragment_control_plane_is_defensively_copied(self) -> None:
        """spawn_fragment copia control_plane para evitar aliasing accidental."""
        parent = ASTNode(
            node_id="parent-1",
            sequence_id=1,
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Texto."),
            control_plane={"source": "test"},
        )

        fragment = parent.spawn_fragment(
            new_id="fragment-1",
            new_payload=ParagraphPayload(content="Fragmento."),
            segment_index=1,
        )

        assert fragment.control_plane == {"source": "test"}
        assert fragment.control_plane is not parent.control_plane