from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ASTNode(BaseModel):
    node_id: str
    type: Literal["section", "text_block", "display_equation"]
    content: Optional[str] = None
    latex: Optional[str] = None
    children: List["ASTNode"] = Field(default_factory=list)

    status: Literal["pending", "ok", "fallback_empty", "fallback_suspicious", "error"] = "pending"