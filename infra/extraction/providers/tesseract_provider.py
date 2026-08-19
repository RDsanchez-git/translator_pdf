import os
import pytesseract
from core.domain.document import DocumentLayout, DocumentProfile, DocumentType
from core.extraction.provider import ExtractionProvider, ExtractionCapabilities

class TesseractProvider(ExtractionProvider):
    def __init__(self, tesseract_cmd: str, tessdata_prefix: str, max_workers: int = 4):
        self._max_workers = max_workers
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        os.environ["TESSDATA_PREFIX"] = tessdata_prefix
        self._capabilities = ExtractionCapabilities(
            has_bbox=True,
            has_tables=False,
            has_images=False,
            has_font_info=False,
            has_vector_text=False,
            supports_math=False,
            supports_multicolumn=False,
            supports_rotation=False
        )

    @property
    def capabilities(self) -> ExtractionCapabilities:
        return self._capabilities

    def extract(self, pdf_path: str) -> DocumentLayout:
        profile = DocumentProfile(
            document_type=DocumentType.PAPER,
            primary_language="en"
        )
        return DocumentLayout(
            source_path=pdf_path,
            total_pages=1,
            profile=profile,
            pages=[]
        )