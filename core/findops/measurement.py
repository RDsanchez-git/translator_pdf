from typing import Protocol
from dataclasses import dataclass
from core.validation.estimators import TokenEstimatorProtocol

@dataclass(frozen=True, slots=True)
class InferenceMeasurement:
    """SOTA: DTO puramente observacional y volumétrico."""
    instruction_tokens: int
    context_tokens: int
    payload_tokens: int
    structural_overhead: int

    @property
    def total_tokens(self) -> int:
        return self.instruction_tokens + self.context_tokens + self.payload_tokens + self.structural_overhead

class MeasurableInference(Protocol):
    """SOTA: Interface Segregation. Lo único que FinOps necesita saber."""
    @property
    def logical_payload(self) -> str: ...
    
    @property
    def logical_context(self) -> str: ...
    
    @property
    def logical_instructions(self) -> str: ...
    
    @property
    def physical_network_payload(self) -> str: ...

class InferenceMeasurementService:
    """SOTA: Mide cualquier intención de inferencia que cumpla el protocolo."""
    def __init__(self, estimator: TokenEstimatorProtocol):
        self._estimator = estimator

    def measure(self, inference: MeasurableInference) -> InferenceMeasurement:
        pay_tok = self._estimator.estimate_tokens(inference.logical_payload)
        ctx_tok = self._estimator.estimate_tokens(inference.logical_context)
        inst_tok = self._estimator.estimate_tokens(inference.logical_instructions)
        
        total_tok = self._estimator.estimate_tokens(inference.physical_network_payload)
        overhead = max(0, total_tok - (pay_tok + ctx_tok + inst_tok))

        return InferenceMeasurement(
            instruction_tokens=inst_tok,
            context_tokens=ctx_tok,
            payload_tokens=pay_tok,
            structural_overhead=overhead
        )