# core/validation/volumetric.py
from typing import List
from core.validation.models import ValidationContext, ValidationResult, Severity, Scope

class VolumetricValidator:
    """
    SOTA: Evaluador de ratio de compresión/expansión.
    """
    def __init__(self, min_ratio: float = 0.5, max_ratio: float = 2.0, min_length: int = 20):
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
        self.min_length = min_length

    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        if context.scope != Scope.CHUNK:
            return results

        src_len = len(context.source_text.strip())
        tgt_len = len(context.target_text.strip())

        # Exclusión contractual absoluta
        if src_len == 0:
            return results

        # Filtro de masa crítica NLP
        if src_len < self.min_length:
            return results

        ratio = tgt_len / src_len

        if ratio < self.min_ratio or ratio > self.max_ratio:
            results.append(ValidationResult(
                invariant_id="VI-01",
                passed=False,
                severity=Severity.WARNING,
                message=f"Deformación volumétrica detectada. Ratio: {ratio:.2f} (Límites: {self.min_ratio}-{self.max_ratio})",
                context=context
            ))

        return results