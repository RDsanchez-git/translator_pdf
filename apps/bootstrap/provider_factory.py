from core.extraction.provider import ExtractionProvider
from apps.bootstrap.extraction_config import ExtractionProviderId
from core.extraction.ocr_providers.pymupdf_provider import PyMuPDFProvider
from core.layout.classification import LayoutClassifier, HeuristicLayoutClassifier


class ExtractionProviderFactory:
    """
    Factoría de wiring que resuelve proveedores concretos.

    NADR-02 §5.2 R1: La selección del proveedor de extracción MUST estar
    gobernada por una política explícita del sistema.
    NADR-11 §5.1 R1: Este componente pertenece al Composition Root.
    """

    @classmethod
    def create(
        cls,
        provider_id: ExtractionProviderId,
        classifier: LayoutClassifier | None = None,
    ) -> ExtractionProvider:
        if provider_id == ExtractionProviderId.PYMUPDF:
            if classifier is None:
                classifier = HeuristicLayoutClassifier()
            return PyMuPDFProvider(classifier=classifier)

        raise ValueError(
            f"ExtractionProviderId no soportado: {provider_id}. "
            f"Disponibles: [PYMUPDF]"
        )