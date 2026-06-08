"""
Contrato único para validadores (ADR-003, 11E.3.2)
Todos los validadores implementan validate(context) -> List[ValidationResult]
"""

from typing import Protocol, List
from core.validation.models import ValidationContext, ValidationResult

class Validator(Protocol):
    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        ...