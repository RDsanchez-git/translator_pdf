from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class TelemetryEventType(str, Enum):
    CACHE_HIT = "cache_hit"
    RATE_LIMIT_429 = "rate_limit_429"
    CB_TRIP = "circuit_breaker_trip"
    CONTEXT_OVERFLOW = "context_overflow"
    PROVIDER_SELECTION = "provider_selection"
    TRANSLATION_FAILURE = "translation_failure"
    TRANSLATION_SUCCESS = "translation_success"

class ProviderSelectionReason(str, Enum):
    """SOTA FIX: Taxonomía causal del enrutamiento."""
    PRIMARY_ROUTE = "primary_route"
    FALLBACK_RATE_LIMIT = "fallback_rate_limit"
    FALLBACK_CIRCUIT_BREAKER = "fallback_circuit_breaker"
    FALLBACK_CONTEXT_WINDOW = "fallback_context_window"

@dataclass(frozen=True, slots=True)
class ProductionTelemetryEvent:
    execution_id: str
    chunk_id: str
    provider: str
    event_type: TelemetryEventType
    selection_reason: Optional[ProviderSelectionReason] = None
    latency_ms: float = 0.0
    quota_wait_ms: float = 0.0  
    input_tokens: int = 0
    output_tokens: int = 0

@dataclass(frozen=True, slots=True)
class SLOConfig:
    """SOTA FIX: Gobernanza operacional y fronteras de degradación."""
    max_translation_failure_ratio: float = 0.01  # 1%
    max_context_overflow_ratio: float = 0.00     # Tolerancia cero
    max_p95_quota_wait_ms: float = 5000.0        # 5 segundos max en cola
    min_effective_tps: float = 25.0              # Piso mínimo para que la LPU tenga sentido

@dataclass(frozen=True, slots=True)
class SLOViolation:
    metric: str
    threshold: float
    actual_value: float

@dataclass(frozen=True, slots=True)
class ProductionHealthReport:
    execution_id: str
    total_chunks_processed: int
    cache_hit_ratio: float
    circuit_breaker_trips: int
    context_overflow_ratio: float
    provider_selection_ratio: Dict[str, Dict[str, float]]  
    translation_failure_ratio: float
    p95_quota_wait_ms: float
    effective_tps: float
    theoretical_tps: float
    throughput_degradation_ratio: float
    slo_violations: List[SLOViolation]
    is_healthy: bool