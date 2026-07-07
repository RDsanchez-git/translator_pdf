import logging
from types import MappingProxyType
from typing import Iterable, Mapping, cast
from core.ast.models import ASTNode
from core.segmenter.protocols import (
    NodeSegmenter, 
    BoundaryPolicy, 
    SegmentContext, 
    TextPayload, 
    NodeIdentityGenerator
)
from core.ast.enums import ContentNodeType

logger = logging.getLogger(__name__)

class AtomicSegmenter:
    """Passthrough inmutable. Respeta invariantes: segment_index = 0, parent_node_id = None."""
    
    def segment(self, node: ASTNode, context: SegmentContext) -> Iterable[ASTNode]:
        yield node


class ParagraphSegmenter:
    """Transformador Lazy agnóstico de Pydantic y de las políticas subyacentes."""
    
    def __init__(self, policy: BoundaryPolicy, id_generator: NodeIdentityGenerator):
        self._policy = policy
        self._id_generator = id_generator

    def segment(self, node: ASTNode, context: SegmentContext) -> Iterable[ASTNode]:
        payload = cast(TextPayload, node.payload)
        text = payload.content
        
        boundaries = self._policy.find_boundaries(text, context)
        
        if len(boundaries) <= 1:
            yield node
            return

        start_idx = 0
        current_segment = 1
        
        for end_idx in boundaries:
            fragment_text = text[start_idx:end_idx].strip()
            
            if fragment_text:
                new_payload = payload.with_content(fragment_text)
                
                # Delega la clonación al dominio del AST (Ocultamiento de Información)
                yield node.spawn_fragment(
                    new_id=self._id_generator.generate(),
                    new_payload=new_payload,
                    segment_index=current_segment
                )
                current_segment += 1
            
            start_idx = end_idx

        # Telemetría SRE: Trazabilidad de amplificación de nodos
        logger.debug(f"[SEG-001] Nodo {node.node_id} fragmentado en {current_segment - 1} segmentos.")


class SegmentDispatcher:
    """
    SOTA: Enrutador 100% tonto y declarativo. 
    Cumple con Arquitectura Hexagonal pura recibiendo dependencias inyectadas.
    """
    
    def __init__(self, registry: Mapping[ContentNodeType, NodeSegmenter], fallback: NodeSegmenter):
        # MappingProxyType garantiza inmutabilidad en tiempo de ejecución (Read-Only)
        self._registry = MappingProxyType(registry)
        self._fallback = fallback

    def dispatch(self, node: ASTNode) -> NodeSegmenter:
        """Enruta dinámicamente basado en las propiedades de la entidad."""
        return self._registry.get(node.node_type, self._fallback)