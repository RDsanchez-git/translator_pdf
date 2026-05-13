import logging

logger = logging.getLogger(__name__)

class TexBuilder:
    def __init__(self):
        # SOTA: Plantilla base adaptada para motor XeTeX (Tectonic)
        self.header = [
            "\\documentclass[11pt,a4paper]{article}",
            "\\usepackage{fontspec}",  # SOTA: Soporte Unicode nativo absoluto
            "\\usepackage{amsmath, amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{hyperref}",
            "\\begin{document}"
        ]
        self.footer = ["\\end{document}"]

    def build(self, valid_chunks: list[tuple[str, str]]) -> str:
        document = list(self.header)
        
        for node_id, text_to_render in valid_chunks:
            # SOTA: Falla explícita si el chunk materializado es nulo o vacío
            if not text_to_render or not str(text_to_render).strip():
                raise ValueError(f"CRÍTICO: El nodo {node_id} se marcó como válido pero su contenido está vacío. Integridad comprometida.")
                
            document.append(f"% [NODE_ID: {node_id}]")
            document.append(text_to_render)
            document.append("") 
                
        document.extend(self.footer)
        return "\n".join(document)