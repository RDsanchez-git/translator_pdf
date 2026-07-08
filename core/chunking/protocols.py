from typing import Protocol
from collections.abc import Iterator
from core.ast.models import ASTNode
from core.chunking.models import BoundaryDecision, TranslationChunk

class TokenEstimator(Protocol):
    """
    Puerto de estimación de peso algorítmico.
    Invariante: La implementación debe ser estrictamente pura, determinista y libre de I/O.
    """
    def estimate(self, node: ASTNode) -> int:
        ...

class NodeAtomicityPolicy(Protocol):
    """Puerto de regla de negocio para dictaminar la indivisibilidad estructural de una entidad."""
    def is_atomic(self, node: ASTNode) -> bool:
        ...

class ChunkBoundaryPolicy(Protocol):
    """
    Puerto de cohesión semántica para agrupación.
    Invariante: Dictamina basándose exclusivamente en el AST ya consolidado.
    """
    def can_group(self, current_chunk_nodes: tuple[ASTNode, ...], next_node: ASTNode) -> BoundaryDecision:
        ...

class ASTChunker(Protocol):
    """
    Puerto de agregación puro.
    Invariante: Consume y emite iteradores garantizando Back-Pressure nativo en O(1) RAM.
    """
    def chunk(self, stream: Iterator[ASTNode], max_tokens: int) -> Iterator[TranslationChunk]:
        ...