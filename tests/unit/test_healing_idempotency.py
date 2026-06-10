# tests/unit/test_healing_idempotency.py
"""Verificación formal de contratos, idempotencia estricta y garantías de no-degradación (11E.6.3-R3)."""

from core.validation.models import ValidationContext, ValidationResult, Severity
from core.validation.pipeline import ValidationPipeline  # Importación requerida para subtipado nominal
from core.healing.models import HealingOutcome
from core.healing.pipeline import HealingPipeline
from core.healing.strategies.markdown_leakage import MarkdownLeakageHealingStrategy
from core.healing.strategies.meta_text_leakage import MetaTextLeakageHealingStrategy
from core.healing.testing_factories import make_test_healing_context

class MockValidationPipelineWithResidualFail(ValidationPipeline):
    """Stub nominal para simular regresiones sintácticas post-curación."""
    def validate_chunk(self, context: ValidationContext) -> list[ValidationResult]:
        return [
            ValidationResult(
                invariant_id="UNBALANCED_BRACES_OPEN",
                invariant_family="SI-01",
                passed=False,
                severity=Severity.HARD_FAIL,
                message="La curación introdujo una llave huérfana de LaTeX.",
                context=context
            )
        ]

class MockValidationPipelinePass(ValidationPipeline):
    """Stub nominal reactivo para certificar revalidaciones limpias."""
    def validate_chunk(self, context: ValidationContext) -> list[ValidationResult]:
        return []

def test_markdown_healing_is_idempotent():
    strategy = MarkdownLeakageHealingStrategy()
    corrupt_text = "```latex\n\\section{Title}\n```"
    
    # Pasada 1: SUCCESS
    ctx_1 = make_test_healing_context(corrupt_text, "PeI-01", "MARKDOWN_LEAK")
    res_1 = strategy.heal(ctx_1)
    assert res_1.outcome == HealingOutcome.SUCCESS
    assert res_1.healed_text == "\\section{Title}"
    
    # Pasada 2: NOT_APPLICABLE (Idempotencia Léxica)
    ctx_2 = make_test_healing_context(res_1.final_text, "PeI-01", "MARKDOWN_LEAK")
    res_2 = strategy.heal(ctx_2)
    assert res_2.outcome == HealingOutcome.NOT_APPLICABLE
    assert res_2.healed_text is None

def test_metatext_healing_is_idempotent():
    strategy = MetaTextLeakageHealingStrategy()
    corrupt_text = "Sure, here is the translation:\n\\section{Title}"
    
    # Pasada 1: SUCCESS
    ctx_1 = make_test_healing_context(corrupt_text, "PeI-02", "CONVERSATIONAL_PREFIX")
    res_1 = strategy.heal(ctx_1)
    assert res_1.outcome == HealingOutcome.SUCCESS
    assert res_1.healed_text == "\\section{Title}"
    
    # Pasada 2: NOT_APPLICABLE
    ctx_2 = make_test_healing_context(res_1.final_text, "PeI-02", "CONVERSATIONAL_PREFIX")
    res_2 = strategy.heal(ctx_2)
    assert res_2.outcome == HealingOutcome.NOT_APPLICABLE
    assert res_2.healed_text is None

def test_healing_idempotency_not_applicable_chain():
    """Garantiza estabilidad inmutable sobre estados ya limpios (NOT_APPLICABLE -> NOT_APPLICABLE)."""
    strategy = MarkdownLeakageHealingStrategy()
    clean_text = "\\section{Pure LaTex}"
    
    ctx_1 = make_test_healing_context(clean_text, "PeI-01", "MARKDOWN_LEAK")
    res_1 = strategy.heal(ctx_1)
    assert res_1.outcome == HealingOutcome.NOT_APPLICABLE
    
    ctx_2 = make_test_healing_context(clean_text, "PeI-01", "MARKDOWN_LEAK")
    res_2 = strategy.heal(ctx_2)
    assert res_2.outcome == HealingOutcome.NOT_APPLICABLE

def test_healing_edge_case_payload_vacio_returns_failure():
    """Bloquea mutaciones degenerativas que vacíen el fragmento."""
    strategy = MarkdownLeakageHealingStrategy()
    empty_block = "```latex\n\n```"
    
    ctx_1 = make_test_healing_context(empty_block, "PeI-01", "MARKDOWN_LEAK")
    res_1 = strategy.heal(ctx_1)
    assert res_1.outcome == HealingOutcome.FAILURE
    assert res_1.healed_text is None

def test_healing_pipeline_enforces_rollback_on_residual_hard_fail():
    """Certifica el contrato central de No-Degradación: Rollback total ante fallos remanentes."""
    mock_failing_validator = MockValidationPipelineWithResidualFail()
    strategy = MarkdownLeakageHealingStrategy()
    
    # Ensamblado del pipeline con inyección de validador hostil
    pipeline = HealingPipeline(validation_pipeline=mock_failing_validator, strategies=[strategy])
    
    # Payload que se limpia del perímetro pero contiene errores estructurales internos en LaTeX
    corrupt_text = "```latex\n\\section{Title{\n```"
    ctx = make_test_healing_context(corrupt_text, "PeI-01", "MARKDOWN_LEAK")
    
    result = pipeline.heal_and_revalidate(ctx)
    
    # Verificación de Contrato Transaccional de una pasada
    assert result.outcome == HealingOutcome.FAILURE
    assert "Revalidation failed after healing" in result.message
    # Exigencia SOTA: El final_text debe contener el string corrupto original con backticks (Rollback)
    assert result.final_text == corrupt_text