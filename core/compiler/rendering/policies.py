from typing import Protocol, List
from core.compiler.rendering.models import RenderUnit

class DocumentStructurePolicy(Protocol):
    """SRP: Gobierna la topología global, encabezados y cierres del documento."""
    def begin_document(self) -> List[str]: ...
    def end_document(self) -> List[str]: ...

class RenderStrategy(Protocol):
    """SRP: Contrato universal para estrategias de renderizado (Reemplaza a NodeRenderer)."""
    def render(self, unit: RenderUnit) -> str: ...