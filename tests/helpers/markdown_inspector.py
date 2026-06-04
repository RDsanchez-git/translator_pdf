import re
from typing import Dict, List

class MarkdownInspector:
    """SOTA: Extractor analítico de métricas estructurales y técnicas para Markdown/LaTeX."""

    @staticmethod
    def extract_structure(content: str) -> Dict[str, int]:
        """Cuenta elementos de diseño documental basados en especificación CommonMark y LaTeX."""
        return {
            "headings": len(re.findall(r'^#{1,6}\s+.+$', content, re.MULTILINE)),
            # SOTA Fix: Escapar el guion (\-) para evitar que sea interpretado como rango inválido
            "tables": len(re.findall(r'\|[\s-]*:?---:?[\s\-|]*\|', content)),
            "lists": len(re.findall(r'^\s*([\*\+-]|\d+\.)\s+', content, re.MULTILINE)),
            "display_equations": len(re.findall(r"\$\$.*?\$\$", content, re.DOTALL)),
            "inline_equations": len(re.findall(r"(?<!\$)\$(?!\$).*?(?<!\$)\$(?!\$)", content))
        }

    @staticmethod
    def extract_technical_tokens(content: str) -> Dict[str, List[str]]:
        """Aísla identificadores internos de referencias cruzadas e indexación académica."""
        return {
            "labels": re.findall(r'\\label\{([^}]+)\}', content),
            "refs": re.findall(r'\\ref\{([^}]+)\}', content),
            "eqrefs": re.findall(r'\\eqref\{([^}]+)\}', content),
            "cites": re.findall(r'\\cite(?:p|t)?\{([^}]+)\}', content)
        }

    @staticmethod
    def verify_balances(content: str) -> Dict[str, bool]:
        """Evalúa paridad matemática y estructural de delimitadores."""
        # TODO 11B.6.2: Implementar stack parser para delimitar anidamiento y orden real (ej. '}{')
        return {
            "braces_balanced": content.count("{") == content.count("}"),
            "brackets_balanced": content.count("[") == content.count("]"),
            "environments_balanced": (
                content.count(r"\begin{equation}") == content.count(r"\end{equation}") and
                content.count(r"\begin{align}") == content.count(r"\end{align}")
            )
        }