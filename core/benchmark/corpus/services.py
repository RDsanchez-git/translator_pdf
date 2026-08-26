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
            # Ordenamiento alfabético estricto de los rasgos (traits) de cada documento
            sorted_traits = sorted([trait.value for trait in doc.traits])
            traits_str = ",".join(sorted_traits)

            # Gate 4 (Wave 4.2): payload extendido con oracle_hash y ground_truth_state.
            # 'none' como sentinel para valores ausentes (determinista, sin ambigüedad).
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
    corpus→ground_truth (Problema B). El bounded context ground_truth
    (SealGroundTruthUseCase) pasa los valores como strings.

    Matiz 1: para documentos sin oráculo sellado en este ciclo, preserva
    el oracle_hash y ground_truth_state anteriores (no sobrescribe con None).

    Nota de compatibilidad: oracle_hashes y ground_truth_states son opcionales
    para mantener compatibilidad con SealGroundTruthUseCase de Wave 3.2.
    Wave 4.3 actualizará SealGroundTruthUseCase para pasar estos parámetros
    explícitamente, cerrando la ventana de inconsistencia.
    """

    @staticmethod
    def seal_manifest_with_ground_truth(
        current_manifest: RawCorpusManifestDTO,
        detected_hashes: Dict[str, str],
        target_version: str,
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
            gt_version = doc_entry.ground_truth_version
            gt_hash = doc_entry.ground_truth_sha256

            # Aplicación de la regla de negocio: si existe una muestra curada en disco, se asimila el linaje
            if doc_id in detected_hashes:
                gt_version = target_version
                gt_hash = detected_hashes[doc_id]

            # Gate 4 (Wave 4.2): propagar oracle_hash y ground_truth_state.
            # Matiz 1: preservar valores anteriores para documentos sin oráculo en este ciclo.
            new_oracle_hash = oracle_hashes.get(doc_id, doc_entry.oracle_hash)
            new_gt_state = ground_truth_states.get(doc_id, doc_entry.ground_truth_state)

            updated_documents.append(
                RawDocumentEntryDTO(
                    document_id=doc_id,
                    sha256=doc_entry.sha256,
                    traits=doc_entry.traits,
                    page_count=doc_entry.page_count,
                    ground_truth_version=gt_version,
                    ground_truth_sha256=gt_hash,
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

        # Invocación local y directa al calculador de huella digital
        new_manifest_hash = ManifestFingerprintCalculator.compute_hash(
            version=CorpusVersion(value=current_manifest.corpus_version),
            documents=domain_documents_for_rehash,
        )

        return RawCorpusManifestDTO(
            corpus_version=current_manifest.corpus_version,
            manifest_hash=new_manifest_hash,
            documents=updated_documents,
        )