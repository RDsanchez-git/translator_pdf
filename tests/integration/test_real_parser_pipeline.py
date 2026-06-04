import unittest
import os
from infra.adapters.pdf_parser import PdfParserAdapter
from core.ast.models import ASTNode
from core.ast.parser import parse_pdf  # Inyección permitida exclusivamente en la raíz de composición del test

class TestRealParserIsolation(unittest.TestCase):
    """Certificación de Frontera de Aislamiento para el Parser Real (Fase 11B.1A)."""

    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.adapter = PdfParserAdapter(parser_callable=parse_pdf, verify_output=True)
        
        if not os.path.exists(self.pdf_real_path):
            raise FileNotFoundError(f"Fixture binario crítico ausente en la ruta: {self.pdf_real_path}")

    def test_parser_adapter_extracts_and_verifies_structural_presence(self):
        """Certifica la ingesta del binario real y valida la presencia de nodos de dominio válidos."""
        nodes = self.adapter.parse(self.pdf_real_path)
        
        # Validación del contrato de estructura de datos
        self.assertIsInstance(nodes, list)
        self.assertGreater(len(nodes), 0, "El árbol AST retornado está vacío.")
        
        # Validación de integridad de identidad y texto (Sin tocar atributos de tipo)
        for node in nodes:
            self.assertIsInstance(node, ASTNode)
            self.assertIsNotNone(node.node_id, "Se detectó un nodo degenerado sin node_id.")
            self.assertIsNotNone(node.content, f"El nodo {node.node_id} no contiene texto.")
            
        # Sanity check de volumen físico para el documento de 3 páginas
        self.assertGreater(
            len(nodes), 
            3, 
            f"Volumen de fragmentación sospechosamente bajo ({len(nodes)} nodos) para un documento real."
        )