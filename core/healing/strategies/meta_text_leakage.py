# core/healing/strategies/meta_text_leakage.py
"""Estrategia determinista para purgar preámbulos conversacionales del LLM (PeI-02)."""

import re
from core.healing.base import BaseHealingStrategy
from core.healing.models import HealingContext, HealingResult, HealingOutcome

class MetaTextLeakageHealingStrategy(BaseHealingStrategy):
    @property
    def invariant_family(self) -> str:
        return "PeI-02"

    @property
    def priority(self) -> int:
        return 120

    def heal(self, context: HealingContext) -> HealingResult:
        original = context.validation_context.target_text
        
        # SOTA: Soporte bilingüe explícito para capturar tanto 'traducción' como 'translation/translate'
        pattern = re.compile(
            r'\A\s*(?:'
            r'Claro,\s*aquí\s*(?:está|tienes)|'
            r'Aquí\s*(?:está|tienes)\s*la|'
            r'Como\s*asistente\b|'
            r'Lo\s*siento\b|'
            r'I\s*apologize\b|'
            r'Here\s*is\s*the\b|'
            r'Sure,\s*here\s*(?:is|you\s*go)\b'
            r')(?:\s*(?:la\s+|the\s+)?(?:traducc?i[oó]n|translat(?:e|ion)))?\s*[:;]?\s*',
            re.IGNORECASE
        )

        match = pattern.match(original)
        if not match:
            return HealingResult(
                invariant_family=self.invariant_family,
                strategy_id=self.__class__.__name__,
                outcome=HealingOutcome.NOT_APPLICABLE,
                original_text=original,
                changes_count=0,
                message="No se detectó prefijo conversacional en el inicio absoluto."
            )

        cleaned = pattern.sub('', original, count=1)
        
        if not cleaned.strip():
            return HealingResult(
                invariant_family=self.invariant_family,
                strategy_id=self.__class__.__name__,
                outcome=HealingOutcome.FAILURE,
                original_text=original,
                changes_count=0,
                message="La curación abortada: la purga conversacional vació el fragmento."
            )

        return HealingResult(
            invariant_family=self.invariant_family,
            strategy_id=self.__class__.__name__,
            outcome=HealingOutcome.SUCCESS,
            original_text=original,
            healed_text=cleaned,
            changes_count=1,
            message="Prefijo conversacional purgado exitosamente."
        )