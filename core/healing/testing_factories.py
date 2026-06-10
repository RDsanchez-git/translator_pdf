# core/healing/testing_factories.py
"""Factory helpers para desacoplar los tests de las mutaciones de contratos de validación."""

from core.validation.models import ValidationContext, ValidationResult, Scope, Severity
from core.healing.models import HealingContext

def make_test_healing_context(
    text: str, 
    family: str, 
    invariant_id: str, 
    severity: Severity = Severity.HARD_FAIL
) -> HealingContext:
    """SOTA: Abstracción de bajo acoplamiento para instanciación de contextos de prueba."""
    val_ctx = ValidationContext(
        source_text="\\section{Original Source}", 
        target_text=text, 
        scope=Scope.CHUNK
    )
    val_res = ValidationResult(
        invariant_id=invariant_id,
        invariant_family=family,
        passed=False,
        severity=severity,
        message="Simulated test validation failure",
        context=val_ctx
    )
    return HealingContext(validation_context=val_ctx, validation_result=val_res)