import sys
import os
import unittest
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.normalization.latex_sanitizer import InlineMathProtector
from core.ast.enums import ContentNodeType

class TestPipelineFidelity(unittest.TestCase):

    # =========================================================================
    # CAPA 1: SANITIZACIÓN E INVARIANZA MATEMÁTICA (LaTeX & HTML)
    # =========================================================================

    def test_semantic_adjacency_and_mutations(self):
        """Validar adyacencia estricta mediante regex y tolerar mutaciones del LLM."""
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
        """Garantizar que la regex ignora bloques $$ y solo captura inline $."""
        original = "The value $x$ is computed from\n$$\nx = y+z\n$$\nand $z$."
        masked, mapping = InlineMathProtector.mask(original)
        
        self.assertEqual(len(mapping), 2)
        self.assertIn("__MATH_0__", masked)
        self.assertIn("__MATH_1__", masked)
        self.assertIn("$$\nx = y+z\n$$", masked)
        
        restored = InlineMathProtector.restore(masked, mapping)
        self.assertEqual(original, restored)

    # =========================================================================
    # CAPA 2: BLINDAJE DE COSTOS EN ENUM (Worker)
    # =========================================================================

    def test_worker_passthrough_alignment(self):
        """Validar la existencia de las variantes estructurales clave del Enum Semántico."""
        required_passthrough_types = ("INLINE_EQUATION", "DISPLAY_EQUATION", "IMAGE", "TABLE_SIMPLE")
        for type_name in required_passthrough_types:
            self.assertTrue(hasattr(ContentNodeType, type_name), f"Variante ausente en ContentNodeType Enum: {type_name}")

if __name__ == "__main__":
    unittest.main()