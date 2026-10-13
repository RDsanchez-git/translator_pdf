"""
Tests unitarios de la clasificación semántica de efectos externos.

NADR-F18-03 §5.2 R5-R8: Verifica que la función classify_external_effect
implementa correctamente la taxonomía semántica con comportamiento
conservador por defecto.
"""
import pytest
from dataclasses import FrozenInstanceError

from core.execution.semantic_classification import (
    ExternalEffectEvidence,
    ExternalEffectKind,
    classify_external_effect,
)


class TestClassifyExternalEffect:
    """Verifica la lógica de derivación epistemológica."""

    @pytest.mark.parametrize(
        "task_state,has_generated_event,expected",
        [
            # (a) CONFIRMED: existe evento GENERATED, sin importar task_state
            ("PENDING", True, "CONFIRMED"),
            ("PROCESSING", True, "CONFIRMED"),
            ("COMPLETED", True, "CONFIRMED"),
            ("FAILED", True, "CONFIRMED"),
            ("RETRYABLE_ERROR", True, "CONFIRMED"),
            # (b) NOT_STARTED: solo PENDING sin evento demuestra no-inicio
            ("PENDING", False, "NOT_STARTED"),
            # (c) UNCERTAIN: comportamiento conservador por defecto
            ("PROCESSING", False, "UNCERTAIN"),
            ("FAILED", False, "UNCERTAIN"),
            ("RETRYABLE_ERROR", False, "UNCERTAIN"),
            ("COMPLETED", False, "UNCERTAIN"),  # defensivo: inconsistencia
            ("UNKNOWN_STATE", False, "UNCERTAIN"),  # defensivo: estado no mapeado
        ],
    )
    def test_classification_matrix(
        self, task_state: str, has_generated_event: bool, expected: ExternalEffectKind
    ) -> None:
        """Matriz completa de clasificación: 5 estados × 2 condiciones de evento."""
        evidence = ExternalEffectEvidence(
            task_state=task_state,
            has_generated_event=has_generated_event,
        )
        assert classify_external_effect(evidence) == expected

    def test_generated_event_takes_precedence_over_task_state(self) -> None:
        """NADR-F18-03 §5.2 R6: El evento GENERATED es evidencia autoritativa.
        
        Si existe evento GENERATED, la clasificación es CONFIRMED sin importar
        el estado de la tarea (incluso si la tarea aparece como FAILED).
        """
        evidence = ExternalEffectEvidence(
            task_state="FAILED",
            has_generated_event=True,
        )
        assert classify_external_effect(evidence) == "CONFIRMED"

    def test_failed_without_event_is_uncertain_not_not_started(self) -> None:
        """NADR-F18-03 §5.2 R8: Comportamiento conservador.
        
        Una tarea FAILED sin evento GENERATED NO puede clasificarse como
        NOT_STARTED porque pudo fallar POST-effecto/pre-journal (crash
        entre processor.execute() y append_wal()).
        
        Este es el caso crítico que previene reejecución automática de
        efectos externos potencialmente duplicados.
        """
        evidence = ExternalEffectEvidence(
            task_state="FAILED",
            has_generated_event=False,
        )
        result = classify_external_effect(evidence)
        assert result == "UNCERTAIN"
        assert result != "NOT_STARTED"

    def test_pure_function_determinism(self) -> None:
        """ENGINEERING_PRINCIPLES §II: Functional Core.
        
        La misma entrada produce siempre la misma salida (determinismo).
        """
        evidence = ExternalEffectEvidence(
            task_state="PROCESSING",
            has_generated_event=False,
        )
        result_1 = classify_external_effect(evidence)
        result_2 = classify_external_effect(evidence)
        assert result_1 == result_2 == "UNCERTAIN"


class TestExternalEffectEvidence:
    """Verifica el contrato del DTO de evidencia."""

    def test_evidence_is_immutable(self) -> None:
        """ENGINEERING_PRINCIPLES §III: Inmutabilidad de DTOs (frozen=True)."""
        evidence = ExternalEffectEvidence(
            task_state="PENDING",
            has_generated_event=False,
        )
        with pytest.raises(FrozenInstanceError):
            evidence.task_state = "PROCESSING"  # type: ignore[misc]
        with pytest.raises(FrozenInstanceError):
            evidence.has_generated_event = True  # type: ignore[misc]

    def test_evidence_is_hashable(self) -> None:
        """Los dataclasses frozen son hashables: pueden usarse como claves de dict."""
        evidence = ExternalEffectEvidence(
            task_state="PENDING",
            has_generated_event=False,
        )
        assert hash(evidence) == hash(evidence)

    def test_equality_is_structural(self) -> None:
        """Dos evidencias con los mismos valores son iguales (dataclass semantics)."""
        evidence_1 = ExternalEffectEvidence(task_state="PENDING", has_generated_event=False)
        evidence_2 = ExternalEffectEvidence(task_state="PENDING", has_generated_event=False)
        assert evidence_1 == evidence_2