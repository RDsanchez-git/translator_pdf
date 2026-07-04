from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict
from core.domain.document import DocumentLayout

class ExtractionCapabilities(BaseModel):
    model_config = ConfigDict(frozen=True)
    has_bbox: bool
    has_tables: bool
    has_images: bool
    has_font_info: bool
    has_vector_text: bool
    supports_math: bool
    supports_multicolumn: bool
    supports_rotation: bool

class ExtractionProvider(ABC):
    """Contrato abstracto inmutable para la extracción física perimetral."""

    @property
    @abstractmethod
    def capabilities(self) -> ExtractionCapabilities:
        """Retorna las capacidades nativas declaradas por el proveedor."""
        pass

    @abstractmethod
    def extract(self, pdf_path: str) -> DocumentLayout:
        """Ejecuta la extracción física y espacial devolviendo el Aggregate Root del dominio.
        
        Raises:
            ProviderFailure: Ante fallos del motor subyacente.
            LayoutRecoveryError: Ante corrupciones topológicas del layout generado.
        """
        pass