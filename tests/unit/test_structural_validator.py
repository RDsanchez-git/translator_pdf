# tests/unit/test_structural_validator.py
from core.validation.structural_validator import StructuralValidator

def test_braces_balanced_and_escaped():
    assert StructuralValidator._check_braces("{hello}") is None
    assert StructuralValidator._check_braces(r"escaped \{ and \}") is None

def test_braces_unbalanced():
    err_open = StructuralValidator._check_braces("{hello")
    assert err_open is not None
    assert err_open.code == "UNBALANCED_BRACES_OPEN"

    err_early = StructuralValidator._check_braces("hello}")
    assert err_early is not None
    assert err_early.code == "UNBALANCED_BRACES_EARLY"

def test_brackets_balanced_and_escaped():
    assert StructuralValidator._check_brackets("[hello]") is None
    assert StructuralValidator._check_brackets(r"escaped \[ and \]") is None

def test_brackets_unbalanced():
    err_open = StructuralValidator._check_brackets("[hello")
    assert err_open is not None
    assert err_open.code == "UNBALANCED_BRACKETS_OPEN"

def test_math_delimiters_balanced():
    assert StructuralValidator._check_math_delimiters("$x$") is None
    assert StructuralValidator._check_math_delimiters("$$x$$") is None
    assert StructuralValidator._check_math_delimiters(r"\$") is None

def test_math_delimiters_unbalanced():
    err_inline = StructuralValidator._check_math_delimiters("$x")
    assert err_inline is not None
    assert err_inline.code == "UNBALANCED_INLINE_MATH"

    err_display = StructuralValidator._check_math_delimiters("$$x")
    assert err_display is not None
    assert err_display.code == "UNBALANCED_DISPLAY_MATH"

def test_environments_balanced():
    text = r"\begin{equation}x=1\end{equation}"
    assert StructuralValidator._check_environments(text) is None

def test_environments_unbalanced():
    err_unclosed = StructuralValidator._check_environments(r"\begin{equation}x=1")
    assert err_unclosed is not None
    assert err_unclosed.code == "ENV_UNCLOSED"
    
    err_mismatch = StructuralValidator._check_environments(r"x=1\end{equation}")
    assert err_mismatch is not None
    assert err_mismatch.code == "ENV_MISMATCH"