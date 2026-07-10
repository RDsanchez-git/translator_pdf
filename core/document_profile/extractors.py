from typing import Protocol
from core.ast.models import ASTNode
# SOTA: Single Source of Truth. No duplicamos la taxonomía del AST.
from core.ast.enums import ContentNodeType 

class NodeGeometry(Protocol):
    @property
    def center_x(self) -> float: ...
    
    @property
    def relative_center_x(self) -> float: ...

    @property
    def page_number(self) -> int: ...

class NodeGeometryExtractor(Protocol):
    def extract(self, node: ASTNode) -> NodeGeometry | None:
        ...

class NodeSemanticAdapter(Protocol):
    """
    SOTA: Adaptador de lectura semántica. 
    Retorna el tipo canónico del AST. El agrupamiento (Grouping) 
    es responsabilidad estricta de la política del detector.
    """
    def kind(self, node: ASTNode) -> ContentNodeType | None:
        ...