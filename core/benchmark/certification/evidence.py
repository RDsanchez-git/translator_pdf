"""Certification Evidence (NADR-24 SS5.7 R29-R31, Wave 4.3 Task 4.3.3).

Functional Core: ensamblaje puro, consistencia cruzada y serializacion
determinista. NO calcula hashes desde disco: las identidades llegan ya
computadas por el Imperative Shell con los calculadores existentes
(ManifestFingerprintCalculator, ConfigurationFingerprintCalculator,
ParameterIdentityCalculator, compute_sha256).

Mapeo de identidades (interpretacion normativa GF-02, ver crosswalk en
FASE_5_WAVE_4_3_EVIDENCE_RECORD.md):
  corpus_identity   := compuesto de la capa de contenido (SHA-256 ordenados
                       de los documentos; NADR-20 SS5.1-SS5.5). Estable entre sellados.
  manifest_identity := manifest_hash (NADR-20 SS5.6 R24/R26). Incluye oracle_hash
                       y ground_truth_state; cambia con el sellado.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from core.shared.crypto import compute_sha256


def compute_corpus_content_identity(document_sha256: tuple[str, ...]) -> str:
    """Identidad compuesta de la capa de contenido (NADR-20 SS5.1-SS5.5).

    Insensible al orden (sorted previo), agnostica a filenames y rutas (R2).
    """
    if not document_sha256:
        raise ValueError(
            "corpus content identity requiere al menos un documento (NADR-20 R1)"
        )
    payload = "|".join(sorted(document_sha256))
    return compute_sha256(payload.encode("utf-8"))


@dataclass(frozen=True)
class DocumentResultEvidence:
    """Veredicto individual por documento (R29: per-document results)."""

    document_id: str
    verdict: str
    nss_score: float


@dataclass(frozen=True)
class CertificationEvidence:
    """Siete elementos minimos de R29 + extras de trazabilidad (R31)."""

    corpus_identity: str
    manifest_identity: str
    configuration_identity: str
    frozen_parameters_identity: str
    evaluation_provenance_reference: str
    per_document_results: tuple[DocumentResultEvidence, ...]
    aggregate_result: str
    evaluation_kind: str
    result_identity: str

    def to_mapping(self) -> dict[str, object]:
        return {
            "corpus_identity": self.corpus_identity,
            "manifest_identity": self.manifest_identity,
            "configuration_identity": self.configuration_identity,
            "frozen_parameters_identity": self.frozen_parameters_identity,
            "evaluation_provenance_reference": self.evaluation_provenance_reference,
            "per_document_results": [
                {
                    "document_id": d.document_id,
                    "verdict": d.verdict,
                    "nss_score": d.nss_score,
                }
                for d in self.per_document_results
            ],
            "aggregate_result": self.aggregate_result,
            "evaluation_kind": self.evaluation_kind,
            "result_identity": self.result_identity,
        }


def serialize_evidence(evidence: CertificationEvidence) -> str:
    """Serializacion determinista (R31: auditable sin re-ejecucion)."""
    return json.dumps(
        evidence.to_mapping(), indent=2, ensure_ascii=False, sort_keys=True
    )
