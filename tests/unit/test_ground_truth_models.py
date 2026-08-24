"""Tests unitarios de los modelos de dominio del Ground Truth.

Verifica NADR-F17BIS-12 §5.1 R1-R2 (Tasks 1.1.1-1.1.2):
- R1: El Ground Truth se modela como una entidad de dominio.
- R2: Tipos disjuntos para borrador curado y oráculo sellado, sin conversión
     implícita.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.ground_truth.models import (
    DraftSubState,
    GroundTruthDraft,
    GroundTruthLifecycleState,
    SealedOracle,
    hydrate_ground_truth,
)


def _make_node(node_id: str) -> ASTNode:
    """Construye un nodo AST de párrafo mínimo para pruebas."""
    return ASTNode(
        node_id=node_id,
        sequence_id=1,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content="Contenido de prueba."),
    )


class TestGroundTruthLifecycleState:
    """Verifica el vocabulario de estados de ciclo de vida."""

    def test_four_states_with_canonical_values(self) -> None:
        assert GroundTruthLifecycleState.DRAFT.value == "draft"
        assert GroundTruthLifecycleState.AUDITED.value == "audited"
        assert GroundTruthLifecycleState.VALIDATED.value == "validated"
        assert GroundTruthLifecycleState.SEALED.value == "sealed"

    def test_exactly_four_states(self) -> None:
        assert len(GroundTruthLifecycleState) == 4


class TestGroundTruthDraft:
    """Verifica el tipo disjunto GroundTruthDraft."""

    def test_draft_carries_document_id_and_nodes(self) -> None:
        nodes = (_make_node("n1"), _make_node("n2"))
        draft = GroundTruthDraft(document_id="doc-123", nodes=nodes)
        assert draft.document_id == "doc-123"
        assert draft.nodes == nodes

    def test_draft_is_immutable(self) -> None:
        draft = GroundTruthDraft(document_id="doc-123", nodes=(_make_node("n1"),))
        with pytest.raises(ValidationError):
            draft.nodes = (_make_node("n2"),)  # type: ignore[misc]
        with pytest.raises(ValidationError):
            draft.document_id = "doc-456"  # type: ignore[misc]

    def test_draft_requires_document_id_and_nodes(self) -> None:
        with pytest.raises(ValidationError):
            GroundTruthDraft()  # type: ignore[call-arg]

    def test_draft_requires_non_empty_document_id(self) -> None:
        with pytest.raises(ValidationError):
            GroundTruthDraft(document_id="", nodes=(_make_node("n1"),))

    def test_draft_accepts_empty_nodes_tuple(self) -> None:
        """Verifica que el modelo NO valida no-vaciedad.

        NOTA: La validación de no-vaciedad es responsabilidad del contrato
        de validez (Task 2.1.2), no del modelo. Este test documenta el
        comportamiento actual.
        """
        draft = GroundTruthDraft(document_id="doc-123", nodes=())
        assert draft.nodes == ()

    def test_draft_replacement_creates_new_instance(self) -> None:
        """R8: Se puede crear una nueva GroundTruthDraft con el mismo document_id.

        La creación de una nueva instancia no muta la instancia original.
        Esto materializa el reemplazo permitido durante la curaduría.
        """
        nodes_a = (_make_node("n1"),)
        nodes_b = (_make_node("n2"),)

        draft_a = GroundTruthDraft(document_id="doc-123", nodes=nodes_a)
        draft_b = GroundTruthDraft(document_id="doc-123", nodes=nodes_b)

        # Dos instancias con mismo document_id coexisten
        assert draft_a.document_id == draft_b.document_id
        assert draft_a is not draft_b

        # La creación de draft_b no mutó draft_a
        assert draft_a.nodes == nodes_a
        assert draft_b.nodes == nodes_b


class TestSealedOracle:
    """Verifica el tipo disjunto SealedOracle."""

    def test_oracle_carries_document_id_and_nodes(self) -> None:
        nodes = (_make_node("n1"), _make_node("n2"))
        oracle = SealedOracle(document_id="doc-123", nodes=nodes)
        assert oracle.document_id == "doc-123"
        assert oracle.nodes == nodes

    def test_oracle_is_immutable(self) -> None:
        oracle = SealedOracle(document_id="doc-123", nodes=(_make_node("n1"),))
        with pytest.raises(ValidationError):
            oracle.nodes = (_make_node("n2"),)  # type: ignore[misc]
        with pytest.raises(ValidationError):
            oracle.document_id = "doc-456"  # type: ignore[misc]

    def test_oracle_requires_document_id_and_nodes(self) -> None:
        with pytest.raises(ValidationError):
            SealedOracle()  # type: ignore[call-arg]

    def test_oracle_requires_non_empty_document_id(self) -> None:
        with pytest.raises(ValidationError):
            SealedOracle(document_id="", nodes=(_make_node("n1"),))

    def test_oracle_accepts_empty_nodes_tuple(self) -> None:
        """Verifica que el modelo NO valida no-vaciedad.

        NOTA: La validación de no-vaciedad es responsabilidad del contrato
        de validez (Task 2.1.2), no del modelo. Este test documenta el
        comportamiento actual.
        """
        oracle = SealedOracle(document_id="doc-123", nodes=())
        assert oracle.nodes == ()


class TestDisjointTypes:
    """Verifica NADR-F17BIS-12 §5.1 R2: tipos disjuntos sin conversión."""

    def test_draft_and_oracle_are_distinct_types(self) -> None:
        nodes = (_make_node("n1"),)
        draft = GroundTruthDraft(document_id="doc-123", nodes=nodes)
        oracle = SealedOracle(document_id="doc-123", nodes=nodes)
        assert type(draft) is not type(oracle)
        assert not isinstance(draft, SealedOracle)
        assert not isinstance(oracle, GroundTruthDraft)

    def test_no_implicit_conversion_draft_to_oracle(self) -> None:
        """Verifica que no existe conversión implícita Draft → Oracle."""
        nodes = (_make_node("n1"),)
        draft = GroundTruthDraft(document_id="doc-123", nodes=nodes)
        
        # No debe existir método de conversión implícita
        assert not hasattr(draft, "to_oracle")
        assert not hasattr(draft, "seal")
        assert not hasattr(draft, "as_oracle")

    def test_no_implicit_conversion_oracle_to_draft(self) -> None:
        """Verifica que no existe conversión implícita Oracle → Draft."""
        nodes = (_make_node("n1"),)
        oracle = SealedOracle(document_id="doc-123", nodes=nodes)
        
        # No debe existir método de conversión implícita
        assert not hasattr(oracle, "to_draft")
        assert not hasattr(oracle, "unseal")
        assert not hasattr(oracle, "as_draft")

    def test_same_document_id_different_types(self) -> None:
        """Verifica que el mismo document_id puede tener Draft y Oracle.

        Esto es válido porque son tipos disjuntos. La autoridad de sellado
        (Task 1.2.1) gobierna la transición de Draft a Oracle.
        """
        nodes = (_make_node("n1"),)
        draft = GroundTruthDraft(document_id="doc-123", nodes=nodes)
        oracle = SealedOracle(document_id="doc-123", nodes=nodes)
        
        assert draft.document_id == oracle.document_id
        assert type(draft) is not type(oracle)


class TestHydrateGroundTruth:
    """Verifica la fábrica de hidratación (NADR-F17BIS-12 §5.1 R3)."""

    def test_hydrate_draft_state_returns_ground_truth_draft(self) -> None:
        nodes = (_make_node("n1"),)
        entity = hydrate_ground_truth("doc-123", nodes, GroundTruthLifecycleState.DRAFT)
        assert isinstance(entity, GroundTruthDraft)
        assert entity.document_id == "doc-123"
        assert entity.nodes == nodes
        assert entity.sub_state == DraftSubState.DRAFT

    def test_hydrate_sealed_state_returns_sealed_oracle(self) -> None:
        nodes = (_make_node("n1"),)
        entity = hydrate_ground_truth("doc-123", nodes, GroundTruthLifecycleState.SEALED)
        assert isinstance(entity, SealedOracle)
        assert entity.document_id == "doc-123"
        assert entity.nodes == nodes

    def test_hydrate_audited_state_returns_ground_truth_draft(self) -> None:
        """AUDITED es un sub-estado del Draft (DF-06 resuelto)."""
        nodes = (_make_node("n1"),)
        entity = hydrate_ground_truth("doc-123", nodes, GroundTruthLifecycleState.AUDITED)
        assert isinstance(entity, GroundTruthDraft)
        assert entity.sub_state == DraftSubState.AUDITED

    def test_hydrate_validated_state_returns_ground_truth_draft(self) -> None:
        """VALIDATED es un sub-estado del Draft (DF-06 resuelto)."""
        nodes = (_make_node("n1"),)
        entity = hydrate_ground_truth("doc-123", nodes, GroundTruthLifecycleState.VALIDATED)
        assert isinstance(entity, GroundTruthDraft)
        assert entity.sub_state == DraftSubState.VALIDATED

    def test_hydrate_preserves_node_order(self) -> None:
        nodes = (_make_node("n1"), _make_node("n2"), _make_node("n3"))
        entity = hydrate_ground_truth("doc-123", nodes, GroundTruthLifecycleState.DRAFT)
        assert entity.nodes == nodes

    def test_hydrate_accepts_empty_nodes_tuple(self) -> None:
        """La no-vaciedad es responsabilidad de Task 2.1.2, no de la fábrica."""
        entity = hydrate_ground_truth("doc-123", (), GroundTruthLifecycleState.DRAFT)
        assert entity.nodes == ()

