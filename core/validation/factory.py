# core/validation/factory.py
"""
Factoría de construcción del ValidationPipeline de producción.

NADR-04 §5.1 R2: ÚNICO punto de construcción del ValidationPipeline.
NADR-04 §5.2 R2: Sin LegacyValidatorAdapter.
NADR-04 §5.2 R3: StructuralValidator invocado directamente vía bridge limpio.
"""

from core.validation.pipeline import ValidationPipeline
from core.validation.adapters.structural_bridge import StructuralValidationBridge
from core.validation.preservation import PreservationValidator
from core.validation.perimeter import PerimeterValidator
from core.validation.semantic import SemanticValidator
from core.validation.volumetric import VolumetricValidator


def build_validation_pipeline() -> ValidationPipeline:
    """
    Construye el ValidationPipeline de producción con validadores nativos.

    Retorna un pipeline completamente cableado, listo para ser inyectado
    en el AsyncDispatcher y el HealingPipeline por constructor.
    """
    pipeline = ValidationPipeline()

    # Validación estructural (reemplaza LegacyValidatorAdapter)
    structural_bridge = StructuralValidationBridge()
    pipeline.add_chunk_validator(structural_bridge)
    pipeline.add_document_validator(structural_bridge)

    # Validadores de dominio nativos
    pipeline.add_chunk_validator(PreservationValidator())
    pipeline.add_chunk_validator(PerimeterValidator())
    pipeline.add_chunk_validator(SemanticValidator())
    pipeline.add_chunk_validator(VolumetricValidator())
    pipeline.add_document_validator(PreservationValidator())

    return pipeline