# core/healing/strategies/markdown_leakage.py
"""Estrategia determinista para desenvolver contenido LaTeX encapsulado en Markdown (PeI-01)."""

import re
from core.healing.base import BaseHealingStrategy
from core.healing.models import HealingContext, HealingResult, HealingOutcome

class MarkdownLeakageHealingStrategy(BaseHealingStrategy):
    @property
    def invariant_family(self) -> str:
        return "PeI-01"

    @property
    def priority(self) -> int:
        return 110

    def heal(self, context: HealingContext) -> HealingResult:
        original = context.validation_context.target_text
        
        # Anclaje absoluto: Solo actúa si el payload entero está envuelto en una valla
        pattern = re.compile(r'\A\s*```[a-zA-Z]*\s*\n(.*?)\n\s*```\s*\Z', re.DOTALL)
        match = pattern.match(original)
        
        if not match:
            return HealingResult(
                invariant_family=self.invariant_family,
                strategy_id=self.__class__.__name__,
                outcome=HealingOutcome.NOT_APPLICABLE,
                original_text=original,
                changes_count=0,
                message="El payload no está envuelto en un bloque Markdown estricto."
            )

        cleaned = match.group(1).strip()
        
        # Protección estricta contra payload vacío (Problema 6)
        if not cleaned:
            return HealingResult(
                invariant_family=self.invariant_family,
                strategy_id=self.__class__.__name__,
                outcome=HealingOutcome.FAILURE,
                original_text=original,
                changes_count=0,
                message="La curación abortada: el desenrollado generó un contenido vacío."
            )
        
        return HealingResult(
            invariant_family=self.invariant_family,
            strategy_id=self.__class__.__name__,
            outcome=HealingOutcome.SUCCESS,
            original_text=original,
            healed_text=cleaned,
            changes_count=1,  # Unificado: Cantidad de transformaciones discretas (Problema 5)
            message="Bloque Markdown externo desenrollado exitosamente."
        )