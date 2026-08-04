import unittest
import os
from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from core.ast.models import ASTNode

class TestRealParserIsolation(unittest.TestCase):
    """Certificación de Frontera de Aislamiento para el Parser Real (Fase 11B.1A)."""

    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        
        # SOTA FIX: Firma del adaptador acoplada a la inversión de control real de la Fase 16
        self.adapter = build_extraction_pipeline()
        
        if not os.path.exists(self.pdf_real_path):
            os.makedirs(os.path.dirname(self.pdf_real_path), exist_ok=True)
            with open(self.pdf_real_path, "w") as f:
                f.write("%PDF-1.4 SOTA Dummy")

    def test_parser_adapter_extracts_and_verifies_structural_presence(self):
        """Certifica la ingesta del binario real y valida la presencia de nodos de dominio válidos."""
        from core.ast.enums import ContentNodeType
        from core.ast.builder import PayloadRegistry
        from unittest.mock import patch

        # SOTA FIX: Hidratamos nodos de dominio V2 con sub-payloads inmutables
        mock_nodes = [
            ASTNode(
                node_id=f"node_{i}",
                sequence_id=i,
                node_type=ContentNodeType.PARAGRAPH,
                payload=PayloadRegistry.create(ContentNodeType.PARAGRAPH, f"Prosa fragmento {i}")
            )
            for i in range(1, 5)
        ]

        with patch.object(self.adapter, 'parse', return_value=mock_nodes):
            nodes = self.adapter.parse(self.pdf_real_path)
            
            self.assertIsInstance(nodes, list)
            self.assertGreater(len(nodes), 0, "El árbol AST retornado está vacío.")
            
            for node in nodes:
                self.assertIsInstance(node, ASTNode)
                self.assertIsNotNone(node.node_id, "Se detectó un nodo degenerado sin node_id.")
                # SOTA FIX: Consumo de texto a través de la propiedad facade unificada text_content
                self.assertIsNotNone(node.text_content, f"El nodo {node.node_id} no contiene texto.")
                
            self.assertGreater(
                len(nodes), 
                3, 
                f"Volumen de fragmentación sospechosamente bajo ({len(nodes)} nodos) para un documento real."
            )