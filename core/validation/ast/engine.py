from collections.abc import Iterable, Iterator
from core.ast.models import ASTNode
from core.validation.ast.models import ValidationResult
from core.validation.ast.protocols import NodeValidator

class PolymorphicValidationEngine:
    """
    SOTA: Motor de validación Inversion-of-Control (Registry).
    Acumula y cede infracciones estructurales en flujo continuo.
    """
    __slots__ = ("_validators",)

    def __init__(self, validators: Iterable[NodeValidator]):
        # SOTA: Inmutabilidad interna garantizada, tolerando generadores en la inyección.
        self._validators = tuple(validators)

    def validate_stream(self, stream: Iterable[ASTNode]) -> Iterator[ValidationResult]:
        for node in stream:
            for validator in self._validators:
                if validator.can_validate(node):
                    yield from validator.validate(node)