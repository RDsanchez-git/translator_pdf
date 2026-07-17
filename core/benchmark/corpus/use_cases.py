import pathlib
from core.benchmark.corpus.ports import CorpusManifestLoaderPort, DocumentMetadataExtractorPort
from core.benchmark.corpus.models import CorpusDocumentMetadata, DocumentFingerprint, CorpusManifest, CorpusVersion
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.services import ManifestFingerprintCalculator
from core.benchmark.corpus.dtos import RawCorpusManifestDTO, RawDocumentEntryDTO, BootstrapCorpusResult

class BootstrapCorpusManifestUseCase:
    """Camino de Escritura/Saneamiento. Ejecuta la reconciliación física contra el hardware (Problema 6)."""
    def __init__(self, loader: CorpusManifestLoaderPort, extractor: DocumentMetadataExtractorPort):
        self._loader = loader
        self._extractor = extractor

    def execute(self, pdf_directory: pathlib.Path) -> BootstrapCorpusResult:
        current_dto = self._loader.load_raw_manifest()
        domain_documents: list[CorpusDocumentMetadata] = []
        total_pages = 0

        for entry in current_dto.documents:
            pdf_path = pdf_directory / f"{entry.document_id}.pdf"
            if not pdf_path.exists():
                raise FileNotFoundError(f"Fallo de consistencia: Binario ausente {pdf_path}")

            # Extracción local delegada al adaptador periférico
            calculated_sha256 = self._extractor.extract_sha256(pdf_path)
            real_page_count = self._extractor.extract_page_count(pdf_path)
            total_pages += real_page_count

            domain_documents.append(
                CorpusDocumentMetadata(
                    document_id=entry.document_id,
                    fingerprint=DocumentFingerprint(sha256=calculated_sha256),
                    traits=frozenset(ExtractionChallengeTrait(t) for t in entry.traits),
                    page_count=real_page_count
                )
            )

        sorted_docs = sorted(domain_documents, key=lambda d: d.document_id)
        manifest = CorpusManifest(corpus_version=CorpusVersion(value=current_dto.corpus_version), documents=sorted_docs)
        manifest_hash = ManifestFingerprintCalculator.compute_hash(manifest.corpus_version, manifest.documents)

        # Volcado de actualización atómica hacia el loader
        self._loader.save_manifest_dto(
            RawCorpusManifestDTO(
                corpus_version=manifest.corpus_version.value,
                manifest_hash=manifest_hash,
                documents=[
                    RawDocumentEntryDTO(
                        document_id=doc.document_id,
                        sha256=doc.fingerprint.sha256,
                        traits=sorted([t.value for t in doc.traits]),
                        page_count=doc.page_count
                    )
                    for doc in sorted_docs
                ]
            )
        )

        return BootstrapCorpusResult(
            manifest_hash=manifest_hash,
            documents_processed=len(sorted_docs),
            total_pages_indexed=total_pages
        )

class LoadCorpusManifestUseCase:
    """Camino de Lectura en Runtime. Solo lectura O(1) RAM para ejecución de campañas masivas (Problema 6)."""
    def __init__(self, loader: CorpusManifestLoaderPort):
        self._loader = loader

    def execute(self) -> CorpusManifest:
        dto = self._loader.load_raw_manifest()
        return CorpusManifest(
            corpus_version=CorpusVersion(value=dto.corpus_version),
            documents=[
                CorpusDocumentMetadata(
                    document_id=entry.document_id,
                    fingerprint=DocumentFingerprint(sha256=entry.sha256),
                    traits=frozenset(ExtractionChallengeTrait(t) for t in entry.traits),
                    page_count=entry.page_count
                )
                for entry in dto.documents
            ]
        )