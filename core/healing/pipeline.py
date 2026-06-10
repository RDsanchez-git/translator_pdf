# core/healing/pipeline.py
"""
core/healing/pipeline.py
Orquestador determinista de curación transaccional en una sola pasada con tipado estricto y telemetría de latencia.
"""

import logging
import time
from typing import List, Dict, Optional, TYPE_CHECKING
from core.healing.models import HealingContext, HealingResult, HealingOutcome
from core.healing.telemetry import HealingTelemetryRegistry, HealingEvent

if TYPE_CHECKING:
    from core.validation.pipeline import ValidationPipeline

from core.healing.base import BaseHealingStrategy

logger = logging.getLogger(__name__)

class HealingPipeline:
    """
    Motor de orquestación de resiliencia.
    Estrategia cerrada: Evalúa, repara y revalida en un único paso atómico con auditoría integrada.
    """

    def __init__(
        self, 
        validation_pipeline: "ValidationPipeline", 
        strategies: List[BaseHealingStrategy],
        registry: Optional[HealingTelemetryRegistry] = None
    ):
        """
        Inyección por constructor para garantizar la inmutabilidad del estado.
        Usa string literal hint para evadir dependencias circulares en runtime.
        """
        self._validation_pipeline = validation_pipeline
        self._telemetry_registry = registry or HealingTelemetryRegistry()
        
        # Ordenamiento determinista por prioridad para resolver colisiones latentes
        sorted_strategies = sorted(strategies, key=lambda x: x.priority)
        
        # Mapeo O(1) inmutable del registro de estrategias
        self._registry: Dict[str, BaseHealingStrategy] = {
            strat.invariant_family: strat for strat in sorted_strategies
        }

    def heal_and_revalidate(self, context: HealingContext) -> HealingResult:
        """
        Punto de entrada único del ciclo de resiliencia.
        Aplica la curación y exige de forma mandatoria la ausencia de HARD_FAIL.
        """
        # SOTA: Type narrowing defensivo. Evita que un None interrumpa el mapping O(1)
        family = context.validation_result.invariant_family or "UNKNOWN"
        strategy = self._registry.get(family)

        # Caso 1: El invariante no pertenece al catálogo de reparabilidad automatizada
        if not strategy:
            result = HealingResult(
                invariant_family=family,
                strategy_id="NONE",
                outcome=HealingOutcome.NOT_APPLICABLE,
                original_text=context.validation_context.target_text,
                message=f"No healing strategy registered for family '{family}'"
            )
            self._telemetry_registry.record(HealingEvent(
                strategy_id="NONE",
                invariant_family=family,
                outcome=HealingOutcome.NOT_APPLICABLE.name,
                latency_ms=0.0,
                changes_count=0
            ))
            return result

        strat_id = getattr(strategy, "strategy_id", strategy.__class__.__name__)
        # SOTA: El cronómetro abarca toda la transacción, incluyendo revalidación (Problema E)
        start_time = time.perf_counter()

        try:
            strategy_result = strategy.heal(context)
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"HEALING_CRASH: La estrategia '{strat_id}' falló internamente: {str(e)}")
            
            result = HealingResult(
                invariant_family=family,
                strategy_id=strat_id,
                outcome=HealingOutcome.FAILURE,
                original_text=context.validation_context.target_text,
                message=f"Runtime exception in strategy execution: {str(e)}"
            )
            self._telemetry_registry.record(HealingEvent(
                strategy_id=strat_id,
                invariant_family=family,
                outcome="FAILURE",
                latency_ms=round(latency_ms, 3),
                changes_count=0,
                rollback_reason="Strategy Crash"
            ))
            return result

        if strategy_result.outcome != HealingOutcome.SUCCESS or strategy_result.healed_text is None:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            self._telemetry_registry.record(HealingEvent(
                strategy_id=strat_id,
                invariant_family=family,
                outcome=strategy_result.outcome.name,
                latency_ms=round(latency_ms, 3),
                changes_count=strategy_result.changes_count
            ))
            return strategy_result

        # Revalidación Estricta
        from dataclasses import replace
        new_ctx = replace(context.validation_context, target_text=strategy_result.healed_text)
        validation_results = self._validation_pipeline.validate_chunk(new_ctx)
        active_hard_fails = [r for r in validation_results if r.severity.name == "HARD_FAIL"]

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        if active_hard_fails:
            # SOTA: Extracción formal de invariantes fallidos para auditoría (Problema D)
            failed_invariants_list = [f.invariant_id for f in active_hard_fails]
            failures_summary = ", ".join(failed_invariants_list)
            
            logger.warning(f"HEALING_REJECTED: Rollback aplicado. Errores: {failures_summary}")
            
            result = HealingResult(
                invariant_family=family,
                strategy_id=strat_id,
                outcome=HealingOutcome.FAILURE,
                original_text=context.validation_context.target_text,
                message=f"Revalidation failed. Errors: {failures_summary}"
            )
            
            self._telemetry_registry.record(HealingEvent(
                strategy_id=strat_id,
                invariant_family=family,
                outcome="ROLLBACK",
                latency_ms=round(latency_ms, 3),
                changes_count=strategy_result.changes_count,
                failed_invariants=failed_invariants_list,
                rollback_reason="Revalidation Hard Fail"
            ))
            return result

        # Éxito verificado
        self._telemetry_registry.record(HealingEvent(
            strategy_id=strat_id,
            invariant_family=family,
            outcome="SUCCESS",
            latency_ms=round(latency_ms, 3),
            changes_count=strategy_result.changes_count
        ))
        return strategy_result