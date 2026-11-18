"""B-04: technical LaTeX mask/restore and enum contracts (historical filename).

The checks protect exact mathematical placeholders and a small set of AST
content types; they do NOT establish linguistic/scientific or PDF-to-PDF fidelity.
No import-time sys.path mutation is necessary with the repository test runner.
"""
import unittest
import re

from core.normalization.latex_sanitizer import InlineMathProtector
from core.ast.enums import ContentNodeType

class TestMathProtectionContracts(unittest.TestCase):
    """Historical tests of mathematical adjacency, roundtrip and enum presence."""

    # =========================================================================
    # CAPA 1: SANITIZACIÓN E INVARIANZA MATEMÁTICA (LaTeX & HTML)
    # =========================================================================

    def test_math_placeholder_restoration_preserves_adjacency(self):
        """Verify source math adjacency after restoring three placeholder variants."""
        original_text = "The estimator $x_i$ is unbiased."
        masked, mapping = InlineMathProtector.mask(original_text)
        
        llm_mutated_responses = [
            "El estimador __ MATH_0 __ es insesgado.",
            "La asignación para el estimador __math_0__.", 
            "El estimador __ Math _ 0 __ es insesgado."
        ]
        
        for llm_output in llm_mutated_responses:
            restored = InlineMathProtector.restore(llm_output, mapping)
            has_adjacency = bool(re.search(r'estimador\s*(?:[\w,]+\s+){0,1}\$x_i\$', restored.lower()))
            self.assertTrue(has_adjacency, f"Desplazamiento semántico crítico detectado: {restored}")

    def test_mixed_inline_and_block_math(self):
        """B02.4: protect inline AND display math without changing source bytes."""
        original = "The value $x$ is computed from\n$$\nx = y+z\n$$\nand $z$."
        masked, mapping = InlineMathProtector.mask(original)

        self.assertEqual(mapping, {
            "__MATH_0__": "$x$",
            "__MATH_1__": "$$\nx = y+z\n$$",
            "__MATH_2__": "$z$",
        })
        self.assertEqual(masked.count("__MATH_"), 3)
        for explicit_math in mapping.values():
            self.assertNotIn(explicit_math, masked)

        restored = InlineMathProtector.restore(masked, mapping)
        self.assertEqual(original, restored)

    # =========================================================================
    # CAPA 2: BLINDAJE DE COSTOS EN ENUM (Worker)
    # =========================================================================

    def test_worker_passthrough_alignment(self):
        """Only verifies the presence of four AST node-type enum members."""
        required_passthrough_types = ("INLINE_EQUATION", "DISPLAY_EQUATION", "IMAGE", "TABLE_SIMPLE")
        for type_name in required_passthrough_types:
            self.assertTrue(hasattr(ContentNodeType, type_name), f"Variante ausente en ContentNodeType Enum: {type_name}")

if __name__ == "__main__":
    unittest.main()