from typing import FrozenSet, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.dataclasses import dataclass

from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.shared.identity_contracts import DocumentId, GroundTruthState


@dataclass(frozen=True, slots=True)
class DocumentFingerprint:
    sha256: str

    def __post_init__(self) -> None:
        """Invariante de dominio: SHA-256 hex lowercase de 64 caracteres.

        SOTA FIX (Wave 2.3): Se elimina el check .islower() que fallaba
        para hashes puramente numéricos (ej: "0"*64). str.islower() retorna
        False cuando no hay caracteres alfabéticos. El check de longitud
        y pertenencia al set hex es suficiente y correcto.
        """
        if len(self.sha256) != 64 or not all(c in "0123456789abcdef" for c in self.sha256):
            raise ValueError(
                "Fallo de invariante: El hash SHA-256 debe tener exactamente "
                "64 caracteres hexadecimales en minúsculas."
            )


@dataclass(frozen=True, slots=True)
class CorpusVersion:
    value: str


class CorpusDocumentMetadata(BaseModel):
    """Modelo de dominio de un documento dentro del corpus canónico.

    CONTRATO DE DOMINIO (NADR-F17BIS-17 §5.1, Waves 2.1/2.4 Fase 3):

    document_id:
        - Identidad lógica del documento dentro del corpus.
        - DOMINIO: cualquier string no vacío que NO contenga el carácter ':'.
        - PROHIBIDO: ':' (delimitador de campo en el framing criptográfico
          de ManifestFingerprintCalculator).
        - JUSTIFICACIÓN: garantizar inyectividad del encoding. Si document_id
          pudiera contener ':', dos payloads distintos podrían producir el
          mismo hash, comprometiendo la identidad criptográfica de la baseline.
        - VALIDACIÓN: fail-fast en construcción vía DocumentId
          (core/shared/identity_contracts.py).
        - SENTINEL: no aplica (document_id es obligatorio).

    fingerprint:
        - H_physical del documento (SHA-256 del archivo PDF).
        - Valida hex lowercase de 64 caracteres en __post_init__.

    oracle_hash:
        - H_semantic del oráculo sellado ($H_{semantic}$).
        - Hash SHA-256 determinista del contenido semántico del oráculo.
        - None si el documento no tiene oráculo sellado.
        - Sentinel en manifest_hash: "none" cuando es None.

    ground_truth_state:
        - Estado OPERACIONAL del ciclo de vida (DF-13).
        - NO es identidad científica del contenido (eso es oracle_hash).
        - DOMINIO: cualquier string no vacío que NO contenga ':', o None.
        - PROHIBIDO: ':' (delimitador del framing criptográfico).
        - VALIDACIÓN: fail-fast en construcción vía GroundTruthState.
        - SENTINEL: None es válido (interpretado como DRAFT por la capa
          de consumo, según DF-13).
        - DF-01 (Wave 2.4): contrato agregado para cierre de asimetría
          defensiva con document_id y node_id.
    """

    document_id: DocumentId
    fingerprint: DocumentFingerprint
    traits: FrozenSet[ExtractionChallengeTrait] = Field(..., min_length=1)
    page_count: int = Field(..., gt=0)
    # Gate 4 (Wave 4.2): dimensiones de identidad adicionales.
    # oracle_hash: identidad semántica del oráculo ($H_{semantic}$).
    # ground_truth_state: estado del ciclo de vida (DF-13).
    # Ambos son strings genéricos (no enums) para evitar dependencia
    # cruzada corpus→ground_truth (Problema B).
    # DF-01 (Wave 2.4): ground_truth_state validado vía GroundTruthState.
    oracle_hash: Optional[str] = None
    ground_truth_state: Optional[GroundTruthState] = None
    model_config = ConfigDict(frozen=True)


class CorpusManifest(BaseModel):
    """Aggregate Root Puro. El negocio inmutable del espacio muestral."""
    corpus_version: CorpusVersion
    documents: List[CorpusDocumentMetadata]
    model_config = ConfigDict(frozen=True)