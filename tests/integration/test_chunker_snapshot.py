import os
import json
import logging
import unittest
from core.ast.models import ASTNode, ContentNodeType, StructuralNodeType, FastWordEstimator
from core.ast.hashing import SemanticChunker, ChunkPolicy

logger = logging.getLogger(__name__)

class TestChunkerSnapshot(unittest.TestCase):
    """Suite de Integración para detectar mutaciones colaterales en el empaquetado de producción."""

    def setUp(self):
        self.estimator = FastWordEstimator()
        self.chunker = SemanticChunker(estimator=self.estimator, policy=ChunkPolicy())
        self.ast_cache_path = "tests/fixtures/sample_3_pages.pdf.ast.json"
        self.snapshot_path = "tests/fixtures/sample_chunks.json"

    def test_snapshot_verification(self):
        """10B.2.9: Compara el estado actual del empaquetador contra el baseline congelado."""
        if not os.path.exists(self.ast_cache_path):
            self.skipTest("Caché del AST no disponible. Se requiere ejecutar el pipeline base primero.")

        with open(self.ast_cache_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            real_ast = [
                ASTNode(
                    node_id=d["node_id"],
                    sequence_id=d["sequence_id"],
                    type=StructuralNodeType(d["type"]) if d["type"] in [e.value for e in StructuralNodeType] else ContentNodeType(d["type"]),
                    content=d["content"],
                    metadata=d.get("metadata", {})
                )
                for d in raw_data
            ]

        production_units = self.chunker.chunk_document(real_ast)
        
        actual_snapshot = [
            {
                "chunk_index": u.chunk_index,
                "chunk_id": u.chunk_id,
                "chunk_type": u.chunk_type,
                "source_sequence_range": list(u.source_sequence_range), # Tupla a Lista para JSON
                "node_count": u.node_count,
                "reference_context": u.reference_context,
                "target_payload": u.target_payload,
                "estimated_tokens": u.estimated_tokens,
                "payload_sha256": u.payload_sha256
            }
            for u in production_units
        ]

        # Modo Generación: Solo crea el snapshot si no existe
        if not os.path.exists(self.snapshot_path):
            with open(self.snapshot_path, "w", encoding="utf-8") as f:
                json.dump(actual_snapshot, f, indent=2, ensure_ascii=False)
            logger.info("Baseline Snapshot generado. Ejecutar test nuevamente para verificar.")
            return

        # Modo Verificación: Falla estrictamente ante regresiones
        with open(self.snapshot_path, "r", encoding="utf-8") as f:
            expected_snapshot = json.load(f)

        self.assertEqual(len(actual_snapshot), len(expected_snapshot), "Regresión: Cambio en la longitud total de unidades.")

        for actual, expected in zip(actual_snapshot, expected_snapshot):
            self.assertEqual(actual["chunk_id"], expected["chunk_id"], f"Regresión de ID en chunk {actual['chunk_index']}.")
            self.assertEqual(actual["payload_sha256"], expected["payload_sha256"], f"Regresión criptográfica en chunk {actual['chunk_index']}.")
            self.assertEqual(actual["target_payload"], expected["target_payload"], f"Regresión de Payload en chunk {actual['chunk_index']}.")
            self.assertEqual(actual["reference_context"], expected["reference_context"], f"Regresión de Sliding Window en chunk {actual['chunk_index']}.")