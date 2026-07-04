from core.domain.document import DocumentLayout, DocumentProfile, DocumentType
from core.extraction.provider import ExtractionProvider, ExtractionCapabilities

class PyMuPDFProvider(ExtractionProvider):
    def __init__(self, write_images: bool = True):
        self._write_images = write_images
        self._capabilities = ExtractionCapabilities(
            has_bbox=True,
            has_tables=False,
            has_images=self._write_images,
            has_font_info=True,
            has_vector_text=True,
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