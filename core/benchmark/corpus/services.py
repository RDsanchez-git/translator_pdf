from typing import Dict, List
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from core.benchmark.corpus.models import CorpusVersion, CorpusDocumentMetadata, DocumentFingerprint
from core.benchmark.corpus.enums import ExtractionChallengeTrait


class ManifestFingerprintCalculator:
    """Servicio de dominio encargado del cálculo determinista de la firma global del manifiesto."""

    @staticmethod
    def compute_hash(version: CorpusVersion, documents: List[CorpusDocumentMetadata]) -> str:
        from core.shared.crypto import compute_sha256
        parts = [version.value.encode("utf-8")]
        sorted_documents = sorted(documents, key=lambda doc: doc.document_id)
        for doc in sorted_documents:
            # Ordenamiento alfabético estricto de los rasgos (traits) de cada documento
            sorted_traits = sorted([trait.value for trait in doc.traits])
            traits_str = ",".join(sorted_traits)
            document_payload = f"{doc.document_id}:{doc.fingerprint.sha256}:{traits_str}:{doc.page_count}"
            parts.append(document_payload.encode("utf-8"))
        return compute_sha256(b"".join(parts))


class ManifestLineageSealer:
    """Servicio de Dominio del Corpus. Gobierna la política de sellado y actualización de firmas globales."""
    
    @staticmethod
    def seal_manifest_with_ground_truth(
        current_manifest: RawCorpusManifestDTO,
        detected_hashes: Dict[str, str],
        target_version: str
    ) -> RawCorpusManifestDTO:
        """Aplica las firmas del Ground Truth sobre el catálogo y regenera la huella inmutable del manifiesto."""
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

            updated_documents.append(
                RawDocumentEntryDTO(
                    document_id=doc_id,
                    sha256=doc_entry.sha256,
                    traits=doc_entry.traits,
                    page_count=doc_entry.page_count,
                    ground_truth_version=gt_version,
                    ground_truth_sha256=gt_hash
                )
            )

            domain_documents_for_rehash.append(
                CorpusDocumentMetadata(
                    document_id=doc_id,
                    fingerprint=DocumentFingerprint(sha256=doc_entry.sha256),
                    traits=frozenset(ExtractionChallengeTrait(t) for t in doc_entry.traits),
                    page_count=doc_entry.page_count
                )
            )

        # Invocación local y directa al calculador de huella digital
        new_manifest_hash = ManifestFingerprintCalculator.compute_hash(
            version=CorpusVersion(value=current_manifest.corpus_version),
            documents=domain_documents_for_rehash
        )

        return RawCorpusManifestDTO(
            corpus_version=current_manifest.corpus_version,
            manifest_hash=new_manifest_hash,
            documents=updated_documents
        )