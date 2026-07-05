import logging
from typing import List, Dict, Final, Callable, Any
from core.layout.models import LayoutBlockCollection, LayoutBlockDraft
from core.ast.enums import ContentNodeType, HeadingLevel, SemanticOrigin
from core.ast.models import (
    ASTNode, NodeMetadata, ASTPayload,
    HeadingPayload, ParagraphPayload, MathPayload, CodePayload, 
    TablePayload, ImagePayload, ListPayload
)
from core.ast.strategy import resolve_strategy
from core.ast.cross_page import CrossPageNormalizer

logger = logging.getLogger(__name__)

# Contrato estático de inyección: Función que recibe (datos_crudos, kwargs) y devuelve un ASTPayload
PayloadFactoryMethod = Callable[[str, Dict[str, Any]], ASTPayload]

class PayloadRegistry:
    """SOTA: Factoría OCP-Compliant y Type-Safe. 
    Usa un registro de delegados para instanciar firmas heterogéneas sin usar if/elif, 
    satisfaciendo simultáneamente el tipado estricto de Pylance y el Open/Closed Principle."""
    
    _REGISTRY: Final[Dict[ContentNodeType, PayloadFactoryMethod]] = {
        ContentNodeType.HEADING: lambda r, kw: HeadingPayload(
            content=r, 
            heading_level=kw.get('heading_level', HeadingLevel.UNKNOWN)
        ),
        ContentNodeType.PARAGRAPH: lambda r, kw: ParagraphPayload(content=r),
        ContentNodeType.DISPLAY_EQUATION: lambda r, kw: MathPayload(content=r),
        ContentNodeType.INLINE_EQUATION: lambda r, kw: MathPayload(content=r),
        ContentNodeType.CODE: lambda r, kw: CodePayload(content=r),
        ContentNodeType.TABLE_SIMPLE: lambda r, kw: TablePayload(content=r),
        ContentNodeType.TABLE_COMPLEX: lambda r, kw: TablePayload(content=r),
        ContentNodeType.IMAGE: lambda r, kw: ImagePayload(asset_path=r),
        ContentNodeType.LIST: lambda r, kw: ListPayload(content=r),
        ContentNodeType.COMPOSITE_BLOCK: lambda r, kw: ParagraphPayload(content=r),
    }

    @classmethod
    def create(cls, node_type: ContentNodeType, raw_data: str, **kwargs) -> ASTPayload:
        factory_method = cls._REGISTRY.get(node_type)
        if not factory_method:
            raise ValueError(f"[AST-003] [PAYLOAD_CREATION_FAILED] Tipo '{node_type}' no registrado en PayloadRegistry.")
            
        return factory_method(raw_data, kwargs)


class FlatASTBuilder:
    """Orquestador Inmutable O(n) de la Fase 16.2.
    Opera estrictamente como una tubería funcional (Pipeline)."""

    _TYPE_MAPPING: Final[Dict[str, ContentNodeType]] = {
        "TITLE": ContentNodeType.HEADING,
        "HEADING": ContentNodeType.HEADING,
        "PARAGRAPH": ContentNodeType.PARAGRAPH,
        "TEXT": ContentNodeType.PARAGRAPH,
        "TABLE": ContentNodeType.TABLE_SIMPLE,
        "IMAGE": ContentNodeType.IMAGE,
        "FIGURE": ContentNodeType.IMAGE,
        "EQUATION": ContentNodeType.DISPLAY_EQUATION,
        "MATH": ContentNodeType.DISPLAY_EQUATION,
        "LIST": ContentNodeType.LIST,
        "CODE": ContentNodeType.CODE,
        "COMPOSITE": ContentNodeType.COMPOSITE_BLOCK
    }

    @classmethod
    def build(cls, layout_collection: LayoutBlockCollection) -> List[ASTNode]:
        if not layout_collection.blocks:
            return []

        # 1. Proyección DTO: Mapeo de Layout crudo a Nodos Lógicos
        raw_nodes = [
            cls._map_physical_to_logical(block, idx) 
            for idx, block in enumerate(layout_collection.blocks)
        ]

        # 2. Sutura Trans-página: Unión de bloques perimetrales fracturados
        merged_nodes = CrossPageNormalizer.execute(raw_nodes)

        # 3. Gobernanza y Topología Pura O(n)
        return cls._apply_topology_and_policies(merged_nodes)

    @classmethod
    def _map_physical_to_logical(cls, block: LayoutBlockDraft, index: int) -> ASTNode:
        """Aísla atributos físicos y garantiza trazabilidad inmutable hacia Fase 16.1."""
        raw_type = str(block.logical_type).upper() if block.logical_type else "PARAGRAPH"
        semantic_type = cls._TYPE_MAPPING.get(raw_type)
        
        if not semantic_type:
            logger.warning(f"[AST-004] [UNMAPPED_LAYOUT_TYPE] Layout emitió un tipo '{raw_type}'. Degradando a PARAGRAPH.")
            semantic_type = ContentNodeType.PARAGRAPH

        # SOTA: Conserva el semantic_origin emitido por la fase de extracción
        metadata = NodeMetadata(
            bboxes=[block.bbox],
            pages=[block.page_index],
            confidence=block.confidence,
            provider_native_id=block.provider_native_id,
            layout_reading_order=index,
            semantic_origin=getattr(block, 'semantic_origin', SemanticOrigin.PDF_TEXT)
        )

        explicit_payload = PayloadRegistry.create(
            node_type=semantic_type, 
            raw_data=block.content,
            heading_level=cls._map_native_level(getattr(block, 'level', 0))
        )

        return ASTNode(
            node_id=str(block.block_id) if block.block_id else f"ast_node_{index}",
            sequence_id=index + 1,
            node_type=semantic_type,
            payload=explicit_payload,
            metadata=metadata
        )

    @staticmethod
    def _map_native_level(raw_level: int) -> HeadingLevel:
        """Transformación pura del nivel jerárquico nativo sin depender de Markdown."""
        mapping = {1: HeadingLevel.H1, 2: HeadingLevel.H2, 3: HeadingLevel.H3}
        return mapping.get(raw_level, HeadingLevel.UNKNOWN)

    @classmethod
    def _apply_topology_and_policies(cls, nodes: List[ASTNode]) -> List[ASTNode]:
        """SOTA: Stack Topológico O(n). Calcula el nivel real de anidamiento sin 
        generar un árbol multidimensional, facilitando el chunking posterior."""
        
        final_nodes: List[ASTNode] = []
        # Pila para el trackeo de contexto semántico: List[int] representando niveles activos
        heading_stack: List[int] = [] 

        for idx, node in enumerate(nodes):
            target_strategy = resolve_strategy(node.node_type)
            
            if node.node_type == ContentNodeType.HEADING:
                level_val = 0
                if hasattr(node.payload, 'heading_level'):
                    level_mapping = {HeadingLevel.H1: 1, HeadingLevel.H2: 2, HeadingLevel.H3: 3}
                    level_val = level_mapping.get(node.payload.heading_level, 0) # type: ignore
                
                if level_val > 0:
                    # Desapilar hasta encontrar el ancestro correcto (ej: subir de H3 a H1)
                    while heading_stack and heading_stack[-1] >= level_val:
                        heading_stack.pop()
                    heading_stack.append(level_val)

            # La profundidad es matemáticamente igual a la longitud de la pila activa
            node_depth = len(heading_stack)

            final_nodes.append(node.model_copy(update={
                "sequence_id": idx + 1,
                "strategy": target_strategy,
                "depth": node_depth
            }))

        return final_nodes