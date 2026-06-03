import os
import json
import unittest
import hashlib
from core.ast.models import TranslationUnit
from unittest.mock import MagicMock
from apps.llm_workers.workers import FakeGeminiWorker
from apps.llm_workers.resilience import ResilientWorkerProxy
from apps.llm_workers.cache import SQLiteTranslationCache
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.compiler.assembler import DocumentAssembler

class TestTrueWalkingSkeletonE2E(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación determinista del pipeline transversal (AST -> Unidades -> Caché -> Ensamblador)."""

    def setUp(self):
        self.ast_fixture_path = "tests/fixtures/sample_3_pages.pdf.ast.json"
        self.test_db_path = "tests/fixtures/e2e_cache_real.db"
        
        if not os.path.exists(self.ast_fixture_path):
            self.skipTest(f"Fixture AST no encontrado en {self.ast_fixture_path}")

        self.cache = SQLiteTranslationCache(db_path=self.test_db_path)
        
        # Inyección de mocks para satisfacer el contrato estructural del FakeGeminiWorker
        mock_prompt_builder = MagicMock()
        mock_prompt_builder.build.return_value = "Prompt de prueba"
        mock_prompt_builder.PROMPT_VERSION = "v1.0-mock"
        
        mock_estimator = MagicMock()
        mock_estimator.estimate.return_value = 5
        
        # Corrección exacta: Inyección de dependencias requeridas
        fake_worker = FakeGeminiWorker(prompt_builder=mock_prompt_builder, estimator=mock_estimator)
        
        self.proxy = ResilientWorkerProxy(base_worker=fake_worker, max_concurrency=5)
        self.dispatcher = AsyncDispatcher(
            worker=self.proxy, cache=self.cache,
            model_name="gemini-mock", prompt_version="v1.0"
        )
        self.assembler = DocumentAssembler(separator="\n\n")

    def tearDown(self):
        for suffix in ("", "-wal", "-shm"):
            p = f"{self.test_db_path}{suffix}"
            if os.path.exists(p):
                try:
                    os.remove(p)
                except PermissionError:
                    pass

    def _bridge_ast_to_units(self, ast_nodes: list) -> list[TranslationUnit]:
        """Adaptador tolerante que traduce el esquema físico del AST a DTOs de ejecución."""
        units = []
        for i, node in enumerate(ast_nodes, start=1):
            node_type = node.get("type", "unknown")
            is_passthrough = node_type in ["equation", "table", "image", "inline_math", "Table", "Image"]
            
            # Ajuste 2: Cobertura polimórfica de la clave de texto original del AST
            payload = node.get("content") or node.get("latex") or node.get("text") or ""
            if not payload.strip():
                continue
                
            # Ajuste 1: Firma criptográfica determinista estable entre subprocesos
            sha256_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
                
            units.append(TranslationUnit(
                chunk_index=i,
                chunk_id=node.get("node_id", f"node_{i}"),
                chunk_type="passthrough" if is_passthrough else "translate",
                source_sequence_range=(i, i),
                node_count=1,
                reference_context="",
                target_payload=payload,
                estimated_tokens=len(payload) // 4,
                payload_sha256=sha256_hash
            ))
        return units

    async def test_full_pipeline_from_ast_with_cache_reentrancy(self):
        """10D.5: Flujo completo garantizando passthrough, cobertura de ensamblado y reentrabilidad de caché."""
        
        with open(self.ast_fixture_path, 'r', encoding='utf-8') as f:
            ast_data = json.load(f)
            nodes = ast_data.get("nodes", ast_data) if isinstance(ast_data, dict) else ast_data

        translation_units = self._bridge_ast_to_units(nodes)
        self.assertGreater(len(translation_units), 0, "El adaptador no pudo mapear nodos válidos del AST.")

        # ==========================================
        # PRIMERA CORRIDA (Cache Miss)
        # ==========================================
        translated_units_run_1 = await self.dispatcher.dispatch(translation_units)
        
        # Ajuste 3: Eliminación de tautología y evaluación condicional del passthrough
        passthrough_count = sum(1 for u in translated_units_run_1 if u.chunk_type == "passthrough")
        if passthrough_count > 0:
            passthrough_unit = next(u for u in translated_units_run_1 if u.chunk_type == "passthrough")
            self.assertEqual(passthrough_unit.model_name, "bypass_passthrough")

        # Ajuste 4: Verificación estricta de cobertura del ensamblador
        doc_1 = self.assembler.assemble(translated_units_run_1)
        self.assertEqual(doc_1.total_chunks, len(translation_units), "El ensamblador omitió elementos del pipeline.")
        self.assertEqual(doc_1.translated_chunks + doc_1.passthrough_chunks, doc_1.total_chunks)

        # ==========================================
        # SEGUNDA CORRIDA (Cache Hit Reentrante)
        # ==========================================
        translated_units_run_2 = await self.dispatcher.dispatch(translation_units)
        
        # Validación criptográfica del hit
        for unit in translated_units_run_2:
            if unit.chunk_type == "translate":
                self.assertTrue(
                    unit.model_name.startswith("cache_hit:"), 
                    f"Fallo de persistencia en disco. El chunk {unit.chunk_index} re-ejecutó el worker."
                )
            elif unit.chunk_type == "passthrough":
                self.assertEqual(unit.model_name, "bypass_passthrough")

        doc_2 = self.assembler.assemble(translated_units_run_2)
        self.assertEqual(doc_1.content, doc_2.content, "Corrupción latente: La hidratación de la caché alteró los datos.")