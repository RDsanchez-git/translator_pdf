# tests/unit/test_math_domain_normalizer.py

import pytest

from core.normalization.fixers.math_pipeline import MathDomainNormalizer


@pytest.fixture
def normalizer():
    return MathDomainNormalizer()


# ==========================================================
# REGIONES PROTEGIDAS
# ==========================================================

def test_verbatim_environment_is_immune(normalizer):
    text = r"""
\begin{verbatim}
\begin{equation}
x = 1
\end{equation}
\end{verbatim}
"""

    result = normalizer.normalize(text)

    assert result.text == text
    assert not any(
        "LATEX_TOPOLOGY" in w.message
        for w in result.warnings
    )


def test_nested_verbatim_immunity(normalizer):
    text = r"""
\begin{verbatim}
\verb|\begin{equation}|
\end{verbatim}
"""

    result = normalizer.normalize(text)

    assert result.text == text
    assert len(result.warnings) == 0


def test_verb_with_dynamic_delimiter(normalizer):
    text = r"\verb|\begin{equation}|"

    result = normalizer.normalize(text)

    assert result.text == text


def test_lstinline_preserved(normalizer):
    text = r"\lstinline|x+1|"

    result = normalizer.normalize(text)

    assert result.text == text


def test_mintinline_preserved(normalizer):
    text = r"\mintinline{python}{x=1}"

    result = normalizer.normalize(text)

    assert result.text == text


def test_mintinline_with_options(normalizer):
    text = r"\mintinline[breaklines]{python}{x=1}"

    result = normalizer.normalize(text)

    assert result.text == text


# ==========================================================
# HTML -> LATEX
# ==========================================================

def test_html_sup_conversion(normalizer):
    text = "x<sup>2</sup>"

    result = normalizer.normalize(text)

    assert result.text == "x^{2}"


def test_html_sub_conversion(normalizer):
    text = "H<sub>2</sub>O"

    result = normalizer.normalize(text)

    assert result.text == "H_{2}O"


def test_html_double_wrap_protection(normalizer):
    text = "x^<sup>2</sup>"

    result = normalizer.normalize(text)

    assert result.text == "x^2"


# ==========================================================
# DELIMITADORES MATEMÁTICOS
# ==========================================================

def test_balanced_inline_math(normalizer):
    text = "$x+y$"

    result = normalizer.normalize(text)

    severe = [
        w for w in result.warnings
        if w.severity == "SEVERE"
    ]

    assert len(severe) == 0


def test_unbalanced_inline_math_detection(normalizer):
    text = "$x+y"

    result = normalizer.normalize(text)

    assert any(
        "Unbalanced mathematical delimiters"
        in w.message
        for w in result.warnings
    )


def test_balanced_display_math(normalizer):
    text = "$$x+y$$"

    result = normalizer.normalize(text)

    severe = [
        w for w in result.warnings
        if w.severity == "SEVERE"
    ]

    assert len(severe) == 0


# ==========================================================
# TOPOLOGÍA LATEX
# ==========================================================

def test_unclosed_environment_detection(normalizer):
    text = r"""
\begin{equation}
x=1
"""

    result = normalizer.normalize(text)

    assert any(
        "Unclosed environments"
        in w.message
        for w in result.warnings
    )


def test_environment_mismatch_detection(normalizer):
    text = r"""
\begin{equation}
x=1
\end{align}
"""

    result = normalizer.normalize(text)

    assert any(
        "Mismatch"
        in w.message
        for w in result.warnings
    )


def test_orphaned_end_detection(normalizer):
    text = r"\end{equation}"

    result = normalizer.normalize(text)

    assert any(
        "Orphaned"
        in w.message
        for w in result.warnings
    )


# ==========================================================
# DELIMITADORES DEPRECADOS
# ==========================================================

def test_inline_deprecated_conversion(normalizer):
    text = r"\(x+y\)"

    result = normalizer.normalize(text)

    assert result.text == "$x+y$"


def test_display_deprecated_conversion(normalizer):
    text = r"\[x+y\]"

    result = normalizer.normalize(text)

    assert result.text == "$$x+y$$"


# ==========================================================
# IDEMPOTENCIA FUERTE
# ==========================================================

def test_multiple_pass_idempotency(normalizer):

    original = r"""
\begin{align}
x<sup>2</sup> &= y \\
z &= \mintinline{python}{a+b}
\end{align}
"""

    r1 = normalizer.normalize(original)
    r2 = normalizer.normalize(r1.text)
    r3 = normalizer.normalize(r2.text)

    assert r1.text == r2.text
    assert r2.text == r3.text


# ==========================================================
# ROBUSTEZ
# ==========================================================

def test_empty_input(normalizer):
    result = normalizer.normalize("")

    assert result.text == ""


def test_whitespace_input(normalizer):
    result = normalizer.normalize("   ")

    assert result.text == "   "


def test_protected_region_roundtrip(normalizer):
    text = r"""
\begin{verbatim}
foo bar baz
\end{verbatim}
"""

    result = normalizer.normalize(text)

    assert result.text == text


# ==========================================================
# VALIDACIÓN SOTA DE SEVERIDAD Y TELEMETRÍA
# ==========================================================

def test_strict_warning_severity_and_telemetry(normalizer):
    """Verifica el tipado estructurado de las alertas y el registro de métricas."""
    # CORRECCIÓN: Inyección de un dólar huérfano dentro de $$ para disparar la alerta de colisión
    text = r"""
    \begin{align}
    x = 1
    $$ y = 2 $ z $$
    """
    result = normalizer.normalize(text)
    
    # 1. Validar que la telemetría registró el entorno amsmath
    assert "env_align:1" in result.fixes
    
    # 2. Validar que el FSM detectó la colisión y asignó severidad estricta
    severe_warnings = [w for w in result.warnings if w.severity == "SEVERE"]
    assert len(severe_warnings) > 0
    assert any("Collision" in w.message for w in severe_warnings)


def test_illegal_recursive_nesting_detection(normalizer):
    """Garantiza el bloqueo topológico de entornos no anidables consigo mismos."""
    text = r"""
\begin{equation}
\begin{equation}
x = 1
\end{equation}
\end{equation}
"""
    result = normalizer.normalize(text)
    
    severe_nesting = [w for w in result.warnings if w.severity == "SEVERE"]
    assert any("ILLEGAL_NESTING" in w.message for w in severe_nesting)


def test_complex_environment_arguments_parsing(normalizer):
    """Verifica que los entornos con argumentos numéricos o de formato no rompan la pila."""
    text = r"""
\begin{alignedat}{2}
A  &= B  &  C &= D \\
E  &= F  &  G &= H
\end{alignedat}
"""
    result = normalizer.normalize(text)
    
    # La pila debe balancear correctamente ignorando los argumentos {2}
    assert "env_alignedat:1" in result.fixes
    assert not any(w.severity == "SEVERE" for w in result.warnings)


def test_escaped_dollar_immunity_in_fsm(normalizer):
    r"""Valida que los dólares escapados (\$) sean puenteados por el autómata de estados."""
    text = r"El costo de la ecuación es \$500 y cumple que $x + y = 1$."
    result = normalizer.normalize(text)
    
    # El FSM no debe confundir \$500 con una apertura de inline math
    assert not any(w.severity == "SEVERE" for w in result.warnings)

def test_verbatim_masking(normalizer):
    """Verifica que los bloques \verb no interfieran con la validación de entornos."""
    text = r"Some text \verb|\begin{matrix}| and then real math \begin{equation} x=1 \end{equation}"
    result = normalizer.normalize(text)
    
    # El lexer debió aislar el falso entorno, por lo que no hay errores topológicos
    assert not any("LATEX_TOPOLOGY" in w.message for w in result.warnings)
    assert r"\verb|\begin{matrix}|" in result.text
    assert "env_equation:1" in result.fixes

def test_inequalities_not_removed(normalizer):
    """Asegura que las inecuaciones no se confundan con HTML por culpa del Fast-Path."""
    text = r"x < abc > y and a <= b"
    result = normalizer.normalize(text)
    
    assert "html_safe_unwrap" not in result.fixes
    assert "<" in result.text
    assert ">" in result.text


def test_math_delimiter_automaton(normalizer):
    """Prueba el autómata de estados finitos puro para delimitadores $/$$."""
    # 1. Estructura Balanceada
    result_1 = normalizer.normalize(r"$$ x + y $$")
    assert len(result_1.warnings) == 0

    # 2. Desbalance display/inline
    result_2 = normalizer.normalize(r"$$ x + y $")
    assert any("Unbalanced mathematical delimiters" in w.message for w in result_2.warnings)
    assert any(w.severity == "SEVERE" for w in result_2.warnings)

    # 3. Colisión de contexto (Inline dentro de Display)
    result_3 = normalizer.normalize(r"$$ x $ y $$")
    assert any("Collision" in w.message for w in result_3.warnings)

    # 4. Inmunidad ante caracteres de escape
    result_4 = normalizer.normalize(r"$$ x + \$y $$")
    assert len([w for w in result_4.warnings if w.severity == "SEVERE"]) == 0

def test_illegal_nesting_detection(normalizer):
    """Detecta colisiones jerárquicas recursivas de entornos no anidables."""
    text = r"\begin{equation}\begin{equation}x=1\end{equation}\end{equation}"
    result = normalizer.normalize(text)
    
    assert any("ILLEGAL_NESTING" in w.message for w in result.warnings)
    assert any(w.severity == "SEVERE" for w in result.warnings)


def test_idempotency_preserve_contract(normalizer):
    """Garantiza la estabilidad del texto. Las firmas se recalculan pero el texto se congela."""
    original = r"\begin{align}A &= B\\ C &= D\end{align}"
    
    first = normalizer.normalize(original)
    second = normalizer.normalize(first.text)
    
    # El texto debe ser exactamente idéntico entre pasadas
    assert first.text == second.text
    # Las métricas se mantienen estables porque el entorno sigue existiendo en el texto
    assert first.fixes == second.fixes