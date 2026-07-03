from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from core.domain.document import BlockId, BoundingBox

class LayoutBlockDraft(BaseModel):
    """
    SOTA: Único DTO de transición para el ciclo de vida de la Fase 16.1.
    Absorbe la evolución espacial e identitaria del bloque sin mutar estados.
    """
    model_config = ConfigDict(frozen=True)
    
    block_id: Optional[BlockId] = None
    logical_type: Optional[str] = None
    content: str
    bbox: BoundingBox
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    provider_native_id: Optional[str] = None
    merge_history: List[str] = Field(default_factory=list)

    column_index: Optional[int] = None
    
class LayoutBlockCollection(BaseModel):
    """Contenedor tipado inmutable para el transporte seguro entre capas."""
    model_config = ConfigDict(frozen=True)
    blocks: List[LayoutBlockDraft]