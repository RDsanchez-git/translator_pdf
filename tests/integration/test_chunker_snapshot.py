import os
import json
import logging
import unittest
from core.ast.models import ASTNode, FastWordEstimator
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from apps.bootstrap.pipeline_factory import build_extraction_pipeline

logger = logging.getLogger(__name__)

class TestChunkerSnapshot(unittest.TestCase):
    """Suite de Integración para detectar mutaciones colaterales en el empaquetado de producción."""

    def setUp(self):
        self.adapter = build_extraction_pipeline()
        self.estimator = FastWordEstimator()
        self.ast_cache_path = "tests/fixtures/sample_3_pages.pdf.ast.json"
        self.snapshot_path = "tests/fixtures/sample_chunks.json"

    def test_snapshot_verification(self):
        """10B.2.9: Compara el estado actual del empaquetador contra el baseline congelado de la Fase 13."""
        if not os.path.exists(self.ast_cache_path):
            self.skipTest("Caché del AST no disponible. Se requiere ejecutar el pipeline base primero.")

        from core.ast.builder import PayloadRegistry
        from core.ast.enums import ContentNodeType

        with open(self.ast_cache_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            real_ast = []
            for d in raw_data:
                type_str = d["type"].upper() if hasattr(d["type"], "upper") else str(d["type"])
                if "EQUATION" in type_str or "MATH" in type_str:
                    ntype = ContentNodeType.INLINE_EQUATION
                elif "TABLE" in type_str:
                    ntype = ContentNodeType.TABLE_SIMPLE
                elif "HEADING" in type_str or "SECTION" in type_str:
                    ntype = ContentNodeType.HEADING
                elif "LIST" in type_str:
                    ntype = ContentNodeType.LIST
                else:
                    try:
                        ntype = ContentNodeType(type_str)
                    except ValueError:
                        ntype = ContentNodeType.PARAGRAPH

                payload = PayloadRegistry.create(ntype, d["content"])
                
                node = ASTNode(
                    node_id=d["node_id"],
                    sequence_id=d["sequence_id"],
                    node_type=ntype,
                    payload=payload,
                    control_plane=d.get("control_plane", {"context_id": "GLOBAL_ROOT", "structural_path": ["ROOT"]})
                )
                real_ast.append(node)

        # Desempaquetado de la tupla SOTA
        production_units, _ = build_semantic_chunks_as_units(real_ast, self.estimator)
        
        actual_snapshot = [
            {
                "chunk_index": u.chunk_index,
                "chunk_id": u.chunk_id,
                "chunk_fingerprint": u.chunk_fingerprint,
                "chunk_type": u.chunk_type.value if hasattr(u.chunk_type, "value") else u.chunk_type,
                "source_sequence_range": list(u.source_sequence_range), # Tupla a Lista para JSON
                "node_count": u.node_count,
                "context_id": u.context_id,
                "context_depth": u.context_depth,
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
            
            # SOTA: Retrocompatibilidad con snapshots previos a la Fase 13
            if "context_id" in expected:
                self.assertEqual(actual["context_id"], expected["context_id"], f"Regresión de Frontera Lógica (Contexto) en chunk {actual['chunk_index']}.")