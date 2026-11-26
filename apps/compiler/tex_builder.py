import logging
from typing import List
from core.compiler.rendering.models import RenderUnit
from core.compiler.rendering.context import RenderContext

logger = logging.getLogger(__name__)

class TexBuilder:
    """
    SOTA: Compilador Inversion-of-Control (Release Candidate).
    Cero lógica de negocio, cero strings mágicos, 100% delegación de estrategias.
    """
    def __init__(self, context: RenderContext):
        self._context = context

    def build(self, units: List[RenderUnit]) -> str:
        document = self._context.structure.begin_document()
        
        for unit in units:
            rendered_content = self._context.render_unit(unit)
            
            if rendered_content:
                # Keep arbitrary DTO metadata inside one TeX comment line.
                # ascii() quotes the identifier and escapes all control,
                # newline, and non-ASCII characters without changing identity.
                document.append(
                    f"% [NODE_ID: {ascii(unit.node_id)}] [TYPE: {unit.node_type.value}]"
                )
                document.append(rendered_content)
                document.append("") 
                
        document.extend(self._context.structure.end_document())
        return "\n".join(document)