import hashlib
import pathlib
import fitz 
from core.benchmark.corpus.ports import DocumentMetadataExtractorPort

class PyMuPdfDocumentMetadataExtractor(DocumentMetadataExtractorPort):
    def extract_sha256(self, file_path: pathlib.Path) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def extract_page_count(self, file_path: pathlib.Path) -> int:
        with fitz.open(file_path) as doc:
            return len(doc)