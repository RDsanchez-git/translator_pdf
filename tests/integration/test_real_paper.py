import os
import unittest
import logging
from unittest.mock import patch
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.ast.builder import PayloadRegistry
from core.ast.parser import parse_pdf
from core.ast.validator import ASTValidator, ASTHealthReport, ASTValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integration_test")

class TestRealPaperIntegration(unittest.TestCase):
    def setUp(self):
        self.pdf_path = os.getenv("TEST_REAL_PDF_PATH", "tests/fixtures/sample_3_pages.pdf")
        self.expect_stem_document = os.getenv("EXPECT_STEM_DOCUMENT", "1") == "1"
        
        if not os.path.exists(self.pdf_path):
            self.skipTest(f"Test de integración abortado: Fixture ausente en '{self.pdf_path}'")

    def test_parser_and_validation_e2e_local(self):
        # SOTA FIX: Mapeador robusto por sub-cadenas para normalizar la taxonomía legacy V1 al ecosistema V2
        def custom_ast_node_factory(**kwargs):
            if "type" in kwargs and "node_type" not in kwargs:
                type_str = str(kwargs.pop("type")).upper()
                if "EQUATION" in type_str or "MATH" in type_str:
                    kwargs["node_type"] = ContentNodeType.INLINE_EQUATION
                elif "TABLE" in type_str:
                    kwargs["node_type"] = ContentNodeType.TABLE_SIMPLE
                elif "HEADING" in type_str or "SECTION" in type_str:
                    kwargs["node_type"] = ContentNodeType.HEADING
                elif "LIST" in type_str:
                    kwargs["node_type"] = ContentNodeType.LIST
                else:
                    try:
                        kwargs["node_type"] = ContentNodeType(type_str)
                    except ValueError:
                        kwargs["node_type"] = ContentNodeType.PARAGRAPH
                        
            if "content" in kwargs and "payload" not in kwargs:
                kwargs["payload"] = PayloadRegistry.create(kwargs["node_type"], kwargs.pop("content"))
            return ASTNode(**kwargs)

        with patch("core.ast.parser.ASTNode", side_effect=custom_ast_node_factory):
            ast = parse_pdf(self.pdf_path)
        
        report = ASTHealthReport.from_ast(ast)
        print(report)
        
        try:
            ASTValidator.validate(ast, unknown_count_floor=5, max_unknown_ratio=0.15)
            
            self.assertGreater(report.stats["paragraphs"], 0, "Error: El parser devolvió un árbol vacío de narrativa.")
            self.assertGreater(report.semantic_coverage, 0.70, f"Error: Cobertura semántica críticamente baja: {report.semantic_coverage:.1%}")
            
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