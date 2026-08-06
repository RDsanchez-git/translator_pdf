"""
tests/unit/test_pipeline_factory.py

Pruebas unitarias de configuración y Composition Root.
"""

def test_extraction_provider_factory_returns_valid_provider() -> None:
    """Verifica que la factoría retorna un ExtractionProvider válido."""
    from apps.bootstrap.extraction_config import ExtractionProviderId
    from apps.bootstrap.provider_factory import ExtractionProviderFactory
    from core.extraction.provider import ExtractionProvider

    provider = ExtractionProviderFactory.create(ExtractionProviderId.PYMUPDF)

    assert isinstance(provider, ExtractionProvider)
    assert provider.capabilities is not None


def test_extraction_provider_factory_rejects_unknown_id() -> None:
    """Verifica fail-fast ante un provider ID no registrado."""
    import pytest
    from apps.bootstrap.provider_factory import ExtractionProviderFactory

    # Usar un string arbitrario que no está en el enum
    with pytest.raises(ValueError, match="ExtractionProviderId no soportado"):
        ExtractionProviderFactory.create("nonexistent_provider")  # type: ignore