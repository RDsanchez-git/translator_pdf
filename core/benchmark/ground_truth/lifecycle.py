"""Autoridad de transiciones de ciclo de vida del Ground Truth.

Materializa NADR-F17BIS-12 §5.2 R4: el ciclo de vida del Ground Truth se
define explícitamente con los estados borrador, auditado, validado y sellado,
y las únicas transiciones permitidas entre ellos.

Este servicio de dominio es stateless (ENGINEERING_PRINCIPLES §II) y gobierna
exclusivamente las transiciones de ciclo de vida. Cada transición retorna una
nueva instancia con sub_state actualizado, nunca muta la instancia origen
(ENGINEERING_PRINCIPLES §II: Inmutabilidad de DTOs).

NOTA DE SCOPE (Gate 1 vs Gates 2/3):
- Esta autoridad DEFINE las transiciones válidas (NADR-12 §5.2 R4).
- NO ejecuta validación de completitud ni validez estructural (NADR-13, Gate 2).
- NO persiste el estado sellado (NADR-14, Gate 3, DF-13).
- La transición seal() solo produce la entidad SealedOracle; la verificación
  del estado sellado es responsabilidad de Gate 3.
"""

from __future__ import annotations

from core.benchmark.ground_truth.models import (
    DraftSubState,
    GroundTruthDraft,
    SealedOracle,
)


class InvalidTransitionError(ValueError):
    """Error de transición ilegal de ciclo de vida.

    NADR-F17BIS-12 §5.2 R4: las transiciones ilegales deben fallar
    explícitamente (ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos).
    """
    pass


class LifecycleTransitionAuthority:
    """Autoridad única de transiciones de ciclo de vida del Ground Truth.

    NADR-F17BIS-12 §5.2 R4: define las únicas transiciones permitidas.
    NADR-F17BIS-12 §5.2 R6: toda transición es producida por esta autoridad,
    nunca como efecto lateral.

    Servicio stateless (ENGINEERING_PRINCIPLES §II).

    Transiciones válidas:
    - GroundTruthDraft(sub_state=DRAFT) → GroundTruthDraft(sub_state=AUDITED)
    - GroundTruthDraft(sub_state=AUDITED) → GroundTruthDraft(sub_state=VALIDATED)
    - GroundTruthDraft(sub_state=VALIDATED) → SealedOracle (sellado)
    - GroundTruthDraft(sub_state=AUDITED) → GroundTruthDraft(sub_state=DRAFT) (rollback)
    - GroundTruthDraft(sub_state=VALIDATED) → GroundTruthDraft(sub_state=AUDITED) (rollback)

    Transición prohibida:
    - SealedOracle → GroundTruthDraft (viola NADR-12 §5.3 R9)
    """

    @staticmethod
    def audit(draft: GroundTruthDraft) -> GroundTruthDraft:
        """Transición DRAFT → AUDITED.

        Retorna una nueva instancia con sub_state=AUDITED.
        """
        if draft.sub_state != DraftSubState.DRAFT:
            raise InvalidTransitionError(
                f"Invalid transition: cannot audit from '{draft.sub_state}'. "
                f"Expected sub_state=DRAFT."
            )
        return GroundTruthDraft(
            document_id=draft.document_id,
            nodes=draft.nodes,
            sub_state=DraftSubState.AUDITED,
        )

    @staticmethod
    def validate(draft: GroundTruthDraft) -> GroundTruthDraft:
        """Transición AUDITED → VALIDATED.

        Retorna una nueva instancia con sub_state=VALIDATED.
        """
        if draft.sub_state != DraftSubState.AUDITED:
            raise InvalidTransitionError(
                f"Invalid transition: cannot validate from '{draft.sub_state}'. "
                f"Expected sub_state=AUDITED."
            )
        return GroundTruthDraft(
            document_id=draft.document_id,
            nodes=draft.nodes,
            sub_state=DraftSubState.VALIDATED,
        )

    @staticmethod
    def seal(draft: GroundTruthDraft) -> SealedOracle:
        """Transición VALIDATED → SEALED.

        ADVERTENCIA: Esta transición NO valida completitud ni validez
        estructural. La validación es responsabilidad de Gate 2
        (NADR-F17BIS-13 §5.1). Esta autoridad solo define que la
        transición es válida; no la ejecuta de forma segura.

        La verificación del estado sellado es responsabilidad de Gate 3
        (NADR-F17BIS-14 §5.2, DF-13).
        """
        if draft.sub_state != DraftSubState.VALIDATED:
            raise InvalidTransitionError(
                f"Invalid transition: cannot seal from '{draft.sub_state}'. "
                f"Expected sub_state=VALIDATED."
            )
        return SealedOracle(
            document_id=draft.document_id,
            nodes=draft.nodes,
        )

    @staticmethod
    def rollback_to_draft(draft: GroundTruthDraft) -> GroundTruthDraft:
        """Transición AUDITED → DRAFT (rollback).

        Retorna una nueva instancia con sub_state=DRAFT.
        """
        if draft.sub_state != DraftSubState.AUDITED:
            raise InvalidTransitionError(
                f"Invalid transition: cannot rollback to draft from '{draft.sub_state}'. "
                f"Expected sub_state=AUDITED."
            )
        return GroundTruthDraft(
            document_id=draft.document_id,
            nodes=draft.nodes,
            sub_state=DraftSubState.DRAFT,
        )

    @staticmethod
    def rollback_to_audited(draft: GroundTruthDraft) -> GroundTruthDraft:
        """Transición VALIDATED → AUDITED (rollback).

        Retorna una nueva instancia con sub_state=AUDITED.
        """
        if draft.sub_state != DraftSubState.VALIDATED:
            raise InvalidTransitionError(
                f"Invalid transition: cannot rollback to audited from '{draft.sub_state}'. "
                f"Expected sub_state=VALIDATED."
            )
        return GroundTruthDraft(
            document_id=draft.document_id,
            nodes=draft.nodes,
            sub_state=DraftSubState.AUDITED,
        )