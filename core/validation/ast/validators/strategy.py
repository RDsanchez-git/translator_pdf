from typing import Final
from collections.abc import Iterator
from core.ast.models import ASTNode
from core.ast.enums import TranslationStrategy
from core.validation.ast.models import ValidationResult, ValidationSeverity

class PassthroughIntegrityValidator:
    """
    SOTA: Validador de estrategia para nodos estructurales.
    Garantiza que los nodos que eluden el LLM posean referencias físicas válidas
    en el documento original, evitando corrupciones de Layout en el ensamblaje.
    """
    NAME: Final = "PassthroughIntegrityValidator"
    __slots__ = ("_severity",)

    def __init__(self, severity: ValidationSeverity = ValidationSeverity.HARD_FAIL):
        self._severity = severity

    @property
    def name(self) -> str:
        return self.NAME

    def can_validate(self, node: ASTNode) -> bool:
        return node.strategy == TranslationStrategy.PASSTHROUGH

    def validate(self, node: ASTNode) -> Iterator[ValidationResult]:
        # Zero-Reflection: Consumimos la metadata física que es estáticamente tipada.
        # Un nodo PASSTHROUGH (imagen, tabla intacta) sin Bounding Boxes carece de 
        # anclaje físico, lo cual es una invariante rota para el ensamblador PDF.
        if not node.metadata.bboxes:
            yield ValidationResult(
                node_id=str(node.node_id),
                sequence_id=node.sequence_id,
                severity=self._severity,
                message="Integridad espacial comprometida: Nodo PASSTHROUGH sin bounding boxes.",
                validator_name=self.name
            )