# core/validation/pipeline.py
"""
ValidationPipeline: Orquestador determinista de la capa de confiabilidad.
Organiza y ejecuta los validadores registrados segregándolos por su alcance.
"""

from typing import List
from core.validation.models import ValidationContext, ValidationResult
from core.validation.base import Validator

class ValidationPipeline:
    def __init__(self) -> None:
        self._chunk_validators: List[Validator] = []
        self._document_validators: List[Validator] = []

    def add_chunk_validator(self, validator: Validator) -> None:
        """Registra de forma determinista un validador para el alcance de CHUNK."""
        self._chunk_validators.append(validator)

    def add_document_validator(self, validator: Validator) -> None:
        """Registra de forma determinista un validador para el alcance de DOCUMENT."""
        self._document_validators.append(validator)

    def validate_chunk(self, context: ValidationContext) -> List[ValidationResult]:
        """Ejecuta secuencialmente los validadores asignados al procesamiento de fragmentos."""
        return self._run_validators(self._chunk_validators, context)

    def validate_document(self, context: ValidationContext) -> List[ValidationResult]:
        """Ejecuta secuencialmente los validadores asignados a la integración global."""
        return self._run_validators(self._document_validators, context)

    @staticmethod
    def _run_validators(validators: List[Validator], context: ValidationContext) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        for validator in validators:
            results.extend(validator.validate(context))
        return results

    