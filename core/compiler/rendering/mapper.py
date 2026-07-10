from typing import Protocol, List, Optional
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.compiler.rendering.models import RenderUnit, RenderGeometry, AssetReference

class GeometryExtractorProtocol(Protocol):
    def extract(self, node: ASTNode) -> Optional[RenderGeometry]: ...

class AssetExtractorProtocol(Protocol):
    def extract(self, node: ASTNode) -> Optional[AssetReference]: ...

class RenderUnitMapper(Protocol):
    def map_to_unit(self, nodes: List[ASTNode], final_text: str) -> RenderUnit: ...

class DefaultRenderUnitMapper(RenderUnitMapper):
    _TYPE_PRIORITY = {
        ContentNodeType.IMAGE: 100,
        ContentNodeType.TABLE_COMPLEX: 90,
        ContentNodeType.TABLE_SIMPLE: 80,
        ContentNodeType.DISPLAY_EQUATION: 70,
        ContentNodeType.CODE: 60,
        ContentNodeType.HEADING: 50,
        ContentNodeType.LIST: 40,
        ContentNodeType.CAPTION: 30,
        ContentNodeType.PARAGRAPH: 20,
        ContentNodeType.INLINE_EQUATION: 10,
    }

    def __init__(self, geom_extractor: GeometryExtractorProtocol, asset_extractor: AssetExtractorProtocol):
        self._geom_extractor = geom_extractor
        self._asset_extractor = asset_extractor

    def _resolve_primary_type(self, nodes: List[ASTNode]) -> ContentNodeType:
        if not nodes:
            return ContentNodeType.PARAGRAPH
        return max(nodes, key=lambda n: self._TYPE_PRIORITY.get(n.node_type, 0)).node_type

    def map_to_unit(self, nodes: List[ASTNode], final_text: str) -> RenderUnit:
        if not nodes:
            raise ValueError("No se puede mapear una lista de nodos vacía a un RenderUnit.")

        primary_type = self._resolve_primary_type(nodes)
        
        # TODO: Cálculo de envolvente espacial (Hull Bounding Box) para chunks 1:N.
        # Actualmente se utiliza el nodo de mayor prioridad semántica como proxy topológico.
        # En iteraciones futuras (ej. perfiles IEEE/Springer), unificar las geometrías relativas 
        # para evitar solapamientos si el chunk abarca media página.
        primary_node = next((n for n in nodes if n.node_type == primary_type), nodes[0])

        return RenderUnit(
            node_id=primary_node.node_id,
            node_type=primary_type,
            content=final_text,
            geometry=self._geom_extractor.extract(primary_node),
            asset=self._asset_extractor.extract(primary_node)
        )