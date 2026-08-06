import os
import unittest
import logging
from core.ast.validator import ASTValidator, ASTHealthReport, ASTValidationError
from apps.bootstrap.pipeline_factory import build_extraction_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integration_test")

class TestRealPaperIntegration(unittest.TestCase):
    def setUp(self):
        self.pdf_path = os.getenv("TEST_REAL_PDF_PATH", "tests/fixtures/sample_3_pages.pdf")
        
        if not os.path.exists(self.pdf_path):
            self.skipTest(f"Test de integración abortado: Fixture ausente en '{self.pdf_path}'")

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