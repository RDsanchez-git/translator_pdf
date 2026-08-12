# core/compiler/rendering/implementations.py
from typing import List
from core.compiler.rendering.policies import DocumentStructurePolicy, RenderStrategy
from core.compiler.rendering.models import RenderUnit, RenderingConfiguration
import re
from typing import Dict

class LatexEscaper:
    """
    Escapado de caracteres reservados de LaTeX.

    NADR-06 §5.2 R1-R3: Este componente opera exclusivamente sobre texto
    prosa ya saneado de regiones matemáticas. La protección de sintaxis
    matemática es responsabilidad del caller (TextRenderStrategy).

    No aplicar directamente sobre texto que pueda contener LaTeX legítimo.
    """
    _ESCAPE_MAP = {
        '\\': r'\textbackslash{}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}'
    }
    _TRANSLATION_TABLE = str.maketrans(_ESCAPE_MAP)

    @classmethod
    def escape(cls, text: str) -> str:
        if not text:
            return ""
        return text.translate(cls._TRANSLATION_TABLE)


class LatexPreambleBuilder:
    @staticmethod
    def build(config: RenderingConfiguration) -> List[str]:
        doc_class = "\\documentclass[11pt,a4paper,twocolumn]{article}" if config.is_multi_column else "\\documentclass[11pt,a4paper]{article}"
        preamble = [doc_class, "\\usepackage{amsmath, amssymb}", "\\usepackage{graphicx}"]
        if config.is_multi_column:
            preamble.append("\\usepackage{dblfloatfix}")
        preamble.extend(["\\usepackage{hyperref}", "\\begin{document}"])
        return preamble


class DynamicDocumentStructure(DocumentStructurePolicy):
    def __init__(self, config: RenderingConfiguration):
        self._config = config

    def begin_document(self) -> List[str]:
        return LatexPreambleBuilder.build(self._config)

    def end_document(self) -> List[str]:
        return ["\\end{document}"]




class TextRenderStrategy(RenderStrategy):
    """
    NADR-06 §5.2 R1-R3: Escapado consciente del contexto.

    Preserva sintaxis matemática inline ($...$) y display ($$...$$) intacta.
    Escapa exclusivamente el texto prosa fuera de regiones matemáticas.

    Flujo: mask(display math) → mask(inline math) → escape(prose) → restore

    NOTA: No se usa InlineMathProtector directamente porque sus tokens
    (__MATH_N__) contienen '_' que es escapado por LatexEscaper, haciendo
    que restore() no pueda encontrarlos post-escape. Se usa protección
    local con tokens Unicode inmunes al escape.
    """

    # Display math: $$...$$ (se protege PRIMERO para evitar confusión con dos $...$)
    _DISPLAY_MATH_RE = re.compile(r'\$\$(.+?)\$\$', re.DOTALL)
    # Inline math: $...$ (no $$, no escapado por \)
    _INLINE_MATH_RE = re.compile(r'(?<!\$)(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)')

    def render(self, unit: RenderUnit) -> str:
        text = unit.content
        if not text:
            return ""

        vault: Dict[str, str] = {}
        counter = [0]

        def _make_token() -> str:
            # Tokens con ⟪ ⟫ (U+27EA/U+27EB): NO están en la tabla de escape
            token = f"⟪TEXRENDER{counter[0]}⟫"
            counter[0] += 1
            return token

        # 1. Proteger display math ($$...$$) primero
        def _display_replacer(match: re.Match) -> str:
            token = _make_token()
            vault[token] = match.group(0)
            return token

        text = self._DISPLAY_MATH_RE.sub(_display_replacer, text)

        # 2. Proteger inline math ($...$)
        def _inline_replacer(match: re.Match) -> str:
            token = _make_token()
            vault[token] = match.group(0)
            return token

        text = self._INLINE_MATH_RE.sub(_inline_replacer, text)

        # 3. Escapar solo el texto prosa (regiones math están enmascaradas)
        text = LatexEscaper.escape(text)

        # 4. Restaurar todas las regiones matemáticas preservadas
        for token, original in vault.items():
            text = text.replace(token, original)

        return text


class PassthroughRenderStrategy(RenderStrategy):
    """MVP: Agrupa ecuaciones, código y tablas temporalmente."""
    def render(self, unit: RenderUnit) -> str:
        return unit.content or ""


class AdaptiveFloatStrategy(RenderStrategy):
    def __init__(self, config: RenderingConfiguration):
        self._config = config

    def render(self, unit: RenderUnit) -> str:
        content = unit.content or ""

        if not unit.geometry:
            return f"\\begin{{figure}}[htbp]\n{content}\n\\end{{figure}}"

        is_wide = unit.geometry.relative_width > self._config.float_span_threshold

        if self._config.is_multi_column and is_wide:
            return f"\\begin{{figure*}}[htbp]\n{content}\n\\end{{figure*}}"

        return f"\\begin{{figure}}[htbp]\n{content}\n\\end{{figure}}"