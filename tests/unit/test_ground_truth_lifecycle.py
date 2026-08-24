"""Tests de la autoridad de transiciones de ciclo de vida (Task 1.2.1).

Verifica NADR-F17BIS-12 §5.2 R4 (transiciones válidas) y R6 (transiciones
gobernadas, nunca como efecto lateral).
"""

from __future__ import annotations

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload
from core.benchmark.ground_truth.lifecycle import (
    InvalidTransitionError,
    LifecycleTransitionAuthority,
)
from core.benchmark.ground_truth.models import (
    DraftSubState,
    GroundTruthDraft,
    SealedOracle,
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


def _make_draft(sub_state: DraftSubState = DraftSubState.DRAFT) -> GroundTruthDraft:
    """Construye un GroundTruthDraft con el sub_state dado."""
    return GroundTruthDraft(
        document_id="doc-123",
        nodes=(_make_node("n1"),),
        sub_state=sub_state,
    )


class TestLegalTransitions:
    """Verifica las transiciones legales (NADR-12 §5.2 R4)."""

    def test_audit_from_draft(self) -> None:
        draft = _make_draft(DraftSubState.DRAFT)
        result = LifecycleTransitionAuthority.audit(draft)
        assert isinstance(result, GroundTruthDraft)
        assert result.sub_state == DraftSubState.AUDITED

    def test_validate_from_audited(self) -> None:
        draft = _make_draft(DraftSubState.AUDITED)
        result = LifecycleTransitionAuthority.validate(draft)
        assert isinstance(result, GroundTruthDraft)
        assert result.sub_state == DraftSubState.VALIDATED

    def test_seal_from_validated(self) -> None:
        draft = _make_draft(DraftSubState.VALIDATED)
        result = LifecycleTransitionAuthority.seal(draft)
        assert isinstance(result, SealedOracle)

    def test_rollback_to_draft_from_audited(self) -> None:
        draft = _make_draft(DraftSubState.AUDITED)
        result = LifecycleTransitionAuthority.rollback_to_draft(draft)
        assert isinstance(result, GroundTruthDraft)
        assert result.sub_state == DraftSubState.DRAFT

    def test_rollback_to_audited_from_validated(self) -> None:
        draft = _make_draft(DraftSubState.VALIDATED)
        result = LifecycleTransitionAuthority.rollback_to_audited(draft)
        assert isinstance(result, GroundTruthDraft)
        assert result.sub_state == DraftSubState.AUDITED


class TestIllegalTransitions:
    """Verifica las transiciones ilegales (NADR-12 §5.2 R4)."""

    def test_cannot_validate_from_draft(self) -> None:
        draft = _make_draft(DraftSubState.DRAFT)
        with pytest.raises(InvalidTransitionError):
            LifecycleTransitionAuthority.validate(draft)

    def test_cannot_seal_from_draft(self) -> None:
        draft = _make_draft(DraftSubState.DRAFT)
        with pytest.raises(InvalidTransitionError):
            LifecycleTransitionAuthority.seal(draft)

    def test_cannot_seal_from_audited(self) -> None:
        draft = _make_draft(DraftSubState.AUDITED)
        with pytest.raises(InvalidTransitionError):
            LifecycleTransitionAuthority.seal(draft)

    def test_cannot_audit_from_audited(self) -> None:
        draft = _make_draft(DraftSubState.AUDITED)
        with pytest.raises(InvalidTransitionError):
            LifecycleTransitionAuthority.audit(draft)

    def test_cannot_audit_from_validated(self) -> None:
        draft = _make_draft(DraftSubState.VALIDATED)
        with pytest.raises(InvalidTransitionError):
            LifecycleTransitionAuthority.audit(draft)

    def test_cannot_rollback_to_draft_from_draft(self) -> None:
        draft = _make_draft(DraftSubState.DRAFT)
        with pytest.raises(InvalidTransitionError):
            LifecycleTransitionAuthority.rollback_to_draft(draft)

    def test_cannot_rollback_to_audited_from_draft(self) -> None:
        draft = _make_draft(DraftSubState.DRAFT)
        with pytest.raises(InvalidTransitionError):
            LifecycleTransitionAuthority.rollback_to_audited(draft)

    def test_cannot_rollback_to_audited_from_audited(self) -> None:
        draft = _make_draft(DraftSubState.AUDITED)
        with pytest.raises(InvalidTransitionError):
            LifecycleTransitionAuthority.rollback_to_audited(draft)


class TestSealedOracleNoRollback:
    """Verifica que SealedOracle no puede hacer rollback (NADR-12 §5.3 R9)."""

    def test_seal_produces_sealed_oracle(self) -> None:
        draft = _make_draft(DraftSubState.VALIDATED)
        sealed = LifecycleTransitionAuthority.seal(draft)
        assert isinstance(sealed, SealedOracle)

    def test_sealed_oracle_cannot_rollback(self) -> None:
        """R9: Un SealedOracle no puede ser pasado a métodos de rollback.

        SealedOracle no tiene atributo sub_state, por lo que intentar pasarlo
        a rollback_to_draft o rollback_to_audited lanza AttributeError.
        Esto materializa NADR-12 §5.3 R9: un oráculo sellado no puede ser
        alterado ni sobrescrito por ninguna operación de curaduría.
        """
        draft = _make_draft(DraftSubState.VALIDATED)
        sealed = LifecycleTransitionAuthority.seal(draft)
        assert isinstance(sealed, SealedOracle)

        # SealedOracle no tiene sub_state: no puede ser procesado por
        # los métodos de rollback que verifican sub_state.
        with pytest.raises(AttributeError):
            LifecycleTransitionAuthority.rollback_to_draft(sealed)  # type: ignore[arg-type]

        with pytest.raises(AttributeError):
            LifecycleTransitionAuthority.rollback_to_audited(sealed)  # type: ignore[arg-type]


class TestTransitionImmutability:
    """Verifica que cada transición retorna una nueva instancia (ENGINEERING_PRINCIPLES §II)."""

    def test_audit_returns_new_instance(self) -> None:
        draft = _make_draft(DraftSubState.DRAFT)
        result = LifecycleTransitionAuthority.audit(draft)
        assert result is not draft
        assert draft.sub_state == DraftSubState.DRAFT  # Original no mutado

    def test_validate_returns_new_instance(self) -> None:
        draft = _make_draft(DraftSubState.AUDITED)
        result = LifecycleTransitionAuthority.validate(draft)
        assert result is not draft
        assert draft.sub_state == DraftSubState.AUDITED  # Original no mutado

    def test_seal_returns_new_instance(self) -> None:
        draft = _make_draft(DraftSubState.VALIDATED)
        result = LifecycleTransitionAuthority.seal(draft)
        assert result is not draft
        assert isinstance(result, SealedOracle)

    def test_rollback_returns_new_instance(self) -> None:
        draft = _make_draft(DraftSubState.AUDITED)
        result = LifecycleTransitionAuthority.rollback_to_draft(draft)
        assert result is not draft
        assert draft.sub_state == DraftSubState.AUDITED  # Original no mutado

