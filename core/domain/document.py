from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, model_validator, ConfigDict
from functools import cached_property

# =====================================================================
# 1. ENUMS DEL SISTEMA
# =====================================================================

class LayoutBlockType(str, Enum):
    TITLE = "TITLE"
    AUTHOR = "AUTHOR"
    ABSTRACT = "ABSTRACT"
    SECTION = "SECTION"
    SUBSECTION = "SUBSECTION"
    PARAGRAPH = "PARAGRAPH"
    DISPLAY_EQUATION = "DISPLAY_EQUATION"
    INLINE_EQUATION = "INLINE_EQUATION"
    TABLE_SIMPLE = "TABLE_SIMPLE"
    TABLE_COMPLEX = "TABLE_COMPLEX"
    IMAGE = "IMAGE"
    CAPTION = "CAPTION"
    LIST_ITEM = "LIST_ITEM"
    CODE_BLOCK = "CODE_BLOCK"
    FOOTNOTE = "FOOTNOTE"
    REFERENCE_ENTRY = "REFERENCE_ENTRY"
    HEADER = "HEADER"
    PAGE_NUMBER = "PAGE_NUMBER"
    UNKNOWN = "UNKNOWN"

class DocumentType(str, Enum):
    PAPER = "PAPER"
    BOOK = "BOOK"
    REPORT = "REPORT"

class PageOrientation(str, Enum):
    PORTRAIT = "PORTRAIT"
    LANDSCAPE = "LANDSCAPE"

class OriginType(str, Enum):
    EXTRACTOR = "EXTRACTOR"
    SEGMENTER = "SEGMENTER"
    HEALING = "HEALING"

# =====================================================================
# 2. VALUE OBJECTS
# =====================================================================

class BlockId(BaseModel):
    model_config = ConfigDict(frozen=True)
    value: str

class RawContent(BaseModel):
    model_config = ConfigDict(frozen=True)
    original: str
    normalized: str
    cleaned: str

class BoundingBox(BaseModel):
    model_config = ConfigDict(frozen=True)
    x0: float
    y0: float
    x1: float
    y1: float
    is_normalized: bool = False

    @model_validator(mode="after")
    def validate_bounds(self) -> "BoundingBox":
        if self.x0 >= self.x1 or self.y0 >= self.y1:
            raise ValueError(f"Invariante Geométrica Rota: [{self.x0}, {self.y0}, {self.x1}, {self.y1}]")
        return self

    @property
    def center_x(self) -> float:
        """Retorna el centroide horizontal del bloque."""
        return (self.x0 + self.x1) / 2.0

    @property
    def width(self) -> float:
        """Retorna el ancho relativo del bloque."""
        return max(0.0, self.x1 - self.x0)

    @property
    def height(self) -> float:
        """Retorna la altura relativa del bloque."""
        return max(0.0, self.y1 - self.y0)

# =====================================================================
# 3. METADATOS SEGREGADOS (Anti-Agujero Negro)
# =====================================================================

class TypographyMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    is_bold: bool = False
    is_italic: bool = False

class SpatialMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    reading_order: int = Field(-1, description="Índice de lectura visual")
    column_index: int = Field(0, description="0 = Unica/Izquierda, 1 = Derecha")
    rotation: float = 0.0

class ConfidenceMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    ocr: float = Field(1.0, ge=0.0, le=1.0)
    layout_classification: float = Field(1.0, ge=0.0, le=1.0)

class ProviderMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    provider_name: str
    native_block_index: int

class LayoutMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    typography: Optional[TypographyMetadata] = None
    spatial: Optional[SpatialMetadata] = None
    confidence: Optional[ConfidenceMetadata] = None
    provider: Optional[ProviderMetadata] = None

# =====================================================================
# 4. ENTIDADES DEL DOMINIO
# =====================================================================

class BlockRelationships(BaseModel):
    model_config = ConfigDict(frozen=True)
    parent_id: Optional[BlockId] = None
    children: List[BlockId] = Field(default_factory=list)
    anchors: List[BlockId] = Field(default_factory=list)

class DomainVersion(BaseModel):
    model_config = ConfigDict(frozen=True)
    version: int = Field(1, ge=1)
    origin: OriginType

class LayoutBlock(BaseModel):
    """Representación atómica tridimensional de un bloque."""
    model_config = ConfigDict(frozen=True)
    block_id: BlockId
    logical_type: LayoutBlockType
    content: RawContent
    bbox: Optional[BoundingBox] = None
    metadata: LayoutMetadata
    relationships: BlockRelationships
    versioning: DomainVersion

    @property
    def is_structural(self) -> bool:
        return self.logical_type in (LayoutBlockType.TITLE, LayoutBlockType.SECTION, LayoutBlockType.HEADER)

class PageDimensions(BaseModel):
    model_config = ConfigDict(frozen=True)
    width: float
    height: float
    orientation: PageOrientation

class LayoutPage(BaseModel):
    """Contenedor físico espacial. Permite mix de orientaciones en un documento."""
    model_config = ConfigDict(frozen=True)
    page_number: int = Field(..., ge=1)
    dimensions: PageDimensions
    blocks: List[LayoutBlock] = Field(default_factory=list)

# =====================================================================
# 5. AGGREGATE ROOT
# =====================================================================

class DocumentProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    document_type: DocumentType = DocumentType.PAPER
    primary_language: str = "en"

class DocumentLayout(BaseModel):
    """Aggregate Root: Grafo documental paginado."""
    model_config = ConfigDict(frozen=True, ignored_types=(cached_property,))
    source_path: str
    total_pages: int = Field(..., ge=1)
    profile: DocumentProfile
    pages: List[LayoutPage] = Field(default_factory=list)

    @cached_property
    def _block_index(self) -> Dict[str, LayoutBlock]:
        """Búsqueda O(1) global a través de todas las páginas."""
        return {b.block_id.value: b for page in self.pages for b in page.blocks}

    def get_block(self, block_id: str) -> Optional[LayoutBlock]:
        return self._block_index.get(block_id)

    def get_page(self, page_number: int) -> Optional[LayoutPage]:
        """Resolución O(1) por índice de lista."""
        if 1 <= page_number <= len(self.pages):
            return self.pages[page_number - 1]
        return None

    def with_profile(self, new_profile: "DocumentProfile") -> "DocumentLayout":
        """
        SOTA: Encapsula la mutación inmutable del Aggregate Root.
        Protege invariantes y centraliza la lógica de actualización estructural.
        """
        # Aquí en el futuro se pueden añadir incrementos de versión o audit trails
        return self.model_copy(update={"profile": new_profile})