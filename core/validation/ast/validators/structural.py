from typing import Final
from collections.abc import Iterator
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.validation.ast.models import ValidationResult, ValidationSeverity
from core.validation.ast.protocols import NodeTextExtractor

class StructuralEquationValidator:
    """
    SOTA: Validador estructural iterativo con extracción delegada y 
    algoritmo de balanceo Fail-Fast.
    """
    NAME: Final = "StructuralEquationValidator"
    __slots__ = ("_extractor", "_severity")

    def __init__(
        self, 
        extractor: NodeTextExtractor, 
        severity: ValidationSeverity = ValidationSeverity.SOFT_FAIL
    ):
        self._extractor = extractor
        self._severity = severity

    @property
    def name(self) -> str:
        return self.NAME

    def can_validate(self, node: ASTNode) -> bool:
        return node.node_type == ContentNodeType.DISPLAY_EQUATION

    def validate(self, node: ASTNode) -> Iterator[ValidationResult]:
        content = self._extractor.extract(node)
        
        if not content:
            return

        depth = 0
        for char in content:
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth < 0:
                    # Invariante roto: cierre prematuro. Abortamos evaluación del string.
                    yield ValidationResult(
                        node_id=str(node.node_id),
                        sequence_id=node.sequence_id,
                        severity=self._severity,
                        message="Corrupción LaTeX: cierre prematuro de llaves en '}}'.",
                        validator_name=self.name
                    )
                    return

        if depth != 0:
            yield ValidationResult(
                node_id=str(node.node_id),
                sequence_id=node.sequence_id,
                severity=self._severity,
                message=f"Corrupción LaTeX: llaves sin cerrar (estado de pila: {depth}).",
                validator_name=self.name
            )