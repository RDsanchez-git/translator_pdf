import logging
from core.ast.models import ASTNode, NodeType

logger = logging.getLogger(__name__)

class TexBuilder:
    def __init__(self):
        # SOTA: Plantilla base robusta para papers
        self.header = [
            "\\documentclass[11pt,a4paper]{article}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage[T1]{fontenc}",
            "\\usepackage{amsmath, amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{hyperref}",
            "\\begin{document}"
        ]
        self.footer = ["\\end{document}"]

    def build(self, nodes: list[ASTNode]) -> str:
        document = list(self.header)
        
        for node in nodes:
            # Priorizar el output procesado por el LLM, fallback al original
            text_to_render = getattr(node, "latex", None) or node.content
            if not text_to_render:
                continue
                
            # SOTA: Enrutamiento de renderizado por Tipado Estricto
            if node.type in (NodeType.MACRO_CHUNK, NodeType.PARAGRAPH, NodeType.SECTION):
                document.append(text_to_render)
                document.append("")  # Salto de párrafo LaTeX (\n\n implícito)
            elif node.type == NodeType.EQUATION:
                document.append(text_to_render)
            elif node.type == NodeType.IMAGE:
                document.append("% [Imagen omitida]")
            else:
                # Fallback de seguridad para no perder datos en tipos no mapeados
                document.append(text_to_render)
                
        document.extend(self.footer)
        return "\n".join(document)