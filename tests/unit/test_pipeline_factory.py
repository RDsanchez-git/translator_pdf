"""
tests/unit/test_pipeline_factory.py

Pruebas unitarias de configuración y Composition Root.
"""

def test_default_extraction_provider_is_strictly_typed() -> None:
    from apps.bootstrap.pipeline_factory import DEFAULT_EXTRACTION_PROVIDER
    from core.benchmark.types import ProviderKind

    assert isinstance(DEFAULT_EXTRACTION_PROVIDER, ProviderKind)
    assert DEFAULT_EXTRACTION_PROVIDER is ProviderKind.OCR_PARSER