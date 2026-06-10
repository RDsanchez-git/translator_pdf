# core/healing/strategies/structural.py
"""Estrategias deterministas basadas en análisis léxico real y autómatas de estado rígidos (SI-01 y SI-02)."""

import re
from enum import Enum, auto
from core.healing.base import BaseHealingStrategy
from core.healing.models import HealingContext, HealingResult, HealingOutcome
from core.healing.config import HealingPolicy

class MathState(Enum):
    TEXT = auto()
    INLINE = auto()
    DISPLAY = auto()
    DISPLAY_TRUNCATED = auto()

class EOFBraceClosureStrategy(BaseHealingStrategy):
    def __init__(self, policy: HealingPolicy = HealingPolicy()):
        self._policy = policy

    @property
    def invariant_family(self) -> str:
        return "SI-01"

    @property
    def priority(self) -> int:
        return 210

    def heal(self, context: HealingContext) -> HealingResult:
        original = context.validation_context.target_text
        
        verbatim_block_pattern = re.compile(r'\\begin\{verbatim\}.*?\\end\{verbatim\}', re.DOTALL)
        inline_verb_pattern = re.compile(r'\\verb(.)([^\n]*?)\1')
        
        stripped = verbatim_block_pattern.sub('', original)
        stripped = inline_verb_pattern.sub('', stripped)
        
        i = 0
        open_braces = 0
        length = len(stripped)
        
        while i < length:
            if stripped[i] == '\\':
                if i + 1 < length and stripped[i+1] in ('{', '}'):
                    i += 2  # Salto de llaves escapadas \{ o \}
                    continue
                i += 1  # Avanza sobre prefijo de macros estándares (\textbf)
                continue
            
            if stripped[i] == '{':
                open_braces += 1
            elif stripped[i] == '}':
                if open_braces > 0:
                    open_braces -= 1
            i += 1

        if open_braces == 0:
            return HealingResult(
                invariant_family=self.invariant_family,
                strategy_id=self.__class__.__name__,
                outcome=HealingOutcome.NOT_APPLICABLE,
                original_text=original,
                changes_count=0,
                message="No structural brace imbalance detected at EOF."
            )

        if open_braces > self._policy.max_autofix_braces:
            return HealingResult(
                invariant_family=self.invariant_family,
                strategy_id=self.__class__.__name__,
                outcome=HealingOutcome.FAILURE,
                original_text=original,
                changes_count=0,
                message=f"Massive corruption: {open_braces} open braces exceed policy limit."
            )

        cleaned = original + ("}" * open_braces)
        return HealingResult(
            invariant_family=self.invariant_family,
            strategy_id=self.__class__.__name__,
            outcome=HealingOutcome.SUCCESS,
            original_text=original,
            healed_text=cleaned,
            changes_count=1,
            message=f"Closed {open_braces} trailing structural braces."
        )

class EOFMathClosureStrategy(BaseHealingStrategy):
    def __init__(self, policy: HealingPolicy = HealingPolicy()):
        self._policy = policy

    @property
    def invariant_family(self) -> str:
        return "SI-02"

    @property
    def priority(self) -> int:
        return 220

    def heal(self, context: HealingContext) -> HealingResult:
        original = context.validation_context.target_text
        
        i = 0
        length = len(original)
        state = MathState.TEXT
        
        while i < length:
            if original[i] == '\\':
                if i + 1 < length and original[i+1] == '$':
                    i += 2  # Supresión léxica de escapes \$
                    continue
                i += 1
                continue
            
            if original[i:i+2] == '$$':
                if state == MathState.TEXT:
                    state = MathState.DISPLAY
                elif state == MathState.DISPLAY:
                    state = MathState.TEXT
                i += 2
                continue
                
            if original[i] == '$':
                if state == MathState.TEXT:
                    state = MathState.INLINE
                elif state == MathState.INLINE:
                    state = MathState.TEXT
                elif state == MathState.DISPLAY:
                    state = MathState.DISPLAY_TRUNCATED
                elif state == MathState.DISPLAY_TRUNCATED:
                    state = MathState.TEXT
                i += 1
                continue
            i += 1

        if state == MathState.TEXT:
            return HealingResult(
                invariant_family=self.invariant_family,
                strategy_id=self.__class__.__name__,
                outcome=HealingOutcome.NOT_APPLICABLE,
                original_text=original,
                changes_count=0,
                message="Math environments are balanced."
            )

        # SOTA: Preserva la maquetación (saltos de línea) omitiendo rstrip destructivos
        if state == MathState.DISPLAY_TRUNCATED:
            base_text = original.rstrip()
            if base_text.endswith('$') and not base_text.endswith('\\$'):
                cleaned = base_text[:-1] + "$$"
            else:
                cleaned = base_text + "$$"
            closure = "$$"
        elif state == MathState.DISPLAY:
            cleaned = original.rstrip() + "$$"
            closure = "$$"
        else:
            cleaned = original.rstrip() + "$"
            closure = "$"

        return HealingResult(
            invariant_family=self.invariant_family,
            strategy_id=self.__class__.__name__,
            outcome=HealingOutcome.SUCCESS,
            original_text=original,
            healed_text=cleaned,
            changes_count=1,
            message=f"Closed math environment using token: {closure}"
        )