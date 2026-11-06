import re
from core.normalization.explicit_math import find_explicit_math_spans

class InlineMathProtector:
    """Preserves exact explicit LaTeX spans in G3 prompt placeholders."""
    # Explicación de la regex:
    # (?<!\$)       : Que no empiece con un $ (ignora $$)
    # (?<!\\)\$     : Un $ literal que no esté escapado por \
    # (?!\$)        : Que el siguiente no sea $ (ignora $$)
    # (.+?)         : Captura cualquier cosa (non-greedy)
    # (?<!\\)\$     : Hasta un $ de cierre que no esté escapado por \
    # (?!\$)        : Que no sea el inicio de un $$
    INLINE_MATH_PATTERN = re.compile(r'(?<!\$)(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)')

    @classmethod
    def mask(cls, text: str) -> tuple[str, dict[str, str]]:
        """Mask all whitelisted math delimiters; reject unbalanced formulas."""
        mapping: dict[str, str] = {}
        fragments: list[str] = []
        position = 0
        for start, end in find_explicit_math_spans(text):
            fragments.append(text[position:start])
            token = f"__MATH_{len(mapping)}__"
            mapping[token] = text[start:end]
            fragments.append(token)
            position = end
        fragments.append(text[position:])
        return "".join(fragments), mapping

    @classmethod
    def restore(cls, translated_text: str, mapping: dict) -> str:
        for token, original_latex in mapping.items():
            # Extraemos el índice numérico del token
            idx = token.strip('_').split('_')[-1]
            
            # Tolerancia SOTA a alucinaciones de espaciado del LLM (ej: __ MATH _ 0 __)
            safe_token_pattern = re.compile(r'__\s*MATH\s*_\s*' + str(idx) + r'\s*__', re.IGNORECASE)
            
            # El uso de lambda inhibe el parseo de secuencias de escape en original_latex
            translated_text = safe_token_pattern.sub(lambda m: original_latex, translated_text)
            
        return translated_text