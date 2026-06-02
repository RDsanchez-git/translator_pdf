import os
import unittest
import logging
from core.ast.parser import parse_pdf
from core.ast.validator import ASTValidator, ASTHealthReport, ASTValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integration_test")

class TestRealPaperIntegration(unittest.TestCase):
    def setUp(self):
        self.pdf_path = os.getenv("TEST_REAL_PDF_PATH", "tests/fixtures/sample_3_pages.pdf")
        # Problema 4: Control condicional configurable para la aserción de bloques STEM
        self.expect_stem_document = os.getenv("EXPECT_STEM_DOCUMENT", "1") == "1"
        
        if not os.path.exists(self.pdf_path):
            self.skipTest(f"Test de integración abortado: Fixture ausente en '{self.pdf_path}'")

    def test_parser_and_validation_e2e_local(self):
        # Ingesta física real local (Marker + FSM) sin mocks
        ast = parse_pdf(self.pdf_path)
        
        # Generación e impresión del reporte desacoplado
        report = ASTHealthReport.from_ast(ast)
        print(report)
        
        try:
            # Validación contractual
            ASTValidator.validate(ast, unknown_count_floor=5, max_unknown_ratio=0.15)
            
            # Garantías de Recall Semántico Mínimo
            self.assertGreater(report.stats["paragraphs"], 0, "Error: El parser devolvió un árbol vacío de narrativa.")
            self.assertGreater(report.semantic_coverage, 0.70, f"Error: Cobertura semántica críticamente baja: {report.semantic_coverage:.1%}")
            
            # Aserción STEM Condicional Inteligente
            if self.expect_stem_document:
                total_stem_nodes = report.stats["equations"] + report.stats["tables"] + report.stats["images"]
                self.assertGreater(
                    total_stem_nodes, 0, 
                    "Falla de Recall Estructural: El documento está configurado como STEM "
                    "pero el pipeline local omitió o clasificó incorrectamente las ecuaciones/gráficos."
                )
            else:
                logger.info("[INTEGRATION] Skip assert STEM: El documento está indexado como no-científico/teórico.")
            
        except ASTValidationError as e:
            self.fail(f"El PDF real rompió el contrato de control de calidad del AST: {e}")

if __name__ == "__main__":
    unittest.main()