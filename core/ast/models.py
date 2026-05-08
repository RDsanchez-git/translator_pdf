from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any

class NodeType(str, Enum):
    SECTION = "section"
    PARAGRAPH = "paragraph"
    EQUATION = "equation"
    TABLE = "table"
    CAPTION = "caption"
    IMAGE = "image"
    LIST = "list"
    FOOTNOTE = "footnote"
    CITATION = "citation"
    TOC = "toc"
    MACRO_CHUNK = "macro_chunk" 
    UNKNOWN = "unknown"

class ASTNode(BaseModel):
    node_id: str
    type: NodeType
    content: str
    latex: str | None = None  
    status: str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)