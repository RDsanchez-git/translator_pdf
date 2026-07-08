# core/pipeline/protocols.py
from typing import Protocol
from core.ast.models import ASTNode

class PassthroughSink(Protocol):
    """
    Puerto de infraestructura para nodos estructurales.
    
    Contrato de Resiliencia:
    Si sink() retorna normalmente, el nodo se considera persistido.
    Si no puede garantizar la persistencia de forma síncrona, DEBE lanzar una excepción.
    """
    def sink(self, node: ASTNode) -> None:
        ...