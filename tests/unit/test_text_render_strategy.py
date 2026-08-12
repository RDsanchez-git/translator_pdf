# tests/unit/test_text_render_strategy.py
"""
NADR-06 §5.2 R1-R4: Tests de escapado consciente del contexto.

Verifica que TextRenderStrategy preserva sintaxis matemática intacta
y escapa exclusivamente el texto prosa.
"""
import unittest
from core.compiler.rendering.implementations import TextRenderStrategy, LatexEscaper
from core.compiler.rendering.models import RenderUnit
from core.ast.enums import ContentNodeType


def _render(text: str) -> str:
    """Helper: renderiza texto prosa mediante TextRenderStrategy."""
    unit = RenderUnit(
        node_id="test",
        node_type=ContentNodeType.PARAGRAPH,
        content=text
    )
    return TextRenderStrategy().render(unit)


class TestTextRenderStrategyMathProtection(unittest.TestCase):
    """NADR-06 §5.2 R1: Preservar sintaxis matemática intacta."""

    def test_inline_math_preserved(self):
        """$...$ se preserva intacta."""
        result = _render("The estimator $x_i$ is unbiased.")
        self.assertIn("$x_i$", result)
        self.assertNotIn(r"\$", result)

    def test_inline_math_with_special_chars(self):
        """Math con _ { } ^ dentro de $...$ se preserva."""
        result = _render("Formula $x^2_{ij}$ is correct.")
        self.assertIn("$x^2_{ij}$", result)

    def test_display_math_preserved(self):
        """$$...$$ se preserva intacto."""
        result = _render("Equation: $$E=mc^2$$")
        self.assertIn("$$E=mc^2$$", result)

    def test_escaped_dollar_inside_math(self):
        r"""$ escapado dentro de math se preserva."""
        result = _render(r"Equation $a\$b$ is valid.")
        self.assertIn(r"$a\$b$", result)


class TestTextRenderStrategyProseEscaping(unittest.TestCase):
    """NADR-06 §5.2 R2: Escapar texto prosa fuera de math."""

    def test_plain_text_escaped(self):
        """Prosa sin math: chars reservados se escapan."""
        result = _render("Cost: 10% & tax")
        self.assertIn(r"\%", result)
        self.assertIn(r"\&", result)

    def test_backslash_in_prose_escaped(self):
        r"""Backslash en prosa se escapa."""
        result = _render(r"Path: C:\Users\docs")
        self.assertIn(r"\textbackslash{}", result)

    def test_underscore_in_prose_escaped(self):
        """Underscore en prosa se escapa."""
        result = _render("file_name is important")
        self.assertIn(r"\_", result)

    def test_braces_in_prose_escaped(self):
        """Braces en prosa se escapan."""
        result = _render("{sample} text")
        self.assertIn(r"\{", result)
        self.assertIn(r"\}", result)


class TestTextRenderStrategyMixedContent(unittest.TestCase):
    """NADR-06 §5.2 R3: Sin sustitución ciega en regiones protegidas."""

    def test_mixed_prose_and_math(self):
        """Prosa se escapa, math se preserva en el mismo texto."""
        result = _render("The value $x$ is 50% of total.")
        self.assertIn("$x$", result)
        self.assertIn(r"\%", result)

    def test_multiple_math_regions(self):
        """Múltiples regiones math se preservan."""
        result = _render("From $a$ to $b$ with 10% cost.")
        self.assertIn("$a$", result)
        self.assertIn("$b$", result)
        self.assertIn(r"\%", result)

    def test_mixed_inline_and_display_math(self):
        """Inline y display math coexisten con prosa escapada."""
        result = _render("The value $x$ and\n$$E=mc^2$$\nwith 5% error.")
        self.assertIn("$x$", result)
        self.assertIn("$$E=mc^2$$", result)
        self.assertIn(r"\%", result)


class TestTextRenderStrategyEdgeCases(unittest.TestCase):
    """Casos límite del contrato."""

    def test_empty_content(self):
        """Contenido vacío retorna string vacío."""
        self.assertEqual(_render(""), "")

    def test_only_math(self):
        """Texto que es solo math no se escapa."""
        result = _render("$x_i$")
        self.assertIn("$x_i$", result)
        self.assertNotIn(r"\$", result)

    def test_deterministic_output(self):
        """NADR-06 §5.2 R4: Mismo input produce mismo output."""
        text = "The $x_i$ value & 50% of total."
        self.assertEqual(_render(text), _render(text))

    def test_no_double_escaping_in_single_pass(self):
        """
        Verifica que una sola ejecución de render no produce doble escape.

        NOTA: Esto NO es una prueba de idempotencia (render(render(x)) == render(x)).
        TextRenderStrategy no garantiza idempotencia sobre texto ya escapado.
        Solo verifica que en una pasada no se escape dos veces.
        """
        text = "Value & tax"
        first = _render(text)
        self.assertIn(r"\&", first)
        self.assertNotIn(r"\\&", first)


class TestLatexEscaperRaw(unittest.TestCase):
    """Tests del componente LatexEscaper puro (sin contexto)."""

    def test_all_reserved_chars_escaped(self):
        """
        Documenta explícitamente el contrato de escape de LatexEscaper.
        Cada char reservado produce su secuencia de escape esperada.
        """
        text = r"\~^&%$#_{}"
        result = LatexEscaper.escape(text)
        self.assertIn(r"\textbackslash{}", result)
        self.assertIn(r"\textasciitilde{}", result)
        self.assertIn(r"\textasciicircum{}", result)
        self.assertIn(r"\&", result)
        self.assertIn(r"\%", result)
        self.assertIn(r"\$", result)
        self.assertIn(r"\#", result)
        self.assertIn(r"\_", result)
        self.assertIn(r"\{", result)
        self.assertIn(r"\}", result)

    def test_empty_string(self):
        self.assertEqual(LatexEscaper.escape(""), "")

    def test_no_math_context(self):
        """LatexEscaper escapa $ sin contexto (comportamiento esperado)."""
        result = LatexEscaper.escape("$x$")
        self.assertIn(r"\$", result)