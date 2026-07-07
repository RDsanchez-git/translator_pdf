import uuid
import logging
from typing import Iterable, List
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.segmenter.protocols import SegmentContext
from core.segmenter.policies import ScientificBoundaryPolicy
from core.segmenter.segmenters import AtomicSegmenter, ParagraphSegmenter, SegmentDispatcher
from core.segmenter.normalizer import ASTSequenceNormalizer

logger = logging.getLogger(__name__)

class UUIDIdentityGenerator:
    """Implementación SOTA del puerto NodeIdentityGenerator. Genera identidades opacas V4."""
    def generate(self) -> str:
        return uuid.uuid4().hex


class SegmenterService:
    """
    Orquestador de Casos de Uso (Application Service).
    Gobierna el flujo de entrada, despacho, aplanamiento y normalización.
    """
    
    def __init__(self, dispatcher: SegmentDispatcher, normalizer: ASTSequenceNormalizer):
        self._dispatcher = dispatcher
        self._normalizer = normalizer

    def process_document(self, nodes: Iterable[ASTNode], context: SegmentContext) -> List[ASTNode]:
        """Ejecuta el pipeline de fragmentación y emite la colección topológicamente estable."""
        
        segmented_stream: List[ASTNode] = []
        original_count = 0
        
        # 1. Transformación (1 a N)
        for node in nodes:
            original_count += 1
            try:
                segmenter = self._dispatcher.dispatch(node)
                # El método extend consume el yield O(1) de los transformadores eficientemente
                segmented_stream.extend(segmenter.segment(node, context))
            except Exception as e:
                # SRE Guardrail: En caso de falla catastrófica en un segmentador, 
                # se preserva la entidad original intacta para no corromper el pipeline.
                logger.error(f"[SEG-002] Fallo al segmentar nodo {node.node_id}: {e}. Retornando nodo intacto.")
                segmented_stream.append(node)
                
        # 2. Reparación Topológica Lineal O(n)
        final_nodes = self._normalizer.normalize(segmented_stream)
        
        # Telemetría Global
        logger.info(
            f"[SEG-003] Segmentación completada. Nodos originales: {original_count}. "
            f"Nodos resultantes: {len(final_nodes)}."
        )
        
        return final_nodes


class SegmenterBootstrap:
    """
    Factoría de Inyección de Dependencias (DI Container).
    Ensambla el grafo de objetos garantizando el aislamiento de los componentes puros.
    """
    
    @staticmethod
    def create() -> SegmenterService:
        # Instanciación de dependencias base
        id_gen = UUIDIdentityGenerator()
        policy = ScientificBoundaryPolicy()
        
        # Instanciación de estrategias
        atomic = AtomicSegmenter()
        paragraph = ParagraphSegmenter(policy=policy, id_generator=id_gen)
        
        # Tabla de enrutamiento inmutable
        registry = {
            ContentNodeType.PARAGRAPH: paragraph,
            ContentNodeType.CAPTION: paragraph
        }
        
        # Ensamblado del Dispatcher y Normalizador
        dispatcher = SegmentDispatcher(registry=registry, fallback=atomic)
        normalizer = ASTSequenceNormalizer()
        
        return SegmenterService(dispatcher=dispatcher, normalizer=normalizer)