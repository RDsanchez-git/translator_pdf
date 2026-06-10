# core/healing/telemetry.py
"""Registro estructurado y thread-safe con agregación O(1) de telemetría transaccional."""

import logging
import threading
from collections import deque
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class HealingEvent:
    strategy_id: str
    invariant_family: str
    outcome: str  # 'SUCCESS', 'FAILURE', 'ROLLBACK', 'NOT_APPLICABLE'
    latency_ms: float
    changes_count: int
    # SOTA: Auditoría de Rollback (Problema D)
    failed_invariants: Optional[List[str]] = None
    rollback_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

class HealingTelemetryRegistry:
    def __init__(self, max_size: int = 10000):
        self._events = deque(maxlen=max_size)
        self._lock = threading.Lock()
        # SOTA: Agregación incremental O(1) para evitar snapshots caros (Problema B)
        self._aggregates: Dict[str, Dict[str, float]] = {}

    def record(self, event: HealingEvent) -> None:
        """Persiste el evento y actualiza los contadores agregados en O(1) de forma segura."""
        with self._lock:
            self._events.append(event)
            self._update_aggregates_unlocked(event)
            
        logger.info("healing_event", extra={"telemetry_event": event.to_dict()})

    def _update_aggregates_unlocked(self, event: HealingEvent) -> None:
        strat = event.strategy_id
        if strat not in self._aggregates:
            self._aggregates[strat] = {"total": 0, "SUCCESS": 0, "FAILURE": 0, "ROLLBACK": 0, "latency_sum": 0.0}
        
        self._aggregates[strat]["total"] += 1
        self._aggregates[strat]["latency_sum"] += event.latency_ms
        if event.outcome in ("SUCCESS", "FAILURE", "ROLLBACK"):
            self._aggregates[strat][event.outcome] += 1

    def get_aggregate_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Retorna las tasas calculadas directamente desde los contadores incrementales."""
        with self._lock:
            snapshot = {k: v.copy() for k, v in self._aggregates.items()}

        metrics = {}
        for strat, data in snapshot.items():
            total = data["total"]
            metrics[strat] = {
                "success_rate": round(data["SUCCESS"] / total, 4) if total else 0.0,
                "failure_rate": round(data["FAILURE"] / total, 4) if total else 0.0,
                "rollback_rate": round(data["ROLLBACK"] / total, 4) if total else 0.0,
                "avg_latency_ms": round(data["latency_sum"] / total, 3) if total else 0.0,
                "total_invocations": int(total)
            }
        return metrics

    def get_events(self) -> List[HealingEvent]:
        with self._lock:
            return list(self._events)