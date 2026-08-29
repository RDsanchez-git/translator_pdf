from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from core.shared.identity_contracts import DocumentId, GroundTruthState


class RawDocumentEntryDTO(BaseModel):
    """DTO de frontera para persistencia del manifiesto en JSON.

    CONTRATO DE DOMINIO (NADR-F17BIS-17 §5.1, Waves 2.1/2.4 Fase 3):

    document_id:
        - DOMINIO: cualquier string no vacío que NO contenga ':'.
        - PROHIBIDO: ':' (delimitador del framing criptográfico).
        - VALIDACIÓN: fail-fast en construcción vía DocumentId.
        - Fail-Fast en la frontera: si un manifiesto JSON externo contiene
          un document_id inválido, el error se detecta al cargar el DTO,
          no después durante el cálculo del hash.

    ground_truth_state:
        - DOMINIO: cualquier string no vacío que NO contenga ':', o None.
        - PROHIBIDO: ':' (delimitador del framing criptográfico).
        - VALIDACIÓN: fail-fast en construcción vía GroundTruthState.
        - SENTINEL: None es válido (interpretado como DRAFT, DF-13).
        - DF-01 (Wave 2.4): contrato agregado para cierre de asimetría
          defensiva con document_id y node_id.
    """

    document_id: DocumentId
    sha256: str
    traits: List[str]
    page_count: int
    # DF-13: estado del ciclo de vida del Ground Truth. Raw string (no enum)
    # para evitar dependencia cruzada corpus→ground_truth. Default None;
    # la capa de consumo interpreta None como DRAFT (migración).
    # DF-01 (Wave 2.4): validación de dominio explícita vía GroundTruthState.
    ground_truth_state: Optional[GroundTruthState] = None
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