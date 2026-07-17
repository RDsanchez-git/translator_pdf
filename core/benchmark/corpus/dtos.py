from typing import List
from pydantic import BaseModel, ConfigDict

class RawDocumentEntryDTO(BaseModel):
    document_id: str
    sha256: str
    traits: List[str]
    page_count: int
    model_config = ConfigDict(frozen=True)

class RawCorpusManifestDTO(BaseModel):
    corpus_version: str
    manifest_hash: str
    documents: List[RawDocumentEntryDTO]
    model_config = ConfigDict(frozen=True)

class BootstrapCorpusResult(BaseModel):
    """DTO Rico de salida para control operacional en la capa de aplicación (Problema 4)."""
    manifest_hash: str
    documents_processed: int
    total_pages_indexed: int
    model_config = ConfigDict(frozen=True)