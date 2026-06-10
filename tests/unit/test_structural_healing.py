# tests/unit/test_structural_healing.py
"""Suite de validación sintáctica de límites, paridad y contratos estructurales (11E.6.4)."""


from core.healing.models import HealingOutcome
from core.healing.config import HealingPolicy
from core.healing.strategies.structural import EOFBraceClosureStrategy, EOFMathClosureStrategy
from core.healing.testing_factories import make_test_healing_context

def test_brace_closure_strategy_success_on_nested_macros():
    strategy = EOFBraceClosureStrategy()
    corrupt_text = "\\section{Introducción \\textbf{Texto abierto"
    ctx = make_test_healing_context(corrupt_text, "SI-01", "UNBALANCED_BRACES")
    
    res = strategy.heal(ctx)
    assert res.outcome == HealingOutcome.SUCCESS
    assert res.healed_text == "\\section{Introducción \\textbf{Texto abierto}}"
    assert res.changes_count == 1

def test_verb_does_not_consume_neighboring_braces():
    """Certifica límites estrictos del regex de verb sin degradar caracteres contiguos."""
    strategy = EOFBraceClosureStrategy()
    
    text_a = r"\verb|{| Texto {"
    ctx_a = make_test_healing_context(text_a, "SI-01", "UNBALANCED_BRACES")
    res_a = strategy.heal(ctx_a)
    assert res_a.outcome == HealingOutcome.SUCCESS
    assert res_a.healed_text == r"\verb|{| Texto {}"
    
    text_b = r"\verb|{|{"
    ctx_b = make_test_healing_context(text_b, "SI-01", "UNBALANCED_BRACES")
    res_b = strategy.heal(ctx_b)
    assert res_b.outcome == HealingOutcome.SUCCESS
    # Corrección de la aserción manual errónea
    assert res_b.healed_text == r"\verb|{|{}"

def test_brace_closure_ignores_escaped_braces():
    """Certifica que las llaves escapadas con backslash no alteran la cuenta estructural."""
    strategy = EOFBraceClosureStrategy()
    text = r"\{ texto elástico {"
    ctx = make_test_healing_context(text, "SI-01", "UNBALANCED_BRACES")
    
    res = strategy.heal(ctx)
    assert res.outcome == HealingOutcome.SUCCESS
    assert res.healed_text == r"\{ texto elástico {}"

def test_brace_closure_bounds_trigger_failure_from_policy():
    policy = HealingPolicy(max_autofix_braces=2)
    strategy = EOFBraceClosureStrategy(policy=policy)
    massive_corruption = "Texto {" * 3
    ctx = make_test_healing_context(massive_corruption, "SI-01", "UNBALANCED_BRACES")
    
    res = strategy.heal(ctx)
    assert res.outcome == HealingOutcome.FAILURE
    assert res.healed_text is None

def test_brace_closure_not_applicable():
    strategy = EOFBraceClosureStrategy()
    balanced_text = "\\section{Title} \\textbf{text}"
    ctx = make_test_healing_context(balanced_text, "SI-01", "UNBALANCED_BRACES")
    
    res = strategy.heal(ctx)
    assert res.outcome == HealingOutcome.NOT_APPLICABLE

def test_math_closure_strategy_inline_success():
    strategy = EOFMathClosureStrategy()
    corrupt_text = "Sea la ecuación $E = mc^2"
    ctx = make_test_healing_context(corrupt_text, "SI-02", "UNBALANCED_MATH")
    
    res = strategy.heal(ctx)
    assert res.outcome == HealingOutcome.SUCCESS
    assert res.healed_text == "Sea la ecuación $E = mc^2$"

def test_math_closure_strategy_display_success():
    strategy = EOFMathClosureStrategy()
    corrupt_text = "Texto $$\n\\int x dx"
    ctx = make_test_healing_context(corrupt_text, "SI-02", "UNBALANCED_MATH")
    
    res = strategy.heal(ctx)
    assert res.outcome == HealingOutcome.SUCCESS
    assert res.healed_text == "Texto $$\n\\int x dx$$"

def test_math_closure_strategy_handles_truncated_display_state():
    """Certifica el control de DISPLAY_TRUNCATED preservando saltos de línea originales."""
    strategy = EOFMathClosureStrategy()
    truncated_display = "Texto $$\n\\int_0^1 x dx\n$"
    ctx = make_test_healing_context(truncated_display, "SI-02", "UNBALANCED_MATH")
    
    res = strategy.heal(ctx)
    assert res.outcome == HealingOutcome.SUCCESS
    assert res.healed_text == "Texto $$\n\\int_0^1 x dx\n$$"
    assert res.changes_count == 1

def test_math_closure_not_applicable():
    strategy = EOFMathClosureStrategy()
    balanced_math = "Texto $x=y$ continuo $$a=b$$ sin quiebres."
    ctx = make_test_healing_context(balanced_math, "SI-02", "UNBALANCED_MATH")
    
    res = strategy.heal(ctx)
    assert res.outcome == HealingOutcome.NOT_APPLICABLE