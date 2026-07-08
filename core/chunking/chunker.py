import hashlib
import logging
from collections.abc import Iterator
from dataclasses import dataclass
from core.ast.models import ASTNode
from core.chunking.models import TranslationChunk, ChunkMetadata, BoundaryDecision
from core.chunking.protocols import TokenEstimator, NodeAtomicityPolicy, ChunkBoundaryPolicy
from core.chunking.exceptions import AtomicNodeTooLargeException, ChunkConstructionException

logger = logging.getLogger(__name__)

@dataclass(slots=True, frozen=True)
class ChunkerConfig:
    """Configuración inyectable del motor de agrupamiento."""
    soft_break_threshold: float = 0.8


class PolicyDrivenStreamingChunker:
    """
    SOTA: Acumulador iterativo puro (Zero Mutation).
    Memoria plana O(1), determinista, protegido por Back-Pressure y observable.
    """
    __slots__ = ("_estimator", "_atomicity", "_boundary", "_config")

    def __init__(
        self,
        estimator: TokenEstimator,
        atomicity_policy: NodeAtomicityPolicy,
        boundary_policy: ChunkBoundaryPolicy,
        config: ChunkerConfig | None = None
    ):
        self._estimator = estimator
        self._atomicity = atomicity_policy
        self._boundary = boundary_policy
        self._config = config or ChunkerConfig()

    def chunk(self, stream: Iterator[ASTNode], max_tokens: int) -> Iterator[TranslationChunk]:
        if max_tokens <= 0:
            raise ValueError(f"Violación de invariante: max_tokens debe ser > 0. Recibido: {max_tokens}")

        current_nodes: list[ASTNode] = []
        current_tokens = 0
        
        # Telemetría del ciclo de vida
        metrics = {"nodes_processed": 0, "chunks_generated": 0, "tokens_processed": 0}

        for node in stream:
            metrics["nodes_processed"] += 1
            node_tokens = self._estimator.estimate(node)
            is_atomic = self._atomicity.is_atomic(node)

            if is_atomic and node_tokens > max_tokens:
                raise AtomicNodeTooLargeException(
                    f"Nodo atómico excede el contexto. ID={node.node_id}, Tokens={node_tokens}, Max={max_tokens}"
                )

            decision = self._boundary.can_group(tuple(current_nodes), node)
            
            exceeds_capacity = (current_tokens + node_tokens) > max_tokens
            is_hard_break = decision == BoundaryDecision.HARD_BREAK
            is_soft_break = decision == BoundaryDecision.SOFT_BREAK and current_tokens >= (max_tokens * self._config.soft_break_threshold)

            if current_nodes and (exceeds_capacity or is_hard_break or is_soft_break):
                metrics["chunks_generated"] += 1
                metrics["tokens_processed"] += current_tokens
                yield self._build_chunk(current_nodes, current_tokens)
                current_nodes.clear()
                current_tokens = 0

            current_nodes.append(node)
            current_tokens += node_tokens

        if current_nodes:
            metrics["chunks_generated"] += 1
            metrics["tokens_processed"] += current_tokens
            yield self._build_chunk(current_nodes, current_tokens)

        # Observabilidad indexable al finalizar el stream
        logger.info(
            "Streaming chunking completed",
            extra={
                "event_id": "chunking.completed",
                "metrics": metrics
            }
        )

    def _build_chunk(self, nodes: list[ASTNode], total_tokens: int) -> TranslationChunk:
        if not nodes:
            raise ChunkConstructionException("Intento de construir un TranslationChunk vacío.")
            
        if nodes[0].sequence_id < 0 or nodes[-1].sequence_id < 0:
            raise ChunkConstructionException(
                f"Nodos con sequence_id inválido detectados en construcción de chunk. "
                f"Inicio={nodes[0].sequence_id}, Fin={nodes[-1].sequence_id}"
            )
            
        try:
            # SOTA: Hashing determinista con separador y cast estricto para evitar colisiones 
            # de concatenación y rupturas por cambios de tipado en node_id.
            chunk_hash = hashlib.sha256(
                "|".join(str(n.node_id) for n in nodes).encode("utf-8")
            ).hexdigest()
            
            return TranslationChunk(
                chunk_id=chunk_hash,
                nodes=tuple(nodes),
                metadata=ChunkMetadata(
                    estimated_tokens=total_tokens,
                    node_count=len(nodes),
                    sequence_start=nodes[0].sequence_id,
                    sequence_end=nodes[-1].sequence_id
                )
            )
        except Exception as e:
            raise ChunkConstructionException(f"Fallo estructural al construir TranslationChunk: {str(e)}") from e