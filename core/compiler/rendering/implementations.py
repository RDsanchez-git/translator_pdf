from typing import List
from core.compiler.rendering.policies import DocumentStructurePolicy, RenderStrategy
from core.compiler.rendering.models import RenderUnit, RenderingConfiguration

class LatexEscaper:
    """
    DEUDA TÉCNICA (MVP): Este escaper es ciego al contexto. 
    TODO: Migrar a un Lexer AST-aware (ej. pylatexenc) o inyectar contexto de escape.
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
    def render(self, unit: RenderUnit) -> str:
        return LatexEscaper.escape(unit.content)

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
            
        # TODO: float_span_threshold (0.6) es una decisión editorial. 
        # Extraer a un PublisherProfile en futuras fases.
        is_wide = unit.geometry.relative_width > self._config.float_span_threshold
        
        if self._config.is_multi_column and is_wide:
            return f"\\begin{{figure*}}[htbp]\n{content}\n\\end{{figure*}}"
            
        return f"\\begin{{figure}}[htbp]\n{content}\n\\end{{figure}}"