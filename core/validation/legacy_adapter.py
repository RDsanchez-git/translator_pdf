# core/validation/legacy_adapter.py
"""
Adaptador para integrar validadores legacy (BaseValidator existente)
al nuevo contrato Validator.validate(context).
"""

from typing import Dict, List, Any
from core.validation.models import ValidationContext, ValidationResult, Severity

class UnknownLegacyValidationCodeError(Exception):
    """Se dispara cuando el motor de validación heredado emite un código no registrado en la taxonomía."""
    pass

class LegacyValidatorAdapter:
    FAMILY_MAP: Dict[str, str] = {
        "UNBALANCED_BRACES_OPEN": "SI-01",
        "UNBALANCED_BRACES_EARLY": "SI-01",
        "UNBALANCED_BRACKETS_OPEN": "SI-01",
        "UNBALANCED_BRACKETS_EARLY": "SI-01",
        "UNBALANCED_INLINE_MATH": "SI-02",
        "UNBALANCED_DISPLAY_MATH": "SI-02",
        "ENV_MISMATCH": "SI-03",
        "ENV_UNCLOSED": "SI-03",
        "RESIDUAL_HTML": "SI-04",
    }

    def __init__(self, legacy_validator: Any, severity_map: Dict[str, Severity]):
        """
        legacy_validator: clase u objeto con método validate(text: str) -> List[ValidationError]
        severity_map: diccionario que mapea código de error (ValidationError.code) a Severity.
        """
        self._legacy = legacy_validator
        self._severity_map = severity_map

    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        errors = self._legacy.validate(context.target_text)
        results: List[ValidationResult] = []
        
        for err in errors:
            severity = self._severity_map.get(err.code, Severity.HARD_FAIL)
            
            if err.code not in self.FAMILY_MAP:
                raise UnknownLegacyValidationCodeError(
                    f"Código de validación heredado '{err.code}' no está mapeado en FAMILY_MAP."
                )
                
            family = self.FAMILY_MAP[err.code]

            results.append(ValidationResult(
                invariant_id=err.code,
                passed=False,
                severity=severity,
                message=err.message,
                context=context,
                invariant_family=family
            ))
        return results