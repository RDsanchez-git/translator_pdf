from typing import Protocol
from dataclasses import dataclass
from math import ceil, isfinite
from core.validation.protocols import TokenEstimatorProtocol

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

    def estimate_response_reserve(self, empty_response: str, source_response: str,
                                  expansion_factor: float) -> int:
        """Planning estimate, not an accredited provider completion bound.

        Count the actual serialized response shape once. Expand only the
        incremental source text, not the binding identities or request-only
        instructions. Both samples use the same output serialization.
        """
        structure = self._estimator.estimate_tokens(empty_response)
        populated = self._estimator.estimate_tokens(source_response)
        if (type(structure) is not int or structure <= 0
                or type(populated) is not int or populated <= 0
                or not isfinite(expansion_factor) or expansion_factor < 1):
            raise ValueError("G3_RESPONSE_BUDGET_MEASUREMENT_INVALID")
        return structure + ceil(max(0, populated - structure) * expansion_factor)

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