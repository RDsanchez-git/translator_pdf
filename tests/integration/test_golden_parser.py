import unittest
import os
import json
from typing import List, Dict, Any
from core.ast.models import ASTNode
from infra.adapters.pdf_parser import PdfParserAdapter
from core.ast.parser import parse_pdf

class TestGoldenParser(unittest.TestCase):
    """SOTA: Suite de regresión estructural basada en huellas digitales topológicas (Fase 11B.1B)."""

    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.fingerprint_path = "tests/golden/sample_3_pages.fingerprint.json"
        self.adapter = PdfParserAdapter(parser_callable=parse_pdf, verify_output=True)

        if not os.path.exists(self.pdf_real_path):
            raise FileNotFoundError(f"Falta el binario fuente: {self.pdf_real_path}")

    def _generate_fingerprint(self, nodes: List[ASTNode]) -> Dict[str, Any]:
        """Calcula las invariantes estructurales libres de identidades o literales."""
        distribution: Dict[str, int] = {}
        sequence: List[Dict[str, Any]] = []

        for node in nodes:
            # Extracción limpia del valor string del Enum 'type' (Pydantic / StrEnum)
            type_str = node.type.value if hasattr(node.type, "value") else str(node.type)
            content_str = node.content or ""
            
            # 1. Registro de macro-distribución
            distribution[type_str] = distribution.get(type_str, 0) + 1
            
            # 2. Registro de secuencia con insensibilidad a espacios laterales
            sequence.append({
                "type": type_str,
                "content_length": len(content_str.strip())
            })

        return {
            "summary": {
                "total_nodes": len(nodes),
                "distribution": distribution
            },
            "sequence": sequence
        }

    def test_parser_runtime_matches_golden_fingerprint(self):
        """Certifica que las mutaciones de código en el segmentador no degraden la estructura del AST."""
        # Si el archivo dorado no existe, el sistema levanta la precondición (Modo Captura)
        if not os.path.exists(self.fingerprint_path):
            self.skipTest(f"Línea de base ausente. Ejecute el script de captura primero en: {self.fingerprint_path}")

        # 1. Extracción física real
        current_nodes = self.adapter.parse(self.pdf_real_path)
        current_fingerprint = self._generate_fingerprint(current_nodes)

        # 2. Carga del molde inmutable
        with open(self.fingerprint_path, "r", encoding="utf-8") as f:
            expected_fingerprint = json.load(f)

        # 3. Verificación de Macro-Métricas (Volumetría Global)
        self.assertEqual(
            current_fingerprint["summary"]["total_nodes"],
            expected_fingerprint["summary"]["total_nodes"],
            "Regresión Crítica: La cantidad total de bloques lógicos extraídos cambió."
        )

        # 4. Verificación de Distribución de Componentes (Evita pérdida silenciosa de tablas/ecuaciones)
        self.assertEqual(
            current_fingerprint["summary"]["distribution"],
            expected_fingerprint["summary"]["distribution"],
            "Regresión Semántica: La mezcla distributiva de tipos de nodos divergió del molde."
        )

        # 5. Verificación Micro-Secuencial (Orden jerárquico y densidad de datos aproximada)
        for idx, current_item in enumerate(current_fingerprint["sequence"]):
            expected_item = expected_fingerprint["sequence"][idx]
            
            self.assertEqual(
                current_item["type"],
                expected_item["type"],
                f"Asimetría de orden en el índice {idx}: Se detectó '{current_item['type']}' "
                f"pero se esperaba '{expected_item['type']}'."
            )
            
            # Tolerancia por Delta Relativo: Previene roturas por cambios ínfimos de sanitización
            delta = abs(current_item["content_length"] - expected_item["content_length"])
            self.assertLessEqual(
                delta, 
                5, 
                f"Mutación de densidad en nodo índice {idx} ({current_item['type']}): "
                f"El tamaño de caracteres varió significativamente (Delta: {delta} chars)."
            )