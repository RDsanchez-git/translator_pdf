import pathlib
from typing import Protocol
from core.benchmark.corpus.dtos import RawCorpusManifestDTO


class DocumentMetadataExtractorPort(Protocol):
    def extract_sha256(self, file_path: pathlib.Path) -> str: ...
    def extract_page_count(self, file_path: pathlib.Path) -> int: ...


class CorpusManifestReaderPort(Protocol):
    """Contrato de lectura runtime (NADR-14 §5.1 R1).

    NADR-14 §5.1 R2: el contrato de lectura de runtime NO expone
    capacidad de escritura ni mutación de la baseline.
    """
    def load_raw_manifest(self) -> RawCorpusManifestDTO: ...


class CorpusManifestWriterPort(Protocol):
    """Contrato de escritura de curaduría (NADR-14 §5.1 R1).

    NADR-14 §5.1 R3: el contrato de curaduría NO es consumido por
    los caminos de runtime que leen la baseline certificada.
    """
    def save_manifest_dto(self, dto: RawCorpusManifestDTO) -> None: ...