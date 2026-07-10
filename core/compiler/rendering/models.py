from dataclasses import dataclass
from typing import Optional
from core.ast.models import ContentNodeType

@dataclass(frozen=True, slots=True)
class RenderingConfiguration:
    """ACL: Configuración de renderizado purgada de semántica heurística."""
    is_multi_column: bool
    float_span_threshold: float = 0.6  # Configurable por publisher futuro

@dataclass(frozen=True, slots=True)
class RenderGeometry:
    """Geometría universal abstracta. El Mapper ya resolvió el parser subyacente."""
    relative_x: float
    relative_y: float
    relative_width: float
    relative_height: float
    page_number: int

@dataclass(frozen=True, slots=True)
class AssetReference:
    """Value Object para referencias de medios y anclajes."""
    path: str
    alt_text: Optional[str] = None
    label: Optional[str] = None
    mime_type: str = "image/png"

@dataclass(frozen=True, slots=True)
class RenderUnit:
    """DTO puro de frontera."""
    node_id: str
    node_type: ContentNodeType
    content: str
    geometry: Optional[RenderGeometry] = None
    asset: Optional[AssetReference] = None