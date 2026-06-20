from dataclasses import dataclass
from core.ast.models import DispatchResult
from core.compiler.assembler import DocumentAssemblyDecision
from core.metrics.pricing import PricingEngine

@dataclass(frozen=True)
class TranslationAuditSummary:
    """SOTA: DTO inmutable que concentra la telemetría operativa, financiera y de ahorro (FinOps)."""
    total_chunks: int
    translated_chunks_network: int
    translated_chunks_cache: int
    passthrough_chunks: int
    total_failed_chunks: int           
    dispatch_success_rate: float
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    estimated_cost_without_cache_usd: float
    cost_saved_by_cache_usd: float
    total_latency_ms: float
    cache_hit_ratio: float

class SummaryBuilder:
    """SOTA: Constructor funcional puro alineado a la telemetría agregada (Result Pattern)."""
    
    @staticmethod
    def build(dispatch_result: DispatchResult, decision: DocumentAssemblyDecision) -> TranslationAuditSummary:
        network_hits = 0
        cache_hits = 0
        total_cost = 0.0
        hypothetical_cache_cost = 0.0
        total_latency = 0.0

        doc = decision.document

        # Extracción segura de unidades materializadas desde el DispatchResult
        successful_units = [
            outcome.translated_unit 
            for outcome in dispatch_result.outcomes 
            if outcome.is_success and outcome.translated_unit is not None
        ]

        for unit in successful_units:
            total_latency += unit.latency_ms
            
            if unit.model_name.startswith("cache_hit:"):
                cache_hits += 1
                base_model = unit.model_name.replace("cache_hit:", "")
                estimated_tokens = max(1, len(unit.translated_payload) // 4)
                
                hypothetical_cache_cost += PricingEngine.calculate_cost(
                    model_name=base_model, 
                    input_tokens=estimated_tokens, 
                    output_tokens=estimated_tokens
                )
            else:
                network_hits += 1
                total_cost += PricingEngine.calculate_cost(
                    model_name=unit.model_name, 
                    input_tokens=unit.input_tokens, 
                    output_tokens=unit.output_tokens
                )

        llm_eligible_chunks = network_hits + cache_hits
        hit_ratio = (cache_hits / llm_eligible_chunks) if llm_eligible_chunks > 0 else 0.0
        estimated_cost_without_cache = total_cost + hypothetical_cache_cost

        total_failed = len(decision.failed_outcomes)
        total_chunks = doc.total_chunks if doc else 0
        success_rate = ((total_chunks - total_failed) / total_chunks) if total_chunks > 0 else 0.0

        return TranslationAuditSummary(
            total_chunks=doc.total_chunks if doc else 0,
            translated_chunks_network=network_hits,
            translated_chunks_cache=cache_hits,
            passthrough_chunks=doc.passthrough_chunks if doc else len(decision.failed_outcomes),
            total_failed_chunks=total_failed,                  # Integración
            dispatch_success_rate=round(success_rate, 4),
            total_input_tokens=doc.total_input_tokens if doc else 0,
            total_output_tokens=doc.total_output_tokens if doc else 0,
            total_cost_usd=round(total_cost, 6),
            estimated_cost_without_cache_usd=round(estimated_cost_without_cache, 6),
            cost_saved_by_cache_usd=round(hypothetical_cache_cost, 6),
            total_latency_ms=round(total_latency, 2),
            cache_hit_ratio=round(hit_ratio, 4)
        )