from typing import Protocol, runtime_checkable
from collections.abc import Iterable, Iterator
from core.ast.models import ASTNode
from core.validation.ast.models import ValidationResult

class NodeTextExtractor(Protocol):
    """SOTA: Puerto para la proyección agnóstica de texto del AST."""
    def extract(self, node: ASTNode) -> str:
        ...

        
@runtime_checkable
class NodeValidator(Protocol):
    """
    Contrato puro para estrategias de validación pre-vuelo aisladas.
    Invariante: Componente estrictamente observacional (Zero Mutation).
    """
    
    @property
    def name(self) -> str:
        """Identificador determinista para trazabilidad."""
        ...

    def can_validate(self, node: ASTNode) -> bool:
        """
        Determina aplicabilidad en tiempo constante O(1).
        Invariante: Debe evaluar UNA única dimensión del dominio.
        """
        ...

    def validate(self, node: ASTNode) -> Iterator[ValidationResult]:
        """Ejecuta la validación y emite infracciones de forma perezosa."""
        ...


class ValidationEngine(Protocol):
    """
    Puerto funcional para la orquestación polimórfica en flujo continuo pre-LLM.
    """
    
    def validate_stream(self, stream: Iterable[ASTNode]) -> Iterator[ValidationResult]:
        """
        Consume el AST en memoria plana O(1).
        Aplica la Ley de Postel: acepta Iterable (liberal) y devuelve Iterator (conservador).
        """
        ...