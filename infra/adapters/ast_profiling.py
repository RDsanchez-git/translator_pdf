# infra/adapters/ast_profiling.py
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.document_profile.extractors import NodeGeometry
from collections.abc import Sequence
from core.document_profile.ports import ProfileSamplingPolicy

class _NodeGeometryDTO:
    """Implementación inmutable del puerto NodeGeometry."""
    __slots__ = ("_center_x", "_relative_center_x", "_page_number")
    
    def __init__(self, center_x: float, relative_center_x: float, page_number: int):
        self._center_x = center_x
        self._relative_center_x = relative_center_x
        self._page_number = page_number

    @property
    def center_x(self) -> float:
        return self._center_x

    @property
    def relative_center_x(self) -> float:
        return self._relative_center_x

    @property
    def page_number(self) -> int:
        return self._page_number

class NodeGeometryAdapter:
    """Adaptador de infraestructura: Extrae métricas espaciales blindando al dominio del AST."""
    
    # Ancho estándar de fallback (Carta/A4) para evitar ZeroDivisionError 
    # si el AST no posee metadata de dimensiones de página.
    _FALLBACK_PAGE_WIDTH = 612.0 
    
    def extract(self, node: ASTNode) -> NodeGeometry | None:
        metadata = getattr(node, "metadata", None)
        if not metadata:
            return None

        bboxes = getattr(metadata, "bboxes", None)
        if not bboxes or len(bboxes) == 0:
            return None

        primary_bbox = bboxes[0]
        
        center_x = getattr(primary_bbox, "center_x", None)
        if center_x is None:
            x0 = getattr(primary_bbox, "x0", None)
            x1 = getattr(primary_bbox, "x1", None)
            if x0 is None or x1 is None:
                return None
            center_x = (x0 + x1) / 2.0

        page_width = getattr(metadata, "page_width", self._FALLBACK_PAGE_WIDTH)
        if not page_width or page_width <= 0:
            page_width = self._FALLBACK_PAGE_WIDTH

        # SOTA FIX: Extracción del número de página con fallback a 0
        page_num = getattr(metadata, "page_number", 0)

        return _NodeGeometryDTO(
            center_x=center_x,
            relative_center_x=center_x / page_width,
            page_number=page_num
        )
class NodeSemanticAdapter:
    """Adaptador de infraestructura: Traduce la tipología del AST al dominio."""
    
    def kind(self, node: ASTNode) -> ContentNodeType | None:
        node_type = getattr(node, "node_type", None)
        if isinstance(node_type, ContentNodeType):
            return node_type
            
        # Fallback si el AST guarda el enum como string crudo
        if isinstance(node_type, str):
            try:
                return ContentNodeType(node_type)
            except ValueError:
                return None
                
        return None



class FirstPagesSamplingPolicy:
    """SOTA: Estrategia de Bounded Workload inyectable y configurable."""
    __slots__ = ("_geom_extractor", "_max_pages")

    def __init__(self, geom_extractor: 'NodeGeometryAdapter', max_pages: int):
        self._geom_extractor = geom_extractor
        self._max_pages = max_pages

    def sample(self, nodes: Sequence[ASTNode]) -> Sequence[ASTNode]:
        sampled = []
        seen_pages = set()

        for node in nodes:
            geom = self._geom_extractor.extract(node)
            page_num = geom.page_number if geom else 0 
            
            if page_num not in seen_pages:
                if len(seen_pages) >= self._max_pages:
                    break
                seen_pages.add(page_num)
                
            sampled.append(node)

        return sampled

# Conformidad estructural implícita
_ : ProfileSamplingPolicy = FirstPagesSamplingPolicy(None, 0) # type: ignore