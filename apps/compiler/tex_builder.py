import logging

logger = logging.getLogger(__name__)

class TexBuilder:
    def __init__(self):
        # SOTA: Preámbulo minimalista XeTeX-friendly. 
        # Cero dependencias de system fonts (sin fontspec) y sin el obsoleto inputenc.
        self.header = [
            "\\documentclass[11pt,a4paper]{article}",
            "\\usepackage{amsmath, amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{hyperref}",
            "\\begin{document}"
        ]
        self.footer = ["\\end{document}"]

    def build(self, valid_chunks: list[tuple[str, str]]) -> str:
        document = list(self.header)
        
        for node_id, text_to_render in valid_chunks:
            if not text_to_render or not str(text_to_render).strip():
                raise ValueError(f"CRÍTICO: El nodo {node_id} está vacío. Integridad comprometida.")
                
            # SOTA: Sanitización determinista de Markdown LLM a LaTeX puro
            safe_text = str(text_to_render)
            safe_text = safe_text.replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")
            
            document.append(f"% [NODE_ID: {node_id}]")
            document.append(safe_text)
            document.append("") 
                
        document.extend(self.footer)
        return "\n".join(document)