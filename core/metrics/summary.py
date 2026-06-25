import math
from dataclasses import dataclass
from typing import List
from core.ast.models import DispatchResult
from core.compiler.assembler import DocumentAssemblyDecision
from core.metrics.pricing import PricingEngine
from core.ast.models import FailureReason, ExecutionStatus

@dataclass(frozen=True)
class TranslationAuditSummary:
    """SOTA: DTO inmutable SRE/FinOps ampliado."""
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
    
    # Ratios Operacionales
    cache_hit_ratio: float
    network_execution_ratio: float  
    
    # Telemetría ADR-008: Presupuesto
    context_overflow_ratio: float
    provider_switch_ratio: float
    average_utilization_ratio: float
    p95_utilization_ratio: float    
    
    # Telemetría ADR-008: Cuotas y Contención
    total_quota_wait_seconds: float
    p50_quota_wait_seconds: float   
    p95_quota_wait_seconds: float   
    p99_quota_wait_seconds: float   
    average_quota_attempts: float
    token_reservation_failures: int
    circuit_breaker_trips: int

class SummaryBuilder:
    """SOTA: Constructor funcional puro alineado a la telemetría agregada."""
    
    @staticmethod
    def _percentile(data: List[float], p: float) -> float:
        if not data:
            return 0.0
        s_data = sorted(data)
        n = len(s_data)
        k = math.ceil(p * n) - 1
        return s_data[max(0, k)]

    @staticmethod
    def build(dispatch_result: DispatchResult, decision: DocumentAssemblyDecision) -> TranslationAuditSummary:
        network_hits = 0
        cache_hits = 0
        total_cost = 0.0
        hypothetical_cache_cost = 0.0
        total_latency = 0.0

        dispatch_total = len(dispatch_result.outcomes)
        overflow_count = 0
        switch_count = 0
        
        utilization_ratios: List[float] = []
        quota_waits: List[float] = []
        quota_attempts: List[int] = []
        reservation_failures = 0
        circuit_trips = 0

        for outcome in dispatch_result.outcomes:
            if outcome.telemetry:
                if "utilization_ratio" in outcome.telemetry:
                    utilization_ratios.append(outcome.telemetry["utilization_ratio"])
                if outcome.telemetry.get("target_provider") == "fallback_large_window":
                    switch_count += 1
                if "quota_wait_seconds" in outcome.telemetry:
                    quota_waits.append(outcome.telemetry["quota_wait_seconds"])
                if "quota_reservation_attempts" in outcome.telemetry:
                    quota_attempts.append(outcome.telemetry["quota_reservation_attempts"])

            if outcome.status == ExecutionStatus.FAILED:
                if outcome.failure_reason == FailureReason.CONTEXT_OVERFLOW:
                    overflow_count += 1
                elif outcome.failure_reason == FailureReason.CIRCUIT_OPEN:
                    circuit_trips += 1
                # Captura segura para versiones anteriores a la re-tipificación (Fase 14 -> 15)
                elif outcome.failure_reason in ("quota_rejection", "quota_timeout", FailureReason.QUOTA_REJECTION, FailureReason.QUOTA_TIMEOUT):
                    reservation_failures += 1

        overflow_ratio = (overflow_count / dispatch_total) if dispatch_total > 0 else 0.0
        switch_ratio = (switch_count / dispatch_total) if dispatch_total > 0 else 0.0
        
        avg_utilization = (sum(utilization_ratios) / len(utilization_ratios)) if utilization_ratios else 0.0
        avg_attempts = (sum(quota_attempts) / len(quota_attempts)) if quota_attempts else 1.0

        doc = decision.document
        successful_units = [out.translated_unit for out in dispatch_result.outcomes if out.is_success and out.translated_unit]

        for unit in successful_units:
            total_latency += unit.latency_ms
            if unit.model_name.startswith("cache_hit:"):
                cache_hits += 1
                base_model = unit.model_name.replace("cache_hit:", "")
                estimated_tokens = max(1, len(unit.translated_payload) // 4)
                hypothetical_cache_cost += PricingEngine.calculate_cost(base_model, estimated_tokens, estimated_tokens)
            else:
                network_hits += 1
                total_cost += PricingEngine.calculate_cost(unit.model_name, unit.input_tokens, unit.output_tokens)

        llm_eligible_chunks = network_hits + cache_hits
        hit_ratio = (cache_hits / llm_eligible_chunks) if llm_eligible_chunks > 0 else 0.0
        network_ratio = (network_hits / llm_eligible_chunks) if llm_eligible_chunks > 0 else 0.0
        
        estimated_cost_without_cache = total_cost + hypothetical_cache_cost
        total_failed = len(decision.failed_outcomes)
        doc_total = doc.total_chunks if doc else 0
        success_rate = ((doc_total - total_failed) / doc_total) if doc_total > 0 else 0.0

        return TranslationAuditSummary(
            total_chunks=doc_total,
            translated_chunks_network=network_hits,
            translated_chunks_cache=cache_hits,
            passthrough_chunks=doc.passthrough_chunks if doc else total_failed,
            total_failed_chunks=total_failed,                  
            dispatch_success_rate=round(success_rate, 4),
            total_input_tokens=doc.total_input_tokens if doc else 0,
            total_output_tokens=doc.total_output_tokens if doc else 0,
            total_cost_usd=round(total_cost, 6),
            estimated_cost_without_cache_usd=round(estimated_cost_without_cache, 6),
            cost_saved_by_cache_usd=round(hypothetical_cache_cost, 6),
            total_latency_ms=round(total_latency, 2),
            cache_hit_ratio=round(hit_ratio, 4),
            network_execution_ratio=round(network_ratio, 4),
            context_overflow_ratio=round(overflow_ratio, 4),
            provider_switch_ratio=round(switch_ratio, 4),
            average_utilization_ratio=round(avg_utilization, 4),
            p95_utilization_ratio=round(SummaryBuilder._percentile(utilization_ratios, 0.95), 4),
            total_quota_wait_seconds=round(sum(quota_waits), 3),
            p50_quota_wait_seconds=round(SummaryBuilder._percentile(quota_waits, 0.50), 3),
            p95_quota_wait_seconds=round(SummaryBuilder._percentile(quota_waits, 0.95), 3),
            p99_quota_wait_seconds=round(SummaryBuilder._percentile(quota_waits, 0.99), 3),
            average_quota_attempts=round(avg_attempts, 2),
            token_reservation_failures=reservation_failures,
            circuit_breaker_trips=circuit_trips
        )