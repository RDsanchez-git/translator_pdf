# core/compiler/rendering/implementations.py
from typing import List
from core.compiler.rendering.policies import DocumentStructurePolicy, RenderStrategy
from core.compiler.rendering.models import RenderUnit, RenderingConfiguration
from core.compiler.rendering.image_assets import canonical_image_name
from core.normalization.explicit_math import find_explicit_math_spans

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
    """Escape prose only; preserve the same explicit math spans used by G3.

    No temporary placeholders: direct span concatenation avoids collisions
    with user content and changes neither formula text nor formula delimiters.
    """

    def render(self, unit: RenderUnit) -> str:
        text = unit.content
        if not text:
            return ""
        result: list[str] = []
        position = 0
        for start, end in find_explicit_math_spans(text):
            result.append(LatexEscaper.escape(text[position:start]))
            result.append(text[start:end])
            position = end
        result.append(LatexEscaper.escape(text[position:]))
        return "".join(result)


class PassthroughRenderStrategy(RenderStrategy):
    """MVP: Agrupa ecuaciones, código y tablas temporalmente."""
    def render(self, unit: RenderUnit) -> str:
        return unit.content or ""


class LiteralProtectedRenderStrategy(RenderStrategy):
    """Render contractually literal CODE/TABLE without activating TeX commands.

    Preserves spaces and logical line boundaries explicitly; never interprets
    math-looking delimiters or macro-looking text in a literal-typed node.
    """

    @staticmethod
    def _line(text: str) -> str:
        # TeX normally collapses whitespace. Preserve each significant space
        # and tab in a monospaced group without allowing input to define macros.
        return (
            LatexEscaper.escape(text)
            .replace(" ", r"\ ")
            .replace("\t", r"\hspace*{4em}")
        )

    def render(self, unit: RenderUnit) -> str:
        if not unit.content:
            return ""
        lines = unit.content.split("\n")
        encoded = r"\par\noindent ".join(self._line(line) for line in lines)
        return "\n".join((r"\begingroup\ttfamily\raggedright", r"\noindent " + encoded, r"\par\endgroup"))


class UnclassifiedMixedRenderStrategy(RenderStrategy):
    """Fail closed: COMPOSITE_BLOCK has no per-region authority in RenderUnit."""

    def render(self, unit: RenderUnit) -> str:
        raise ValueError("PPPR_G4_UNCLASSIFIED_MIXED_RENDER_UNIT")


class AdaptiveFloatStrategy(RenderStrategy):
    def __init__(self, config: RenderingConfiguration):
        self._config = config

    def render(self, unit: RenderUnit) -> str:
        # IMAGE never renders unit.content as TeX: it can contain source text
        # or a persisted asset path. Only the verified digest becomes a filename.
        if unit.asset is None:
            raise ValueError("B02_G5_IMAGE_ASSET_REFERENCE_MISSING")
        name = canonical_image_name(unit.asset)
        graphic = f"\\includegraphics[width=\\linewidth,keepaspectratio]{{assets/{name}}}"
        is_wide = bool(unit.geometry and unit.geometry.relative_width > self._config.float_span_threshold)
        environment = "figure*" if self._config.is_multi_column and is_wide else "figure"
        return f"\\begin{{{environment}}}[htbp]\n{graphic}\n\\end{{{environment}}}"