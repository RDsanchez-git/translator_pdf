from typing import Protocol, Iterable, Optional
from dataclasses import dataclass
from core.ast.models import ASTNode, ASTPayload
from core.routing.models import RouteChannel


@dataclass(frozen=True, slots=True)
class SegmentContext:
    """SOTA: Parameter Object inmutable y de alta performance.
    Aísla las firmas de segmentación ante futuras inyecciones de perfilado (Fase 16.7)."""
    language_hint: Optional[str] = None
    # Espacio preparado para: document_profile, token_limits, etc.

class BoundaryPolicy(Protocol):
    """SRP: Motor matemático puro para la detección de fronteras oracionales."""
    
    def find_boundaries(self, text: str, context: SegmentContext) -> tuple[int, ...]:
        """
        Retorna una tupla de offsets absolutos [inicio_oración, ... , longitud_total].
        Ejemplo: Para un texto de 100 caracteres con dos oraciones, devuelve (0, 45, 100).
        Esto indica implícitamente los cortes: text[0:45] y text[45:100].
        La tupla garantiza inmutabilidad y seguridad entre hilos.
        """
        ...

class NodeSegmenter(Protocol):
    """Contrato perezoso (Lazy) para la transformación estructural de Nodos."""
    
    def segment(self, node: ASTNode, context: SegmentContext) -> Iterable[ASTNode]:
        """
        Produce un flujo de fragmentos inmutables propagando el linaje físico.
        Si el nodo es atómico, retorna Iterable[node_original].
        """
        ...

class TextPayload(Protocol):
    """SOTA: Contrato estructural con retorno covariante compatible con la Union del AST."""
    @property
    def content(self) -> str:
        ...

    def with_content(self, text: str) -> ASTPayload:
        """Retorna un miembro válido de la unión de payloads del dominio."""
        ...

class NodeIdentityGenerator(Protocol):
    """Puerto Hexagonal para aislar la estrategia de generación de identidades opacas."""
    def generate(self) -> str:
        ...

class NodeRouter(Protocol):
    """Puerto funcional puro para la clasificación topológica del AST."""
    
    def route(self, node: ASTNode) -> RouteChannel:
        """Determina el canal destino de forma determinista y referencialmente transparente."""
        ...
