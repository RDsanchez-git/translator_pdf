from typing import Protocol
from core.ast.models import ASTNode
from core.routing.models import RouteChannel

class NodeRouter(Protocol):
    """Puerto funcional puro para la clasificación topológica del AST."""
    
    def route(self, node: ASTNode) -> RouteChannel:
        """
        Determina el canal destino de un nodo de forma determinista.
        Invariante: A idéntico estado del nodo, idéntico canal retornado.
        """
        ...