from typing import FrozenSet, List
from pydantic import BaseModel, ConfigDict, Field
from pydantic.dataclasses import dataclass
from core.benchmark.corpus.enums import ExtractionChallengeTrait

@dataclass(frozen=True, slots=True)
class DocumentFingerprint:
    sha256: str

    def __post_init__(self) -> None:
        if not self.sha256.islower() or not all(c in "0123456789abcdef" for c in self.sha256):
            raise ValueError("Fallo de invariante: El hash SHA-256 debe ser hexadecimal en minúsculas.")

@dataclass(frozen=True, slots=True)
class CorpusVersion:
    value: str

class CorpusDocumentMetadata(BaseModel):
    document_id: str = Field(..., min_length=1)
    fingerprint: DocumentFingerprint
    traits: FrozenSet[ExtractionChallengeTrait] = Field(..., min_length=1)
    page_count: int = Field(..., gt=0)
    model_config = ConfigDict(frozen=True)

class CorpusManifest(BaseModel):
    """Aggregate Root Puro. El negocio inmutable del espacio muestral."""
    corpus_version: CorpusVersion
    documents: List[CorpusDocumentMetadata]
    model_config = ConfigDict(frozen=True)