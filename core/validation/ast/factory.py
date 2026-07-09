from core.validation.ast.protocols import ValidationEngine
from core.validation.ast.models import ValidationSeverity
from core.validation.ast.extractors import StronglyTypedTextExtractor
from core.validation.ast.validators.structural import StructuralEquationValidator
from core.validation.ast.validators.strategy import PassthroughIntegrityValidator
from core.validation.ast.engine import PolymorphicValidationEngine

def build_default_validation_engine() -> ValidationEngine:
    """
    SOTA: Constructor de composición (Factory) del Bounded Context.
    Oculta la instanciación y el registro de validadores a las capas superiores.
    """
    extractor = StronglyTypedTextExtractor()
    
    validators = (
        StructuralEquationValidator(
            extractor=extractor, 
            severity=ValidationSeverity.HARD_FAIL
        ),
        PassthroughIntegrityValidator(
            severity=ValidationSeverity.SOFT_FAIL
        ),
    )
    
    return PolymorphicValidationEngine(validators=validators)