import os
import unittest
import logging
import pytest
from core.ast.validator import ASTValidator, ASTHealthReport, ASTValidationError
from apps.bootstrap.pipeline_factory import build_extraction_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integration_test")

@pytest.mark.e2e
class TestRealPaperIntegration(unittest.TestCase):
    """Opt-in real-paper fidelity witness; not a representable-PDF smoke.

    A real document can correctly fail B02 on unsupported vector drawings.
    Do not convert it into a technical PASS with a synthetic substitute: that
    positive extraction path is already covered by the PR #50 integration test.
    """

    def setUp(self):
        self.pdf_path = os.getenv("TEST_REAL_PDF_PATH", "")
        if not self.pdf_path:
            self.fail(
                "REAL_PAPER_INPUT_REQUIRED: set TEST_REAL_PDF_PATH explicitly "
                "to a PDF whose capabilities you intend to validate, then run "
                "python -m pytest -m e2e tests/integration/test_real_paper.py"
            )
        if not os.path.isfile(self.pdf_path):
            self.fail(f"REAL_PAPER_INPUT_MISSING: {self.pdf_path}")

    def test_parser_and_validation_e2e_local(self):
        """Verifica que el pipeline de extracción de producción produce un AST válido."""
        parser = build_extraction_pipeline()
        ast = parser.parse(self.pdf_path)
        
        report = ASTHealthReport.from_ast(ast)
        print(report)
        
        try:
            ASTValidator.validate(ast, unknown_count_floor=5, max_unknown_ratio=0.15)
            
            # Validación semántica (narrativa) — aplicable a todos los providers
            self.assertGreater(
                report.stats["paragraphs"], 0, 
                "Error: El parser devolvió un árbol vacío de narrativa."
            )
            self.assertGreater(
                report.semantic_coverage, 0.70, 
                f"Error: Cobertura semántica críticamente baja: {report.semantic_coverage:.1%}"
            )
            
            # Validación estructural STEM — condicionada al contrato del pipeline
            # El test verifica el contrato del pipeline, no la implementación del proveedor.
            capabilities = parser.capabilities
            if capabilities.supports_math or capabilities.has_tables or capabilities.has_images:
                total_stem_nodes = (
                    report.stats["equations"] + 
                    report.stats["tables"] + 
                    report.stats["images"]
                )
                self.assertGreater(
                    total_stem_nodes, 0,
                    "Falla de Recall Estructural: El pipeline declara capacidades STEM "
                    f"(supports_math={capabilities.supports_math}, "
                    f"has_tables={capabilities.has_tables}, "
                    f"has_images={capabilities.has_images}) "
                    "pero no produjo nodos de ecuaciones, tablas o imágenes."
                )
            else:
                logger.info(
                    "[INTEGRATION] El pipeline actual no declara capacidades STEM. "
                    f"supports_math={capabilities.supports_math}, "
                    f"has_tables={capabilities.has_tables}, "
                    f"has_images={capabilities.has_images}. "
                    "Saltando aserción de recall estructural."
                )
            
        except ASTValidationError as e:
            self.fail(f"El PDF real rompió el contrato de control de calidad del AST: {e}")

if __name__ == "__main__":
    unittest.main()