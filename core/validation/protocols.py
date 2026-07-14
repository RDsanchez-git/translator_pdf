from typing import Protocol, List
from enum import Enum

class ContextReductionLevel(str, Enum):
    FULL = "full"
    HEADINGS = "headings"
    BREADCRUMBS = "breadcrumbs"
    NONE = "none"

class ContextCompressionPolicy(Protocol):
    """SOTA: Protocolo inyectable para estrategias de compresión iterativa de contexto."""
    def get_levels(self) -> List[ContextReductionLevel]: ...

class TokenEstimatorProtocol(Protocol):
    """SOTA: Puerto Hexagonal Transversal para motores de estimación."""
    def estimate_tokens(self, text: str) -> int: ...