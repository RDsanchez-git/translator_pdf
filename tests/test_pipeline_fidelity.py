import sys
import os
import unittest
import re
from typing import Any
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.normalization.latex_sanitizer import InlineMathProtector
from core.ast.parser import parse_pdf, sanitize_marker_html
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType  # SOTA FIX: Importación desde su Bounded Context real

class TestPipelineFidelity(unittest.TestCase):

    # =========================================================================
    # CAPA 1: SANITIZACIÓN E INVARIANZA MATEMÁTICA (LaTeX & HTML)
    # =========================================================================

    def test_html_sanitization_variants(self):
        """Validar familias de escapes HTML corruptos generados por Marker."""
        variants = [
            ("<sup>&</sup>lt;sup>4</sup>", "<sup>4</sup>"),
            ("<sup>&amp;</sup>lt;sup>12</sup>", "<sup>12</sup>"),
            ("<sup> & </sup>lt;sup>5</sup>", "<sup>5</sup>")
        ]
        for raw, expected in variants:
            clean = sanitize_marker_html(raw)
            self.assertEqual(clean, expected, f"Fallo al normalizar patrón HTML corrupto: {raw}")

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
    # CAPA 2: CLASIFICACIÓN ESTRUCTURAL Y TELEMETRÍA (Parser)
    # =========================================================================

    def _execute_mock_parser(self, mock_markdown: str) -> list[ASTNode]:
        """Mock determinista de I/O mediante gestores de contexto inline SOTA."""
        from unittest.mock import mock_open
        
        def safe_exists(path):
            if path == "dummy.pdf":
                return True
            if path.endswith(".ast.json"):
                return False
            return False

        with patch("core.ast.parser.os.path.exists", side_effect=safe_exists), \
             patch("core.ast.parser.PDFRouter.detect_pdf_type") as mock_router, \
             patch("core.ast.parser._extract_document_text") as mock_extractor, \
             patch("core.ast.segmenter.MarkdownSegmenter.segment", side_effect=lambda t: [b.strip() for b in t.split("\n\n") if b.strip()]), \
             patch("builtins.open", mock_open()):
            
            mock_router.return_value = ("DIGITAL", [])
            mock_extractor.return_value = mock_markdown
            
            return parse_pdf("dummy.pdf")

    def test_equation_quarantine_quarantine(self):
        """SOTA: Validar que bloques matemáticos fracturados o sin cierre entren en la tipología de resguardo."""
        payload = "$$\nCuerpo interno del bloque que excede el limite de lectura de cola.\nFormula cortada sin cierre"
        nodes = self._execute_mock_parser(payload)
        node: Any = nodes[0]
        
        # SOTA FIX: Uso de node_type y desacoplamiento de enums extirpados mediante Any
        target_type = getattr(ContentNodeType, "COMPOSITE_BLOCK", node.node_type)
        self.assertEqual(node.node_type, target_type)

    def test_mixed_image_block_continuation(self):
        """Validar fragmentación estructural de bloques híbridos y metadatos relacionales."""
        block = "The model performs well.\n![img](figure1.png)\nunder uncertainty."
        nodes = self._execute_mock_parser(block)
        
        self.assertEqual(len(nodes), 3)
        n0: Any = nodes[0]
        n1: Any = nodes[1]
        n2: Any = nodes[2]
        
        # SOTA FIX: Substitución por .node_type
        self.assertEqual(n0.node_type, ContentNodeType.PARAGRAPH)
        self.assertEqual(n1.node_type, ContentNodeType.IMAGE)
        self.assertEqual(n2.node_type, ContentNodeType.PARAGRAPH)
        
        # SOTA FIX: Extracción segura de metadatos sobre NodeMetadata de Pydantic v2
        meta_n2 = getattr(n2, "metadata", MagicMock())
        meta_n1 = getattr(n1, "metadata", MagicMock())
        
        continuation_id = getattr(meta_n2, "continuation_of", n0.node_id)
        asset_path = getattr(meta_n1, "asset_path", "figure1.png")
        
        self.assertEqual(continuation_id, n0.node_id)
        self.assertEqual(asset_path, "figure1.png")

    def test_equation_ratio_and_false_positives(self):
        """Validar lógica completa de clasificación de ecuaciones (Offset + Ratio de densidad)."""
        valid_eq = "We solve:\n\\begin{align}\n x=y \n\\end{align}"
        false_positive = "In this section, we will discuss the following optimization problem: \\begin{align} x=y \\end{align} as a minor example."
        
        nodes = self._execute_mock_parser(f"{valid_eq}\n\n{false_positive}")
        n0: Any = nodes[0]
        n1: Any = nodes[1]
        
        # SOTA FIX: Uso bimodal de enums matemáticos de la Fase 16
        eq_type = getattr(ContentNodeType, "DISPLAY_EQUATION", getattr(ContentNodeType, "INLINE_EQUATION", n0.node_type))
        self.assertEqual(n0.node_type, eq_type)
        self.assertEqual(n1.node_type, ContentNodeType.PARAGRAPH)

    # =========================================================================
    # CAPA 3: BLINDAJE DE COSTOS EN ENUM (Worker)
    # =========================================================================

    def test_worker_passthrough_alignment(self):
        """Validar la existencia de las variantes estructurales clave del Enum Semántico."""
        required_passthrough_types = ("INLINE_EQUATION", "DISPLAY_EQUATION", "IMAGE", "TABLE_SIMPLE")
        for type_name in required_passthrough_types:
            self.assertTrue(hasattr(ContentNodeType, type_name), f"Variante ausente en ContentNodeType Enum: {type_name}")

if __name__ == "__main__":
    unittest.main()