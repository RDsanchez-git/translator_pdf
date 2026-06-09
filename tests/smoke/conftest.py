# tests/smoke/conftest.py
import pytest
from core.validation.pipeline import ValidationPipeline
from core.validation.legacy_adapter import LegacyValidatorAdapter
from core.validation.structural_validator import StructuralValidator
from core.validation.preservation import PreservationValidator
from core.validation.perimeter import PerimeterValidator
from core.validation.semantic import SemanticValidator
from core.validation.volumetric import VolumetricValidator
from core.validation.models import Severity

@pytest.fixture
def reliability_pipeline():
    """Factoría aislada de la capa de confiabilidad para Smoke Tests."""
    severity_map = {
        "RESIDUAL_HTML": Severity.HARD_FAIL,
        "UNBALANCED_BRACES_EARLY": Severity.HARD_FAIL,
        "UNBALANCED_BRACES_OPEN": Severity.HARD_FAIL,
        "UNBALANCED_BRACKETS_EARLY": Severity.HARD_FAIL,
        "UNBALANCED_BRACKETS_OPEN": Severity.HARD_FAIL,
        "UNBALANCED_DISPLAY_MATH": Severity.HARD_FAIL,
        "UNBALANCED_INLINE_MATH": Severity.HARD_FAIL,
        "ENV_MISMATCH": Severity.HARD_FAIL,
        "ENV_UNCLOSED": Severity.HARD_FAIL,
    }
    pipeline = ValidationPipeline()
    pv = PreservationValidator()
    
    # SOTA: Instanciación explícita para doble registro de ámbito (CHUNK y DOCUMENT)
    structural_adapter = LegacyValidatorAdapter(StructuralValidator, severity_map)
    
    pipeline.add_chunk_validator(structural_adapter)
    pipeline.add_chunk_validator(pv)
    pipeline.add_chunk_validator(PerimeterValidator())
    pipeline.add_chunk_validator(SemanticValidator())
    pipeline.add_chunk_validator(VolumetricValidator())
    
    pipeline.add_document_validator(structural_adapter)  # Cobertura de SI-03
    pipeline.add_document_validator(pv)                  # Cobertura de PI-04
    
    return pipeline