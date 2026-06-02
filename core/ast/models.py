from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union

# =====================================================================
# FAMILIA 1: NODOS ESTRUCTURALES (Contenedores lógicos / Layout)
# =====================================================================
class StructuralNodeType(str, Enum):
    DOCUMENT = "document"
    PART = "part"
    CHAPTER = "chapter"
    SECTION = "section"
    SUBSECTION = "subsection"

# =====================================================================
# FAMILIA 2: NODOS SEMÁNTICOS (Payloads de contenido / Traducibles)
# =====================================================================
class ContentNodeType(str, Enum):
    # Texto
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    
    # STEM
    EQUATION = "equation"
    INLINE_EQUATION = "inline_equation"
    TABLE = "table"
    FIGURE = "figure"
    IMAGE = "image"
    CAPTION = "caption"
    ALGORITHM = "algorithm"
    CODE_BLOCK = "code_block"
    
    # Académico
    FOOTNOTE = "footnote"
    CITATION = "citation"
    REFERENCE_ENTRY = "reference_entry"
    BIBLIOGRAPHY = "bibliography"
    APPENDIX = "appendix"
    
    # Recuperación (SOTA Fallbacks)
    MACRO_CHUNK = "macro_chunk"
    COMPOSITE_BLOCK = "composite_block"
    UNKNOWN = "unknown"

# Tipo compuesto para flexibilidad en tipado estático
NodeType = Union[StructuralNodeType, ContentNodeType]

class ASTNode(BaseModel):
    node_id: str
    type: NodeType
    content: Optional[str] = None  # SOTA: Nodos estructurales puros pueden no tener string crudo
    latex: Optional[str] = None
    status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parent_id: Optional[str] = None # SOTA: Habilitador de árbol jerárquico (DOM)