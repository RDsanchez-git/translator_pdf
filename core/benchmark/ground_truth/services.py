from typing import List, Dict
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO
from core.benchmark.corpus.models import CorpusVersion, CorpusDocumentMetadata, DocumentFingerprint
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.services import ManifestFingerprintCalculator

class ManifestGroundTruthUpdater:
    """Domain Service encargado de la política de actualización de linaje y recálculo de firmas globales."""
    
    @staticmethod
    def apply_lineage_sealing(
        current_manifest: RawCorpusManifestDTO,
        detected_hashes: Dict[str, str],
        target_version: str
    ) -> RawCorpusManifestDTO:
        """Aplica las firmas detectadas sobre el manifiesto y genera la nueva huella criptográfica canónica."""
        updated_documents: List[RawDocumentEntryDTO] = []
        domain_documents_for_rehash: List[CorpusDocumentMetadata] = []

        for doc_entry in current_manifest.documents:
            doc_id = doc_entry.document_id
            gt_version = doc_entry.ground_truth_version
            gt_hash = doc_entry.ground_truth_sha256

            # Aplicación de la política analítica de linaje
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

        # Delegación del cálculo de la huella digital global del agregado
        new_manifest_hash = ManifestFingerprintCalculator.compute_hash(
            version=CorpusVersion(value=current_manifest.corpus_version),
            documents=domain_documents_for_rehash
        )

        return RawCorpusManifestDTO(
            corpus_version=current_manifest.corpus_version,
            manifest_hash=new_manifest_hash,
            documents=updated_documents
        )