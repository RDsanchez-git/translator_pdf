# core/validation/perimeter.py
"""
core/validation/perimeter.py
Validador de fronteras del payload (PeI-01 y PeI-02).
Detecta fugas estructurales de Markdown y metatexto conversacional del LLM.
"""

import re
from typing import List
from core.validation.models import ValidationContext, ValidationResult, Severity, Scope

class PerimeterValidator:
    """
    Guardián de integridad perimetral.
    Aplica escaneo monótono en una sola pasada para mitigar fugas conversacionales
    y estructurales del modelo sin introducir falsos positivos en prosa científica.
    """

    # SOTA: Regex unificado con catálogo extendido de fugas conversacionales (Español/Inglés)
    CONVERSATIONAL_LEAK_REGEX = re.compile(
        r'^\s*(?:Claro\b|Certainly\b|Of\s*course\b|Sure\b|Aquí\s*(?:tienes|está)|A\s*continuación|Traducción:|Texto\s*traducido|The\s*translated\s*text|Below\s*is\s*the\s*translation|Resultado:|Como\s*asistente\b|Lo\s*siento\b|I\s*apologize\b|Here\s*is\s*the\b)',
        re.IGNORECASE | re.MULTILINE
    )

    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        results: List[ValidationResult] = []

        if context.scope != Scope.CHUNK:
            return results

        target = context.target_text

        # PeI-01: Markdown Leakage (Triple backticks exclusivamente para no afectar macros LaTeX)
        if "```" in target:
            results.append(ValidationResult(
                invariant_id="PeI-01",
                passed=False,
                severity=Severity.HARD_FAIL,
                message="Fuga estructural: Bloque de código Markdown (```) detectado en la salida.",
                context=context
            ))

        # PeI-02: Meta-text Leakage (Single-pass validation)
        match = self.CONVERSATIONAL_LEAK_REGEX.search(target)
        if match:
            results.append(ValidationResult(
                invariant_id="PeI-02",
                passed=False,
                severity=Severity.HARD_FAIL,
                message=f"Fuga conversacional detectada en el perímetro: '{match.group().strip()}'",
                context=context
            ))

        return results