from core.ast.models import (
    ASTNode, 
    HeadingPayload, 
    ParagraphPayload, 
    MathPayload, 
    CodePayload, 
    ListPayload
)

class StronglyTypedTextExtractor:
    """
    SOTA: Proyección de texto estrictamente tipada.
    Cero reflexión, cero serialización. Depende del dominio, no de Pydantic.
    """
    __slots__ = ()

    def extract(self, node: ASTNode) -> str:
        payload = node.payload
        
        # Pattern Matching seguro en O(1) evaluando la jerarquía de tipos reales.
        if isinstance(payload, (HeadingPayload, ParagraphPayload, MathPayload, CodePayload, ListPayload)):
            return str(payload.content)
            
        return ""