"""
core/validation/semantic.py
Validador semántico de telemetría (SeI-01: números, SeI-02: unidades físicas).
Emite severidad WARNING. Implementa álgebra de multiconjuntos para cardinalidad numérica.
"""

import re
from typing import List
from collections import Counter
from core.validation.models import ValidationContext, ValidationResult, Severity, Scope

class SemanticValidator:
    """
    SOTA: Guardián de precisión analítica cuantitativa.
    Aplica aserciones de límites agnósticas a caracteres Unicode y previene secuencias IP.
    """

    # Lookarounds evitan fusionar palabras. Soporta un único bloque fraccionario/miles.
    NUMBER_REGEX = re.compile(r'(?<![a-zA-Z0-9.-])-?\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?(?![a-zA-Z0-9.-])')
    
    # Fronteras customizadas para soportar operadores matemáticos internos (/, ³, ·). 
    # Incluye U+00B5 y U+03BC para símbolo micro.
    # SOTA: Ordenamiento de mayor a menor complejidad para evitar cortocircuito de coincidencia parcial
    UNIT_REGEX = re.compile(
    r'(?<![a-zA-Z])(?:kg/m³|m/s|N·m|µm|μm|µs|μs|m²|m³|J/mol|°C|kW|MW|GW|W|V|kV|MV|A|mA|Hz|kHz|MHz|GHz|Pa|kPa|MPa|N|J|kJ|MJ|m|cm|mm|km|g|kg|s|ms|ns|C|K|mol|cd|ppm|dB|rpm|T|nm|%)(?![a-zA-Z])'
    )

    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        if context.scope != Scope.CHUNK:
            return results

        missing_nums = self._missing_numbers(context)
        if missing_nums:
            results.append(ValidationResult(
                invariant_id="SeI-01",
                passed=False,
                severity=Severity.WARNING,
                message=f"Posible alteración o conversión de formato numérico. Faltan: {missing_nums}",
                context=context
            ))

        missing_units = self._missing_units(context)
        if missing_units:
            results.append(ValidationResult(
                invariant_id="SeI-02",
                passed=False,
                severity=Severity.WARNING,
                message=f"Posible pérdida o traducción errónea de unidades físicas: {missing_units}",
                context=context
            ))

        return results

    def _missing_numbers(self, context: ValidationContext) -> List[str]:
        source_counts = Counter(self.NUMBER_REGEX.findall(context.source_text))
        target_counts = Counter(self.NUMBER_REGEX.findall(context.target_text))
        
        missing = []
        for num, count in source_counts.items():
            if target_counts[num] < count:
                missing.extend([num] * (count - target_counts[num]))
        return missing

    def _missing_units(self, context: ValidationContext) -> List[str]:
        source = set(self.UNIT_REGEX.findall(context.source_text))
        target = set(self.UNIT_REGEX.findall(context.target_text))
        return list(source - target)