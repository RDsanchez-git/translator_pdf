import re
from typing import Final, Callable, Tuple
from dataclasses import dataclass
from core.segmenter.protocols import SegmentContext

@dataclass(frozen=True, slots=True)
class BoundaryCandidate:
    """SOTA: Parameter Object para estabilizar las firmas de las reglas."""
    text: str
    punct_start: int
    punct_end: int
    text_length: int
    context: SegmentContext

# Contrato funcional para predicados de descarte
BoundaryRule = Callable[[BoundaryCandidate], bool]

class ScientificLexicon:
    """Base de conocimiento O(1) de terminología que evade cortes oracionales."""
    PROTECTED_TOKENS: Final[frozenset[str]] = frozenset({
        "eq", "fig", "dr", "prof", "vs", "cf", "vol", "sec", "ref",
        "al", "e.g", "i.e", "inc", "ltd", "co", "ph.d", "m.sc", "b.sc",
        "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sept", "oct", "nov", "dec",
        "u.s", "u.k", "no"
    })

class ScientificBoundaryPolicy:
    """
    SOTA: Pipeline Funcional O(n) para desambiguación oracional.
    Evalúa candidatos sintácticos contra una cadena de predicados inmutables.
    """

    _PUNCTUATION_SCANNER: Final[re.Pattern] = re.compile(r'[\.\?\!]+')

    # --- DEFINICIÓN DE PREDICADOS (REGLAS PURAS) ---

    @staticmethod
    def _rule_is_decimal_or_version(candidate: BoundaryCandidate) -> bool:
        """Descarta puntos encapsulados entre dígitos (ej. 3.14, v1.2.0)."""
        if candidate.punct_start > 0 and candidate.punct_end < candidate.text_length:
            return (candidate.text[candidate.punct_start - 1].isdigit() and 
                    candidate.text[candidate.punct_end].isdigit())
        return False

    @staticmethod
    def _rule_is_protected_lexicon(candidate: BoundaryCandidate) -> bool:
        """Escáner inverso robusto para detectar tokens protegidos."""
        if candidate.punct_start == 0:
            return False

        # Escáner inverso O(1) local: extrae el token retrocediendo caracteres válidos
        ptr = candidate.punct_start - 1
        text = candidate.text
        
        while ptr >= 0 and (text[ptr].isalpha() or text[ptr] == '.'):
            ptr -= 1
            
        # Aislar y normalizar el token capturado
        word = text[ptr + 1:candidate.punct_start].lower()
        return word in ScientificLexicon.PROTECTED_TOKENS

    @staticmethod
    def _rule_invalid_continuation(candidate: BoundaryCandidate) -> bool:
        """Verifica la continuidad lógica. Una oración STEM suele seguir con Mayúscula o Números."""
        ptr = candidate.punct_end
        text = candidate.text
        
        while ptr < candidate.text_length and text[ptr].isspace():
            ptr += 1
            
        if ptr == candidate.text_length:
            return False # El final del texto es siempre una frontera válida
            
        char = text[ptr]
        # Invertimos la lógica para actuar como filtro: Si NO es una continuación válida, descartar.
        # (Se puede extender inyectando reglas de idioma desde el candidate.context)
        is_valid_start = char.isupper() or char.isdigit() or char in "([{"
        return not is_valid_start

    # --- MOTOR DE ORQUESTACIÓN OCP ---

    # Tupla inmutable de evaluación perezosa (Short-circuit).
    _RULES: Final[Tuple[BoundaryRule, ...]] = (
        _rule_is_decimal_or_version,
        _rule_is_protected_lexicon,
        _rule_invalid_continuation
    )

    def find_boundaries(self, text: str, context: SegmentContext) -> tuple[int, ...]:
        """Ejecuta el escáner nativo y filtra candidatos contra la cadena de reglas."""
        if not text:
            return ()

        boundaries = []
        text_length = len(text)

        for match in self._PUNCTUATION_SCANNER.finditer(text):
            candidate = BoundaryCandidate(
                text=text,
                punct_start=match.start(),
                punct_end=match.end(),
                text_length=text_length,
                context=context
            )

            # SOTA OCP: Evaluación funcional de todas las reglas registradas
            if any(rule(candidate) for rule in self._RULES):
                continue

            boundaries.append(candidate.punct_end)

        if not boundaries or boundaries[-1] != text_length:
            boundaries.append(text_length)

        return tuple(boundaries)