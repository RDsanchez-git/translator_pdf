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
                    oracle_hash=entry.oracle_hash,
                    ground_truth_state=entry.ground_truth_state,
                )
                for entry in dto.documents
            ],
        )


class AddDocumentToCorpusUseCase:
    """Añade un documento al corpus preservando las entradas selladas (R25/R26).

    Encapsula la lógica de negocio: validación de duplicados, preservación de
    sellados, mapeo DTO->dominio y recálculo del hash encadenado. El Imperative
    Shell solo orquesta I/O (copiar PDF, parsear args).
    """

    def __init__(
        self,
        reader: CorpusManifestReaderPort,
        writer: CorpusManifestWriterPort,
        extractor: DocumentMetadataExtractorPort,
    ) -> None:
        self._reader = reader
        self._writer = writer
        self._extractor = extractor

    def execute(
        self,
        pdf_path,
        doc_id: str,
        traits: list[str],
        new_version: str,
    ) -> tuple[str, str, int]:
        """Retorna (new_manifest_hash, sha256, page_count). Lanza IndexedError ante violación."""
        from core.shared.errors import IndexedError

        # 1. Cargar manifest existente (DTO)
        dto = self._reader.load_raw_manifest()

        # 2. Validar versión nueva distinta de la vigente (cascada de identidades, GF-02)
        if new_version == dto.corpus_version:
            raise IndexedError(
                "ADD-DOC-008",
                f"corpus_version '{new_version}' igual a la vigente. "
                f"Añadir un documento es una nueva versión de corpus.",
            )

        # 3. Validar doc_id no duplicado
        existing_ids = {e.document_id for e in dto.documents}
        if doc_id in existing_ids:
            raise IndexedError("ADD-DOC-005", f"doc_id '{doc_id}' ya existe en el manifest.")

        # 4. Extraer metadata del nuevo PDF
        sha256 = self._extractor.extract_sha256(pdf_path)
        page_count = self._extractor.extract_page_count(pdf_path)

        # 5. Validar sha256 no duplicado (contenido duplicado)
        existing_sha = {e.sha256 for e in dto.documents}
        if sha256 in existing_sha:
            raise IndexedError("ADD-DOC-006", "SHA-256 duplicado: el contenido ya está en el corpus.")

        # 6. Construir nueva entrada DTO (oracle_hash=None, state=None: pre-sealing)
        new_entry = RawDocumentEntryDTO(
            document_id=doc_id,
            sha256=sha256,
            traits=list(traits),
            page_count=page_count,
            oracle_hash=None,
            ground_truth_state=None,
        )

        # 7. Preservar entradas selladas byte-a-byte + añadir nueva (R25/R26)
        new_documents = list(dto.documents) + [new_entry]

        # 8. Mapear DTO->dominio para compute_hash (misma lógica que LoadCorpusManifestUseCase)
        domain_docs = [
            CorpusDocumentMetadata(
                document_id=e.document_id,
                fingerprint=DocumentFingerprint(sha256=e.sha256),
                traits=frozenset(ExtractionChallengeTrait(t) for t in e.traits),
                page_count=e.page_count,
                oracle_hash=e.oracle_hash,
                ground_truth_state=e.ground_truth_state,
            )
            for e in new_documents
        ]
        new_hash = ManifestFingerprintCalculator.compute_hash(
            CorpusVersion(value=new_version), domain_docs
        )

        # 9. Construir nuevo DTO con hash recalculado y salvar
        new_dto = RawCorpusManifestDTO(
            corpus_version=new_version,
            manifest_hash=new_hash,
            documents=new_documents,
        )
        self._writer.save_manifest_dto(new_dto)
        return new_hash, sha256, page_count