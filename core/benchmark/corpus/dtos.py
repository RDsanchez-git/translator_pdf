from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RawDocumentEntryDTO(BaseModel):
    document_id: str
    sha256: str
    traits: List[str]
    page_count: int
    ground_truth_version: Optional[str] = None
    ground_truth_sha256: Optional[str] = None
    # DF-13: estado del ciclo de vida del Ground Truth. Raw string (no enum)
    # para evitar dependencia cruzada corpus→ground_truth. Default None;
    # la capa de consumo interpreta None como DRAFT (migración).
    ground_truth_state: Optional[str] = None
    # Gate 4 (Wave 4.2): identidad semántica del oráculo ($H_{semantic}$).
    # Hash SHA-256 determinista del contenido semántico del oráculo.
    # None si el documento no tiene oráculo sellado.
    oracle_hash: Optional[str] = None
    model_config = ConfigDict(frozen=True)


class RawCorpusManifestDTO(BaseModel):
    corpus_version: str
    manifest_hash: str
    documents: List[RawDocumentEntryDTO]
    model_config = ConfigDict(frozen=True)


class BootstrapCorpusResult(BaseModel):
    manifest_hash: str
    documents_processed: int
    total_pages_indexed: int
    model_config = ConfigDict(frozen=True)