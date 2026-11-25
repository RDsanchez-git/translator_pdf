# core/compiler/rendering/implementations.py
from math import isfinite
from typing import List
from core.compiler.rendering.policies import DocumentStructurePolicy, RenderStrategy
from core.compiler.rendering.models import RenderUnit, RenderingConfiguration, RenderGeometry
from core.compiler.rendering.image_assets import canonical_image_name
from core.ast.enums import HeadingLevel
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


class HeadingRenderStrategy(RenderStrategy):
    """R5-R7: render the actual selected text with the evidenced AST level.

    Starred structural commands avoid inventing/duplicating numbering already
    present in a source heading. G5 never translates source content.
    """

    _COMMANDS = {
        HeadingLevel.H1: r"\section*",
        HeadingLevel.H2: r"\subsection*",
        HeadingLevel.H3: r"\subsubsection*",
    }

    def render(self, unit: RenderUnit) -> str:
        # RenderUnit is a transport DTO; its optional level can be absent.
        # Explicit narrowing keeps the fail-closed contract and Pyright strict.
        level = unit.heading_level
        if level is None:
            raise ValueError(f"PPPR_G4_HEADING_LEVEL_UNVERIFIED node_id={ascii(unit.node_id)}")
        command = self._COMMANDS.get(level)
        if command is None:
            raise ValueError(f"PPPR_G4_HEADING_LEVEL_UNVERIFIED node_id={ascii(unit.node_id)}")
        if not unit.content.strip():
            raise ValueError(f"PPPR_G4_HEADING_CONTENT_MISSING node_id={ascii(unit.node_id)}")
        return f"{command}{{{TextRenderStrategy().render(unit)}}}"


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
        raise ValueError(f"PPPR_G4_UNCLASSIFIED_MIXED_RENDER_UNIT node_id={ascii(unit.node_id)}")


def usable_image_width(geometry: RenderGeometry | None) -> float | None:
    """Usable normalized width only when upstream geometry is accredited.

    RenderGeometryAdapter attests original physical provenance; verify the
    resulting DTO again at the G5 image-layout decision boundary.
    """
    if geometry is None:
        return None
    x, y, width, height = (
        geometry.relative_x, geometry.relative_y,
        geometry.relative_width, geometry.relative_height,
    )
    if not all(isfinite(v) for v in (x, y, width, height)):
        return None
    if (geometry.page_number < 1 or x < 0 or y < 0
            or width <= 0 or height <= 0 or width > 1 or height > 1
            or x + width > 1 + 1e-12 or y + height > 1 + 1e-12):
        return None
    return width


class AdaptiveFloatStrategy(RenderStrategy):
    def __init__(self, config: RenderingConfiguration):
        self._config = config

    def render(self, unit: RenderUnit) -> str:
        # IMAGE never renders unit.content as TeX: it can contain source text
        # or a persisted asset path. Only the verified digest becomes a filename.
        if unit.asset is None:
            raise ValueError("B02_G5_IMAGE_ASSET_REFERENCE_MISSING")
        name = canonical_image_name(unit.asset)
        # A protected PDF region uses its accredited crop box, not the
        # surrounding source media box. PNG rendering remains unchanged.
        crop_option = ",pagebox=cropbox" if unit.asset.mime_type == "application/pdf" else ""
        graphic = f"\\includegraphics[width=\\linewidth,keepaspectratio{crop_option}]{{assets/{name}}}"
        threshold = self._config.float_span_threshold
        if not isfinite(threshold) or not 0 < threshold < 1:
            raise ValueError("PPPR_G4_INVALID_FLOAT_SPAN_THRESHOLD")
        width = usable_image_width(unit.geometry)
        is_wide = width is not None and width > threshold
        environment = "figure*" if self._config.is_multi_column and is_wide else "figure"
        # Unknown width is not a verified narrow image. Retain a conservative
        # diagnostic representation; publication is gated by CompilationService.
        diagnostic = (
            f"% [PPPR_G4_IMAGE_WIDTH_UNVERIFIED] [NODE_ID: {ascii(unit.node_id)}]\n"
            if self._config.is_multi_column and width is None else ""
        )
        return f"{diagnostic}\\begin{{{environment}}}[htbp]\n{graphic}\n\\end{{{environment}}}"
