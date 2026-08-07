"""
Verifica el modelo transaccional de healing multi-fallo.

NADR-07 §5.1 R1-R3: Colección completa de fallos.
NADR-07 §5.2 R4-R5: Rollback atómico.
NADR-07 §5.3 R7-R9: Revalidación única.
NADR-07 §5.4 R10-R12: Detección de anomalías.
"""

from typing import List

from core.validation.models import ValidationContext, ValidationResult, Severity, Scope
from core.validation.pipeline import ValidationPipeline
from core.healing.pipeline import HealingPipeline
from core.healing.models import HealingOutcome, HealingContext
from core.healing.base import BaseHealingStrategy


class MockStrategyA(BaseHealingStrategy):
    """Estrategia que corrige el texto."""
    def __init__(self):
        self._family = "SI-01"
        self._priority = 10

    @property
    def invariant_family(self) -> str:
        return self._family

    @property
    def priority(self) -> int:
        return self._priority

    def heal(self, context: HealingContext):
        from core.healing.models import HealingResult
        healed = context.validation_context.target_text.replace("{broken", "{fixed")
        return HealingResult(
            invariant_family=self._family,
            strategy_id="MockStrategyA",
            outcome=HealingOutcome.SUCCESS,
            original_text=context.validation_context.target_text,
            healed_text=healed,
            message="Fixed braces",
            changes_count=1,
        )


class MockStrategyB(BaseHealingStrategy):
    """Estrategia que rompe el texto (introduce nuevo fallo)."""
    def __init__(self):
        self._family = "SI-02"
        self._priority = 20

    @property
    def invariant_family(self) -> str:
        return self._family

    @property
    def priority(self) -> int:
        return self._priority

    def heal(self, context: HealingContext):
        from core.healing.models import HealingResult
        healed = context.validation_context.target_text.replace("$$", "$")
        return HealingResult(
            invariant_family=self._family,
            strategy_id="MockStrategyB",
            outcome=HealingOutcome.SUCCESS,
            original_text=context.validation_context.target_text,
            healed_text=healed,
            message="Broke math",
            changes_count=1,
        )


class MockValidationPipelineFailAfterHeal(ValidationPipeline):
    """Pipeline de validación que falla después del healing.
    
    Simula que MockStrategyB rompió el display math original:
    el texto original tenía $$...$$ y el texto curado tiene $...$
    (display math degradado a inline math = fallo estructural).
    """
    def validate_chunk(self, context: ValidationContext) -> List[ValidationResult]:
        # Si el texto fue curado por StrategyA ("fixed") y StrategyB eliminó
        # los delimitadores de display math ($$), emitir HARD_FAIL.
        if "fixed" in context.target_text and "$$" not in context.target_text:
            return [ValidationResult(
                invariant_id="SI-02",
                passed=False,
                severity=Severity.HARD_FAIL,
                message="Display math degraded to inline math after healing",
                context=context,
                invariant_family="SI-02",
            )]
        return []


class MockValidationPipelinePass(ValidationPipeline):
    """Pipeline de validación que siempre pasa."""
    def validate_chunk(self, context: ValidationContext) -> List[ValidationResult]:
        return []


def _make_ctx(text: str) -> ValidationContext:
    return ValidationContext(
        source_text="source",
        target_text=text,
        scope=Scope.CHUNK,
        chunk_index=1,
        chunk_type="TRANSLATE",
        payload_sha256="sha_test",
    )


def test_multi_heal_success():
    """3 hard fails → 2 estrategias → éxito → texto curado."""
    validation_pipeline = MockValidationPipelinePass()
    strategies: List[BaseHealingStrategy] = [MockStrategyA(), MockStrategyB()]
    healing = HealingPipeline(validation_pipeline, strategies)

    ctx = _make_ctx("{broken text with $$math$$")
    failures = [
        ValidationResult(
            invariant_id="SI-01", passed=False, severity=Severity.HARD_FAIL,
            message="Unbalanced braces", context=ctx, invariant_family="SI-01",
        ),
        ValidationResult(
            invariant_id="SI-02", passed=False, severity=Severity.HARD_FAIL,
            message="Unbalanced math", context=ctx, invariant_family="SI-02",
        ),
    ]

    result = healing.heal_all_and_revalidate(ctx, failures)

    assert result.outcome == HealingOutcome.SUCCESS
    assert result.healed_text is not None
    assert "{fixed" in result.healed_text


def test_multi_heal_rollback_preserves_original():
    """3 hard fails → 2 estrategias → rollback → texto original intacto."""
    validation_pipeline = MockValidationPipelineFailAfterHeal()
    strategies: List[BaseHealingStrategy] = [MockStrategyA(), MockStrategyB()]
    healing = HealingPipeline(validation_pipeline, strategies)

    original_text = "{broken text with $$math$$"
    ctx = _make_ctx(original_text)
    failures = [
        ValidationResult(
            invariant_id="SI-01", passed=False, severity=Severity.HARD_FAIL,
            message="Unbalanced braces", context=ctx, invariant_family="SI-01",
        ),
        ValidationResult(
            invariant_id="SI-02", passed=False, severity=Severity.HARD_FAIL,
            message="Unbalanced math", context=ctx, invariant_family="SI-02",
        ),
    ]

    result = healing.heal_all_and_revalidate(ctx, failures)

    assert result.outcome == HealingOutcome.FAILURE
    assert result.original_text == original_text


def test_multi_heal_deduplicates_strategies():
    """Dos fallos de la misma familia → una sola ejecución de estrategia."""
    validation_pipeline = MockValidationPipelinePass()
    strategies: List[BaseHealingStrategy] = [MockStrategyA()]
    healing = HealingPipeline(validation_pipeline, strategies)

    ctx = _make_ctx("{broken {broken")
    failures = [
        ValidationResult(
            invariant_id="SI-01a", passed=False, severity=Severity.HARD_FAIL,
            message="Fail 1", context=ctx, invariant_family="SI-01",
        ),
        ValidationResult(
            invariant_id="SI-01b", passed=False, severity=Severity.HARD_FAIL,
            message="Fail 2", context=ctx, invariant_family="SI-01",
        ),
    ]

    result = healing.heal_all_and_revalidate(ctx, failures)

    assert result.outcome == HealingOutcome.SUCCESS
    assert result.strategy_id == "MockStrategyA"
    assert "+" not in result.strategy_id


def test_empty_failures_returns_not_applicable():
    """Sin fallos → NOT_APPLICABLE."""
    validation_pipeline = MockValidationPipelinePass()
    strategies: List[BaseHealingStrategy] = []
    healing = HealingPipeline(validation_pipeline, strategies)

    ctx = _make_ctx("clean text")
    result = healing.heal_all_and_revalidate(ctx, [])

    assert result.outcome == HealingOutcome.NOT_APPLICABLE