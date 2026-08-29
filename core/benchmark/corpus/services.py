from typing import Dict, List, Optional

from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusVersion,
    DocumentFingerprint,
)


class ManifestFingerprintCalculator:
    """Servicio de dominio encargado del cálculo determinista de la firma global del manifiesto.

    JUSTIFICACIÓN DE ground_truth_state EN EL HASH (NADR-F17BIS-16 §5.3 R10, DC-03 resuelto):
    La inclusión de ground_truth_state en el payload del hash es correcta y necesaria porque:

    1. PREVIENE DES-SELLADO SILENCIOSO: Si un oráculo sellado pudiera ser "des-sellado"
       (transicionado de SEALED a DRAFT) sin alterar el manifest_hash, la integridad
       del proceso de certificación quedaría comprometida. Al incluir el estado en el
       hash, cualquier cambio de estado invalida la firma global.

    2. PROTEGE LA INTEGRIDAD DEL PROCESO DE CERTIFICACIÓN: El estado de ciclo de vida
       no es identidad científica del contenido (eso lo captura oracle_hash), sino
       identidad del proceso de certificación. Un oráculo con el mismo contenido pero
       diferente estado (DRAFT vs SEALED) representa diferentes niveles de confianza
       y validación.

    3. INVALIDA EL SELLO ANTE CAMBIOS DE ESTADO: Cualquier transición de estado
       (VALIDATED → SEALED, o SEALED → DRAFT) altera el manifest_hash, forzando
       re-certificación. Esto garantiza que la baseline solo puede estar en estado
       SEALED si todas las dimensiones (incluyendo el estado) son consistentes.

    SEMÁNTICA (NADR-F17BIS-16 §5.3 R9-R12):
    - ground_truth_state es ESTADO OPERACIONAL del ciclo de vida, no identidad
      científica del contenido.
    - oracle_hash es IDENTIDAD CIENTÍFICA del contenido del oráculo.
    - Ambos son dimensiones ortogonales que participan en la identidad global de
      la baseline, pero con semánticas distintas.

    DF-19 (Migración de formato de hash): Wave 4.2 actualizó el formato del
    payload para incluir las nuevas dimensiones de identidad (oracle_hash y
    ground_truth_state). El formato anterior era:
        {doc_id}:{fingerprint_sha256}:{traits}:{page_count}
    El formato actual es:
        {doc_id}:{fingerprint_sha256}:{traits}:{page_count}:{oracle_hash}:{ground_truth_state}

    Este cambio rompe la compatibilidad de hashes con manifiestos sellados
    bajo el formato anterior. Los manifiestos existentes deben re-sellarse
    con el formato nuevo para garantizar la integridad criptográfica de
    todas las dimensiones de identidad (NADR-15 §5.3 R9).
    """

    @staticmethod
    def compute_hash(version: CorpusVersion, documents: List[CorpusDocumentMetadata]) -> str:
        from core.shared.crypto import compute_sha256

        parts = [version.value.encode("utf-8")]
        sorted_documents = sorted(documents, key=lambda doc: doc.document_id)
        for doc in sorted_documents:
            sorted_traits = sorted([trait.value for trait in doc.traits])
            traits_str = ",".join(sorted_traits)

            oracle_hash_str = doc.oracle_hash if doc.oracle_hash is not None else "none"
            gt_state_str = doc.ground_truth_state if doc.ground_truth_state is not None else "none"

            document_payload = (
                f"{doc.document_id}:"
                f"{doc.fingerprint.sha256}:"
                f"{traits_str}:"
                f"{doc.page_count}:"
                f"{oracle_hash_str}:"
                f"{gt_state_str}"
            )
            parts.append(document_payload.encode("utf-8"))
        return compute_sha256(b"".join(parts))


class ManifestLineageSealer:
    """Servicio de Dominio del Corpus. Gobierna la política de sellado y actualización de firmas globales.

    Gate 4 (Wave 4.2): recibe oracle_hashes y ground_truth_states como
    Dict[str, str] (strings genéricos) para evitar dependencia cruzada
    corpus→ground_truth (Problema B).

    Matiz 1: para documentos sin oráculo sellado en este ciclo, preserva
    el oracle_hash y ground_truth_state anteriores (no sobrescribe con None).

    DC-08 resuelto (Wave 1.2 Fase 3): Se eliminaron detected_hashes y target_version
    porque ground_truth_version y ground_truth_sha256 eran campos huérfanos que
    no participaban en manifest_hash ni en CorpusDocumentMetadata. YAGNI.
    """

    @staticmethod
    def seal_manifest_with_ground_truth(
        current_manifest: RawCorpusManifestDTO,
        oracle_hashes: Optional[Dict[str, str]] = None,
        ground_truth_states: Optional[Dict[str, str]] = None,
    ) -> RawCorpusManifestDTO:
        """Aplica las firmas del Ground Truth sobre el catálogo y regenera la huella inmutable del manifiesto."""
        if oracle_hashes is None:
            oracle_hashes = {}
        if ground_truth_states is None:
            ground_truth_states = {}

        updated_documents: List[RawDocumentEntryDTO] = []
        domain_documents_for_rehash: List[CorpusDocumentMetadata] = []

        for doc_entry in current_manifest.documents:
            doc_id = doc_entry.document_id

            # Matiz 1: preservar valores anteriores para documentos sin oráculo en este ciclo.
            new_oracle_hash = oracle_hashes.get(doc_id, doc_entry.oracle_hash)
            new_gt_state = ground_truth_states.get(doc_id, doc_entry.ground_truth_state)

            updated_documents.append(
                RawDocumentEntryDTO(
                    document_id=doc_id,
                    sha256=doc_entry.sha256,
                    traits=doc_entry.traits,
                    page_count=doc_entry.page_count,
                    ground_truth_state=new_gt_state,
                    oracle_hash=new_oracle_hash,
                )
            )

            domain_documents_for_rehash.append(
                CorpusDocumentMetadata(
                    document_id=doc_id,
                    fingerprint=DocumentFingerprint(sha256=doc_entry.sha256),
                    traits=frozenset(ExtractionChallengeTrait(t) for t in doc_entry.traits),
                    page_count=doc_entry.page_count,
                    oracle_hash=new_oracle_hash,
                    ground_truth_state=new_gt_state,
                )
            )

        new_manifest_hash = ManifestFingerprintCalculator.compute_hash(
            version=CorpusVersion(value=current_manifest.corpus_version),
            documents=domain_documents_for_rehash,
        )

        return RawCorpusManifestDTO(
            corpus_version=current_manifest.corpus_version,
            manifest_hash=new_manifest_hash,
            documents=updated_documents,
        )