import logging
from core.ast.models import ContentNodeType

logger = logging.getLogger(__name__)

# SOTA: Conjunto defensivo alineado con los string values exactos del nuevo AST semántico
LATEX_PASSTHROUGH_TYPES = {
    ContentNodeType.EQUATION.value,       # "equation"
    ContentNodeType.INLINE_EQUATION.value, # "inline_equation"
    ContentNodeType.TABLE.value,          # "table"
    ContentNodeType.CODE_BLOCK.value,     # "code_block"
    ContentNodeType.ALGORITHM.value,      # "algorithm"
    ContentNodeType.FIGURE.value,         # "figure"
    ContentNodeType.IMAGE.value,          # "image"
    ContentNodeType.MACRO_CHUNK.value,    # "macro_chunk"
    ContentNodeType.COMPOSITE_BLOCK.value # "composite_block"
}

class TexBuilder:
    def __init__(self):
        self.header = [
            "\\documentclass[11pt,a4paper]{article}",
            "\\usepackage{amsmath, amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{hyperref}",
            "\\begin{document}"
        ]
        self.footer = ["\\end{document}"]

    def build(self, valid_chunks: list) -> str:
        document = list(self.header)
        
        for chunk in valid_chunks:
            # Desempaquetado polimórfico defensivo
            if len(chunk) == 3:
                node_id, text_to_render, node_type = chunk
            else:
                node_id, text_to_render = chunk
                node_type = "paragraph"
                
            if not text_to_render or not str(text_to_render).strip():
                raise ValueError(f"CRÍTICO: El nodo {node_id} está vacío. Integridad comprometida.")
                
            safe_text = str(text_to_render)
            # Normalización homogénea en minúsculas para igualar los valores del Enum
            current_type = str(getattr(node_type, "value", node_type)).lower()
            
            # Sanitización condicional restrictiva basada en el mapa de tipos
            if current_type not in LATEX_PASSTHROUGH_TYPES:
                # Mitigación perimetral para texto plano/narrativo puro
                safe_text = safe_text.replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")
            
            document.append(f"% [NODE_ID: {node_id}] [TYPE: {current_type}]")
            document.append(safe_text)
            document.append("") 
                
        document.extend(self.footer)
        return "\n".join(document)