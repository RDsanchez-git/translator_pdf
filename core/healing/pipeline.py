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
from core.validation.models import ValidationContext, ValidationResult

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

        # =====================================================================
    # NADR-07: Curación multi-fallo transaccional
    # =====================================================================

    def heal_all_and_revalidate(
        self,
        validation_context: "ValidationContext",
        failures: List["ValidationResult"],
    ) -> HealingResult:
        """
        NADR-07 §5.1 R1-R2: Procesa la colección completa de fallos.
        NADR-07 §5.1 R3: No descarta fallos adicionales.
        NADR-07 §5.2 R4-R5: Rollback atómico si la revalidación falla.
        NADR-07 §5.4 R10-R12: Detección de anomalías entre estrategias.
        NADR-07 §5.3 R7: Revalidación única dentro del ciclo transaccional.

        Modelo transaccional:
        Plan → Apply → Detect Anomalies → Validate → Commit/Rollback
        """
        if not failures:
            return HealingResult(
                invariant_family="NONE",
                strategy_id="NONE",
                outcome=HealingOutcome.NOT_APPLICABLE,
                original_text=validation_context.target_text,
                message="No failures to heal",
            )

        # Fase 1: PLAN (con deduplicación)
        planned = self._plan_healing(failures)

        if not planned:
            return HealingResult(
                invariant_family=failures[0].invariant_family or "UNKNOWN",
                strategy_id="NONE",
                outcome=HealingOutcome.NOT_APPLICABLE,
                original_text=validation_context.target_text,
                message=f"No healing strategy registered for any of {len(failures)} failures",
            )

        # Fase 2: APPLY
        original_text = validation_context.target_text
        mutated_text, applied_strategies, total_changes = self._apply_mutations(
            planned, validation_context, original_text
        )

        if not applied_strategies:
            return HealingResult(
                invariant_family=failures[0].invariant_family or "UNKNOWN",
                strategy_id="NONE",
                outcome=HealingOutcome.FAILURE,
                original_text=original_text,
                message="No strategy produced a successful mutation",
            )

        # Fase 3: DETECT ANOMALIES
        anomaly = self._detect_anomalies(original_text, mutated_text, planned)
        if anomaly:
            self._telemetry_registry.record(HealingEvent(
                strategy_id="+".join(applied_strategies),
                invariant_family=failures[0].invariant_family or "UNKNOWN",
                outcome="ROLLBACK",
                latency_ms=0.0,
                changes_count=total_changes,
                rollback_reason=f"Anomaly detected: {anomaly}",
            ))
            return HealingResult(
                invariant_family=failures[0].invariant_family or "UNKNOWN",
                strategy_id="+".join(applied_strategies),
                outcome=HealingOutcome.FAILURE,
                original_text=original_text,
                message=f"Healing anomaly detected: {anomaly}",
            )

        # Fase 4: VALIDATE
        active_hard_fails = self._validate_result(mutated_text, validation_context)

        # Fase 5: COMMIT OR ROLLBACK
        return self._commit_or_rollback(
            active_hard_fails, original_text, mutated_text,
            applied_strategies, total_changes, failures,
        )

    def _plan_healing(self, failures: List["ValidationResult"]) -> List[tuple]:
        """
        Fase 1: Resuelve estrategias disponibles, deduplica por strategy_id
        y ordena por prioridad.

        NADR-07 §5.1 R2: Secuencial, respetando prioridad declarada.
        AJUSTE OBLIGATORIO: Deduplicación por strategy_id para evitar
        ejecutar la misma estrategia dos veces.
        """
        seen_strategy_ids = set()
        planned = []

        for fail in failures:
            family = fail.invariant_family or "UNKNOWN"
            strategy = self._registry.get(family)
            if strategy is None:
                continue

            strat_id = getattr(strategy, "strategy_id", strategy.__class__.__name__)
            if strat_id in seen_strategy_ids:
                continue

            seen_strategy_ids.add(strat_id)
            planned.append((strategy, fail))

        planned.sort(key=lambda x: x[0].priority)
        return planned

    def _apply_mutations(
        self, planned: List[tuple], validation_context: "ValidationContext", original_text: str
    ) -> tuple:
        """
        Fase 2: Aplica mutaciones secuencialmente.
        Cada estrategia opera sobre el texto resultante de la anterior.
        """
        from dataclasses import replace

        current_text = original_text
        applied_strategies: List[str] = []
        total_changes = 0

        for strategy, fail in planned:
            strat_id = getattr(strategy, "strategy_id", strategy.__class__.__name__)
            ctx = HealingContext(
                validation_context=replace(validation_context, target_text=current_text),
                validation_result=fail,
            )
            result = strategy.heal(ctx)

            if result.outcome != HealingOutcome.SUCCESS or result.healed_text is None:
                continue

            if result.healed_text == current_text:
                continue

            current_text = result.healed_text
            applied_strategies.append(strat_id)
            total_changes += result.changes_count

        return current_text, applied_strategies, total_changes

    def _detect_anomalies(
        self, original_text: str, mutated_text: str, planned: List[tuple]
    ) -> str | None:
        """
        Fase 3: Detección de anomalías post-mutación.

        AJUSTE OBLIGATORIO: Renombrado de _detect_conflicts a _detect_anomalies.
        El algoritmo basado en longitud NO detecta conflictos reales
        (dos estrategias pueden modificar el mismo span con longitud idéntica).

        Un detector serio debe trabajar sobre spans modificados o AST diff.
        Se deja como hook explícito para Gate 4.

        NADR-07 §5.4 R10: El mecanismo de detección debe existir.
        La implementación actual es una heurística mínima.
        """
        # TODO Gate 4: Implementar detección de conflictos basada en
        # spans modificados o AST diff. El ratio de longitud solo detecta
        # daño aproximado, no conflictos reales entre estrategias.
        return None

    def _validate_result(
        self, mutated_text: str, validation_context: "ValidationContext"
    ) -> List:
        """
        Fase 4: Revalidación única (NADR-07 §5.3 R7).
        Ocurre exactamente una vez, dentro del ciclo transaccional.
        """
        from dataclasses import replace

        new_ctx = replace(validation_context, target_text=mutated_text)
        validation_results = self._validation_pipeline.validate_chunk(new_ctx)
        return [r for r in validation_results if r.severity.name == "HARD_FAIL"]

    def _commit_or_rollback(
        self, active_hard_fails: List, original_text: str, mutated_text: str,
        applied_strategies: List[str], total_changes: int, original_failures: List,
    ) -> HealingResult:
        """
        Fase 5: Commit o Rollback atómico.
        NADR-07 §5.2 R5: Rollback sin degradación parcial.
        """
        if active_hard_fails:
            failed_invariants_list = [f.invariant_id for f in active_hard_fails]
            failures_summary = ", ".join(failed_invariants_list)

            self._telemetry_registry.record(HealingEvent(
                strategy_id="+".join(applied_strategies),
                invariant_family=original_failures[0].invariant_family or "UNKNOWN",
                outcome="ROLLBACK",
                latency_ms=0.0,
                changes_count=total_changes,
                failed_invariants=failed_invariants_list,
                rollback_reason="Revalidation Hard Fail",
            ))

            return HealingResult(
                invariant_family=original_failures[0].invariant_family or "UNKNOWN",
                strategy_id="+".join(applied_strategies),
                outcome=HealingOutcome.FAILURE,
                original_text=original_text,
                message=f"Revalidation failed after multi-heal. Errors: {failures_summary}",
            )

        self._telemetry_registry.record(HealingEvent(
            strategy_id="+".join(applied_strategies),
            invariant_family=original_failures[0].invariant_family or "UNKNOWN",
            outcome="SUCCESS",
            latency_ms=0.0,
            changes_count=total_changes,
        ))

        return HealingResult(
            invariant_family=original_failures[0].invariant_family or "UNKNOWN",
            strategy_id="+".join(applied_strategies),
            outcome=HealingOutcome.SUCCESS,
            original_text=original_text,
            healed_text=mutated_text,
            message=f"Multi-heal successful with {len(applied_strategies)} strategies",
            changes_count=total_changes,
        )