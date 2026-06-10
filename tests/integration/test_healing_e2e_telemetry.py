# tests/integration/test_healing_e2e_telemetry.py
"""Suite de integración E2E, Rollback Transaccional y Auditoría de Telemetría (11E.6.5)."""

import pytest
from core.validation.models import ValidationContext, ValidationResult, Scope, Severity
from core.healing.models import HealingContext, HealingOutcome
from core.healing.telemetry import HealingTelemetryRegistry
from core.healing.pipeline import HealingPipeline
from core.healing.strategies.markdown_leakage import MarkdownLeakageHealingStrategy
from core.healing.strategies.structural import EOFBraceClosureStrategy, EOFMathClosureStrategy
from core.validation.pipeline import ValidationPipeline

class MockValidationPipeline(ValidationPipeline):
    """Mock heredado de la clase base para cumplir con el análisis estático de dependencias."""
    def __init__(self, fail_revalidation: bool = False) -> None:
        super().__init__()
        self.fail_revalidation = fail_revalidation

    def validate_chunk(self, context: ValidationContext) -> list[ValidationResult]:
        if self.fail_revalidation and "Corrupto" in context.target_text:
            return [
                ValidationResult(
                    invariant_id="MOCK_FAIL",
                    passed=False,
                    severity=Severity.HARD_FAIL,
                    message="Fail",
                    context=context,
                    invariant_family="SI-01"
                )
            ]
        return []

@pytest.fixture
def build_pipeline_and_registry():
    def _builder(fail_revalidation: bool = False):
        val_pipeline = MockValidationPipeline(fail_revalidation)
        strategies = [
            MarkdownLeakageHealingStrategy(),
            EOFBraceClosureStrategy(),
            EOFMathClosureStrategy()
        ]
        registry = HealingTelemetryRegistry()
        pipeline = HealingPipeline(val_pipeline, strategies, registry)
        return pipeline, registry
    return _builder

def _make_ctx(text: str, family: str) -> HealingContext:
    val_ctx = ValidationContext(source_text="source", target_text=text, scope=Scope.CHUNK)
    val_res = ValidationResult(
        invariant_id="ID",
        passed=False,
        severity=Severity.HARD_FAIL,
        message="Msg",
        context=val_ctx,
        invariant_family=family
    )
    return HealingContext(validation_context=val_ctx, validation_result=val_res)

def test_e2e_case_a_markdown_leakage(build_pipeline_and_registry):
    pipeline, registry = build_pipeline_and_registry()
    ctx = _make_ctx("```latex\n\\section{A}\n```", "PeI-01")
    
    res = pipeline.heal_and_revalidate(ctx)
    
    assert res.outcome == HealingOutcome.SUCCESS
    assert res.healed_text == "\\section{A}"
    assert registry.get_events()[0].outcome == "SUCCESS"

def test_e2e_case_b_unbalanced_braces(build_pipeline_and_registry):
    pipeline, registry = build_pipeline_and_registry()
    ctx = _make_ctx("\\textbf{Texto", "SI-01")
    
    res = pipeline.heal_and_revalidate(ctx)
    
    assert res.outcome == HealingOutcome.SUCCESS
    assert res.healed_text == "\\textbf{Texto}"
    assert registry.get_events()[0].strategy_id == "EOFBraceClosureStrategy"

def test_e2e_case_c_math_truncation(build_pipeline_and_registry):
    pipeline, registry = build_pipeline_and_registry()
    ctx = _make_ctx("$$ x $", "SI-02")
    
    res = pipeline.heal_and_revalidate(ctx)
    
    assert res.outcome == HealingOutcome.SUCCESS
    assert res.healed_text == "$$ x $$"

def test_e2e_rollback_guarantee_on_revalidation_failure(build_pipeline_and_registry):
    pipeline, registry = build_pipeline_and_registry(fail_revalidation=True)
    original_corrupt_text = "\\textbf{Corrupto"
    ctx = _make_ctx(original_corrupt_text, "SI-01")
    
    res = pipeline.heal_and_revalidate(ctx)
    
    assert res.outcome == HealingOutcome.FAILURE
    assert res.healed_text is None
    assert res.original_text == original_corrupt_text
    
    event = registry.get_events()[0]
    assert event.outcome == "ROLLBACK"

def test_e2e_telemetry_aggregate_metrics(build_pipeline_and_registry):
    pipeline, registry = build_pipeline_and_registry(fail_revalidation=True)
    
    pipeline.heal_and_revalidate(_make_ctx("\\textbf{Sano", "SI-01"))
    pipeline.heal_and_revalidate(_make_ctx("\\textbf{Corrupto", "SI-01"))
    
    metrics = registry.get_aggregate_metrics()
    stats = metrics["EOFBraceClosureStrategy"]
    
    assert stats["total_invocations"] == 2
    assert stats["success_rate"] == 0.5
    assert stats["rollback_rate"] == 0.5
    assert stats["failure_rate"] == 0.0