from enum import StrEnum
from dataclasses import dataclass

class ValidationSeverity(StrEnum):
    """
    Taxonomía estricta para anomalías topológicas pre-LLM.
    Se aísla del 'Severity' documental para controlar el flujo del pipeline (Routing/Chunking).
    """
    INFO = "INFO"
    SOFT_FAIL = "SOFT_FAIL"
    HARD_FAIL = "HARD_FAIL"

@dataclass(slots=True, frozen=True)
class ValidationResult:
    """
    DTO inmutable de infracción estructural.
    No colisiona con el ValidationResult post-traducción.
    """
    node_id: str
    sequence_id: int
    severity: ValidationSeverity
    message: str
    validator_name: str