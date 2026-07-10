
from core.compiler.rendering.models import RenderingConfiguration

class LatexEscaper:
    """SOTA: Sanitización formal de caracteres reservados. Evita inyecciones de comandos."""
    
    _ESCAPE_MAP = {
        '\\': r'\textbackslash{}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}'
    }
    _TRANSLATION_TABLE = str.maketrans(_ESCAPE_MAP)

    @classmethod
    def escape(cls, text: str) -> str:
        if not text:
            return ""
        return text.translate(cls._TRANSLATION_TABLE)

class LatexPreambleBuilder:
    """SOTA: Constructor dinámico de dependencias."""
    
    @staticmethod
    def build(config: 'RenderingConfiguration') -> list[str]:
        doc_class = "\\documentclass[11pt,a4paper,twocolumn]{article}" if config.is_multi_column else "\\documentclass[11pt,a4paper]{article}"
        
        preamble = [
            doc_class,
            "\\usepackage{amsmath, amssymb}",
            "\\usepackage{graphicx}"
        ]
        
        if config.is_multi_column:
            preamble.append("\\usepackage{dblfloatfix}")
            
        preamble.extend([
            "\\usepackage{hyperref}",
            "\\begin{document}"
        ])
        
        return preamble