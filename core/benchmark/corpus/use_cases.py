import pathlib

from core.benchmark.corpus.dtos import (
    BootstrapCorpusResult,
    RawCorpusManifestDTO,
    RawDocumentEntryDTO,
)
from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.models import (
    CorpusDocumentMetadata,
    CorpusManifest,
    CorpusVersion,
    DocumentFingerprint,
)
from core.benchmark.corpus.ports import (
    CorpusManifestReaderPort,
    CorpusManifestWriterPort,
    DocumentMetadataExtractorPort,
)
from core.benchmark.corpus.services import ManifestFingerprintCalculator


class BootstrapCorpusManifestUseCase:
    """Camino de Escritura/Saneamiento (curaduría, no runtime).

    NADR-14 §5.1 R1: inyecta ambos puertos segregados porque es un caso
    de uso de curaduría. La asimetría prohíbe que el RUNTIME tenga acceso
    de escritura, pero la curaduría puede leer y escribir (observación R1).

    Gate 4 (Wave 4.2): propaga oracle_hash y ground_truth_state desde el DTO
    hacia CorpusDocumentMetadata (Problema E).
    """

    def __init__(
        self,
        reader: CorpusManifestReaderPort,
        writer: CorpusManifestWriterPort,
        extractor: DocumentMetadataExtractorPort,
    ):
        self._reader = reader
        self._writer = writer
        self._extractor = extractor

    def execute(self, pdf_directory: pathlib.Path) -> BootstrapCorpusResult:
        current_dto = self._reader.load_raw_manifest()
        domain_documents: list[CorpusDocumentMetadata] = []
        updated_entries: list[RawDocumentEntryDTO] = []
        total_pages = 0

        for entry in current_dto.documents:
            pdf_path = pdf_directory / f"{entry.document_id}.pdf"
            if not pdf_path.exists():
                raise FileNotFoundError(f"Fallo de consistencia: Binario ausente {pdf_path}")

            calculated_sha256 = self._extractor.extract_sha256(pdf_path)
            real_page_count = self._extractor.extract_page_count(pdf_path)
            total_pages += real_page_count

            domain_documents.append(
                CorpusDocumentMetadata(
                    document_id=entry.document_id,
                    fingerprint=DocumentFingerprint(sha256=calculated_sha256),
                    traits=frozenset(ExtractionChallengeTrait(t) for t in entry.traits),
                    page_count=real_page_count,
                    # Gate 4 (Wave 4.2): propagar dimensiones de identidad
                    oracle_hash=entry.oracle_hash,
                    ground_truth_state=entry.ground_truth_state,
                )
            )

            updated_entries.append(
                RawDocumentEntryDTO(
                    document_id=entry.document_id,
                    sha256=calculated_sha256,
                    traits=entry.traits,
                    page_count=real_page_count,
                    ground_truth_version=entry.ground_truth_version,
                    ground_truth_sha256=entry.ground_truth_sha256,
                    ground_truth_state=entry.ground_truth_state,
                    oracle_hash=entry.oracle_hash,
                )
            )

        sorted_docs = sorted(domain_documents, key=lambda d: d.document_id)
        sorted_entries = sorted(updated_entries, key=lambda d: d.document_id)

        manifest = CorpusManifest(
            corpus_version=CorpusVersion(value=current_dto.corpus_version),
            documents=sorted_docs,
        )
        manifest_hash = ManifestFingerprintCalculator.compute_hash(
            manifest.corpus_version, manifest.documents
        )

        self._writer.save_manifest_dto(
            RawCorpusManifestDTO(
                corpus_version=manifest.corpus_version.value,
                manifest_hash=manifest_hash,
                documents=sorted_entries,
            )
        )

        return BootstrapCorpusResult(
            manifest_hash=manifest_hash,
            documents_processed=len(sorted_docs),
            total_pages_indexed=total_pages,
        )


class LoadCorpusManifestUseCase:
    """Camino de Lectura en Runtime. Solo lectura.

    NADR-14 §5.1 R2: el contrato de lectura de runtime NO expone capacidad
    de escritura. Solo inyecta ReaderPort.

    Gate 4 (Wave 4.2): propaga oracle_hash y ground_truth_state desde el DTO
    hacia CorpusDocumentMetadata (Problema D).
    """

    def __init__(self, reader: CorpusManifestReaderPort):
        self._reader = reader

    def execute(self) -> CorpusManifest:
        dto = self._reader.load_raw_manifest()
        return CorpusManifest(
            corpus_version=CorpusVersion(value=dto.corpus_version),
            documents=[
                CorpusDocumentMetadata(
                    document_id=entry.document_id,
                    fingerprint=DocumentFingerprint(sha256=entry.sha256),
                    traits=frozenset(ExtractionChallengeTrait(t) for t in entry.traits),
                    page_count=entry.page_count,
                    # Gate 4 (Wave 4.2): propagar dimensiones de identidad
                    oracle_hash=entry.oracle_hash,
                    ground_truth_state=entry.ground_truth_state,
                )
                for entry in dto.documents
            ],
        )