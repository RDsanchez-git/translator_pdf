# tests/integration/test_healing_concurrency.py
"""Suite de certificación de Async-Safety, estrés concurrente y auditoría transaccional sin dependencias de plugins."""

import asyncio
from core.validation.models import ValidationContext, ValidationResult, Scope, Severity
from core.healing.models import HealingContext, HealingOutcome
from core.healing.telemetry import HealingTelemetryRegistry, HealingEvent
from core.healing.pipeline import HealingPipeline
from core.healing.strategies.structural import EOFBraceClosureStrategy
from core.validation.pipeline import ValidationPipeline

def test_telemetry_registry_async_concurrency():
    """Certifica que el acumulador incremental O(1) soporta la concurrencia nativa del event loop."""
    # SOTA: Inyección de capacidad extendida exclusiva para el volumen del benchmark de estrés
    registry = HealingTelemetryRegistry(max_size=60000)
    num_tasks = 100
    events_per_task = 500
    total_expected = num_tasks * events_per_task

    async def _async_worker(task_id: int):
        for i in range(events_per_task):
            base_latency = 1.0 if (i % 2 == 0) else 2.0
            event = HealingEvent(
                strategy_id="AsyncStressStrategy",
                invariant_family="PeI-01",
                outcome="SUCCESS" if (i % 2 == 0) else "ROLLBACK",
                latency_ms=base_latency,
                changes_count=1
            )
            registry.record(event)
            await asyncio.sleep(0)

    async def _main_orchestrator():
        tasks = [_async_worker(t) for t in range(num_tasks)]
        await asyncio.gather(*tasks)

    asyncio.run(_main_orchestrator())

    events = registry.get_events()
    assert len(events) == total_expected

    metrics = registry.get_aggregate_metrics()
    stats = metrics["AsyncStressStrategy"]
    
    assert stats["total_invocations"] == total_expected
    assert stats["success_rate"] == 0.5
    assert stats["rollback_rate"] == 0.5
    assert stats["avg_latency_ms"] == 1.5


class ContextDrivenMockValidationPipeline(ValidationPipeline):
    """Mock determinista heredado de la clase base para satisfacer el tipado estricto."""
    
    def __init__(self) -> None:
        super().__init__()

    def validate_chunk(self, context: ValidationContext) -> list[ValidationResult]:
        if context.extra.get("force_rollback") is True:
            return [
                ValidationResult(
                    invariant_id="UNBALANCED_BRACES",
                    passed=False,
                    severity=Severity.HARD_FAIL,
                    message="Unclosed {",
                    context=context,
                    invariant_family="SI-01"
                )
            ]
        return []


def test_healing_pipeline_emits_full_audit_on_rollback():
    """Certifica la emisión de latencia transaccional y metadatos explícitos de auditoría."""
    val_pipeline = ContextDrivenMockValidationPipeline()
    registry = HealingTelemetryRegistry()
    pipeline = HealingPipeline(val_pipeline, [EOFBraceClosureStrategy()], registry)
    
    metadata = {"force_rollback": True}
    val_ctx = ValidationContext(
        source_text="source", 
        target_text="\\textbf{Texto de prueba", 
        scope=Scope.CHUNK, 
        extra=metadata
    )
    
    val_res = ValidationResult(
        invariant_id="UNBALANCED_BRACES",
        passed=False,
        severity=Severity.HARD_FAIL,
        message="Msg",
        context=val_ctx,
        invariant_family="SI-01"
    )
    ctx = HealingContext(val_ctx, val_res)
    
    # Operación puramente síncrona ejecutada de forma directa
    res = pipeline.heal_and_revalidate(ctx)
    
    assert res.outcome == HealingOutcome.FAILURE
    
    events = registry.get_events()
    assert len(events) == 1
    rollback_event = events[0]
    
    assert rollback_event.outcome == "ROLLBACK"
    assert "UNBALANCED_BRACES" in (rollback_event.failed_invariants or [])
    assert rollback_event.rollback_reason == "Revalidation Hard Fail"
    assert rollback_event.latency_ms > 0.0