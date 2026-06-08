# core/validation/legacy_adapter.py
"""
Adaptador para integrar validadores legacy (BaseValidator existente)
al nuevo contrato Validator.validate(context).
"""

from typing import Dict, List, Any
from core.validation.models import ValidationContext, ValidationResult, Severity

class LegacyValidatorAdapter:
    def __init__(
        self,
        legacy_validator: Any,
        severity_map: Dict[str, Severity]
    ):
        """
        legacy_validator: clase u objeto con método validate(text: str) -> List[ValidationError]
        severity_map: diccionario que mapea código de error (ValidationError.code) a Severity.
                      Si un código no está en el mapa, se usa HARD_FAIL por defecto.
        """
        self._legacy = legacy_validator
        self._severity_map = severity_map

    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        # Llama al método legacy con el texto destino únicamente
        errors = self._legacy.validate(context.target_text)
        results: List[ValidationResult] = []
        for err in errors:
            severity = self._severity_map.get(err.code, Severity.HARD_FAIL)
            results.append(ValidationResult(
                invariant_id=err.code,
                passed=False,
                severity=severity,
                message=err.message,
                context=context
            ))
        return results