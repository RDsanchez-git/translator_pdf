import sqlite3
import numpy as np
from typing import Dict, List
from core.telemetry.models import ProductionHealthReport, SLOConfig, SLOViolation

class TelemetryAnalyzer:
    """SOTA FIX: Motor de extracción analítica con gobernanza SLO y cálculo de degradación."""
    
    def __init__(self, db_path: str = "infra/telemetry/production.db", slo_config: SLOConfig = SLOConfig()):
        self.db_path = db_path
        self.slo_config = slo_config

    def _query_scalar(self, query: str, params: tuple = ()) -> float:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            result = cursor.fetchone()[0]
            return float(result) if result else 0.0

    def _query_list(self, query: str, params: tuple = ()) -> List[float]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return [row[0] for row in cursor.fetchall() if row[0] is not None]

    def generate_report(self, execution_id: str, wall_clock_seconds: float) -> ProductionHealthReport:
        total_attempts = self._query_scalar("SELECT COUNT(*) FROM telemetry_events WHERE execution_id = ? AND event_type IN ('translation_success', 'translation_failure')", (execution_id,))
        total_network_calls = self._query_scalar("SELECT COUNT(*) FROM telemetry_events WHERE execution_id = ? AND event_type != 'cache_hit'", (execution_id,))

        if total_attempts == 0:
            return ProductionHealthReport(execution_id, 0, 0.0, 0, 0.0, {}, 0.0, 0.0, 0.0, 0.0, 0.0, [], True)

        cache_hits = self._query_scalar("SELECT COUNT(*) FROM telemetry_events WHERE execution_id = ? AND event_type = 'cache_hit'", (execution_id,))
        cb_trips = int(self._query_scalar("SELECT COUNT(*) FROM telemetry_events WHERE execution_id = ? AND event_type = 'circuit_breaker_trip'", (execution_id,)))
        overflows = self._query_scalar("SELECT COUNT(*) FROM telemetry_events WHERE execution_id = ? AND event_type = 'context_overflow'", (execution_id,))
        failures = self._query_scalar("SELECT COUNT(*) FROM telemetry_events WHERE execution_id = ? AND event_type = 'translation_failure'", (execution_id,))

        # SOTA FIX: Taxonomía de Enrutamiento (Por qué se seleccionó cada proveedor)
        provider_selection_ratio: Dict[str, Dict[str, float]] = {}
        if total_network_calls > 0:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT provider, selection_reason, COUNT(*) * 1.0 / ? 
                    FROM telemetry_events 
                    WHERE execution_id = ? AND event_type = 'provider_selection'
                    GROUP BY provider, selection_reason
                ''', (total_network_calls, execution_id))
                for row in cursor.fetchall():
                    prov, reason, ratio = row[0], row[1] or "unknown", round(row[2], 4)
                    if prov not in provider_selection_ratio:
                        provider_selection_ratio[prov] = {}
                    provider_selection_ratio[prov][reason] = ratio

        # SOTA FIX: Métrica de Saturación (Colas de Rate Limit)
        wait_times = self._query_list("SELECT quota_wait_ms FROM telemetry_events WHERE execution_id = ? AND event_type = 'translation_success'", (execution_id,))
        p95_wait_ms = round(float(np.percentile(wait_times, 95)), 2) if wait_times else 0.0

        # SOTA FIX: Degradación de Throughput (TPS Teórico vs Real/Makespan)
        total_tokens = self._query_scalar("SELECT SUM(input_tokens + output_tokens) FROM telemetry_events WHERE execution_id = ? AND event_type = 'translation_success'", (execution_id,))
        cumulative_latency_sec = self._query_scalar("SELECT SUM(latency_ms) / 1000.0 FROM telemetry_events WHERE execution_id = ? AND event_type = 'translation_success'", (execution_id,))
        
        theoretical_tps = round(total_tokens / cumulative_latency_sec, 2) if cumulative_latency_sec > 0 else 0.0
        effective_tps = round(total_tokens / wall_clock_seconds, 2) if wall_clock_seconds > 0 else 0.0
        degradation_ratio = round(1.0 - (effective_tps / theoretical_tps), 4) if theoretical_tps > 0 else 0.0

        failure_ratio = round(failures / total_attempts, 4)
        overflow_ratio = round(overflows / total_network_calls, 4) if total_network_calls else 0.0

        # SOTA FIX: Verificación de Gobernanza Operacional (SLOs)
        violations = []
        if failure_ratio > self.slo_config.max_translation_failure_ratio:
            violations.append(SLOViolation("translation_failure_ratio", self.slo_config.max_translation_failure_ratio, failure_ratio))
        if overflow_ratio > self.slo_config.max_context_overflow_ratio:
            violations.append(SLOViolation("context_overflow_ratio", self.slo_config.max_context_overflow_ratio, overflow_ratio))
        if p95_wait_ms > self.slo_config.max_p95_quota_wait_ms:
            violations.append(SLOViolation("p95_quota_wait_ms", self.slo_config.max_p95_quota_wait_ms, p95_wait_ms))
        if effective_tps < self.slo_config.min_effective_tps:
            violations.append(SLOViolation("effective_tps", self.slo_config.min_effective_tps, effective_tps))

        return ProductionHealthReport(
            execution_id=execution_id,
            total_chunks_processed=int(total_attempts),
            cache_hit_ratio=round(cache_hits / (total_attempts + cache_hits), 4),
            circuit_breaker_trips=cb_trips,
            context_overflow_ratio=overflow_ratio,
            provider_selection_ratio=provider_selection_ratio,
            translation_failure_ratio=failure_ratio,
            p95_quota_wait_ms=p95_wait_ms,
            effective_tps=effective_tps,
            theoretical_tps=theoretical_tps,
            throughput_degradation_ratio=degradation_ratio,
            slo_violations=violations,
            is_healthy=len(violations) == 0
        )