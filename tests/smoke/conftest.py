# tests/smoke/conftest.py
import pytest
from core.validation.pipeline import ValidationPipeline
from core.validation.adapters.structural_bridge import StructuralValidationBridge
from core.validation.preservation import PreservationValidator
from core.validation.perimeter import PerimeterValidator
from core.validation.semantic import SemanticValidator
from core.validation.volumetric import VolumetricValidator

@pytest.fixture
def reliability_pipeline():
    """Factoría aislada de la capa de confiabilidad para Smoke Tests."""
    pipeline = ValidationPipeline()
    pv = PreservationValidator()
    
    # NADR-04 §5.2: StructuralValidationBridge reemplaza LegacyValidatorAdapter
    structural_bridge = StructuralValidationBridge()
    
    pipeline.add_chunk_validator(structural_bridge)
    pipeline.add_chunk_validator(pv)
    pipeline.add_chunk_validator(PerimeterValidator())
    pipeline.add_chunk_validator(SemanticValidator())
    pipeline.add_chunk_validator(VolumetricValidator())
    
    pipeline.add_document_validator(structural_bridge)
    pipeline.add_document_validator(pv)
    
    return pipeline