# core/validation/adapters/structural_bridge.py
"""
Adaptador de interfaz entre StructuralValidator y el protocolo Validator.

NADR-04 §5.2 R3: StructuralValidator es invocado directamente.
Este componente NO es un LegacyValidatorAdapter:
  - No contiene severity_map externo inyectado.
  - No lanza UnknownLegacyValidationCodeError.
Es un adaptador de interfaz limpio que cumple el protocolo Validator.
"""

from typing import List, Dict
from core.validation.models import ValidationContext, ValidationResult, Severity
from core.validation.structural_validator import StructuralValidator


class StructuralValidationBridge:
    """
    Adaptador de interfaz limpio entre StructuralValidator y el protocolo Validator.

    StructuralValidator expone: validate(text: str) -> List[ValidationError]
    El protocolo Validator exige: validate(context: ValidationContext) -> List[ValidationResult]

    Este bridge realiza la traducción de firma y el mapeo de códigos a familias
    de invariantes, preservando la taxonomía de criticidad del dominio.
    """

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

    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        errors = StructuralValidator.validate(context.target_text)
        results: List[ValidationResult] = []
        for err in errors:
            family = self.FAMILY_MAP.get(err.code, "SI-UNKNOWN")
            results.append(ValidationResult(
                invariant_id=err.code,
                passed=False,
                severity=Severity.HARD_FAIL,
                message=err.message,
                context=context,
                invariant_family=family
            ))
        return results