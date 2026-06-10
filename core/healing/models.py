# core/healing/models.py
"""
core/healing/models.py
Modelos inmutables de alta velocidad para la capa de auto-healing.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from core.validation.models import ValidationContext, ValidationResult, Severity

class HealingContractViolationError(Exception):
    """Se dispara cuando se intenta vulnerar las precondiciones del ciclo de vida de curación."""
    pass

class HealingOutcome(Enum):
    """Máquina de estados para la resolución del intento de curación."""
    SUCCESS = auto()          # La reparación fue exitosa y pasó la revalidación.
    FAILURE = auto()          # La estrategia falló o la revalidación posterior arrojó HARD_FAIL.
    NOT_APPLICABLE = auto()   # La estrategia declinó actuar o no cumple las precondiciones.

@dataclass(frozen=True, slots=True)
class HealingResult:
    """
    Comprobante transaccional inmutable de curación con soporte de slots.
    """
    invariant_family: str                # Familia formal del invariante (ej. 'PeI-01')
    strategy_id: str                     # Identificador único de la estrategia ejecutada
    outcome: HealingOutcome
    original_text: str                   # Payload original corrupto proveniente del LLM
    healed_text: Optional[str] = None    # Texto completo sanitizado (listo para producción)
    changes_count: int = 0               # El significado exacto depende de la estrategia; se documenta en cada implementación concreta.
    message: str = ""                    # Justificación del descarte o traza del error

    @property
    def final_text(self) -> str:
        """
        Garantía de Rollback Atómico.
        Ignora el contenido de healed_text de forma defensiva si el outcome no es exitoso.
        """
        if self.outcome == HealingOutcome.SUCCESS and self.healed_text is not None:
            return self.healed_text
        return self.original_text

@dataclass(frozen=True, slots=True)
class HealingContext:
    """
    Contexto operacional para las estrategias de curación.
    Exige de forma determinista un ValidationResult con severidad HARD_FAIL.
    """
    validation_context: ValidationContext
    validation_result: ValidationResult   # Reporte de HARD_FAIL que detonó la intervención
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Aserción defensiva en tiempo de diseño y ejecución."""
        if self.validation_result.severity != Severity.HARD_FAIL:
            raise HealingContractViolationError(
                f"Contrato violado: El contexto de curación exige un fallo crítico (HARD_FAIL). "
                f"Recibido: '{self.validation_result.severity}' para el invariante '{self.validation_result.invariant_id}'."
            )