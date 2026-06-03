import os
import unittest
import uuid  # Corrección de aislamiento: importación de uuid
from unittest.mock import MagicMock
from core.ast.models import TranslationUnit
from apps.llm_workers.workers import FakeGeminiWorker
from apps.llm_workers.resilience import ResilientWorkerProxy
from apps.llm_workers.cache import SQLiteTranslationCache
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.compiler.assembler import DocumentAssembler

class TestTranslationLayerIntegration(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación del pipeline Dispatcher -> Assembler en memoria pura."""

    def setUp(self):
        # Generación de un sufijo único para evitar colisiones por bloqueos de archivo en Windows
        self.test_id = uuid.uuid4().hex
        self.test_db_path = f"tests/fixtures/integration_cache_{self.test_id}.db"
        
        self.cache = SQLiteTranslationCache(db_path=self.test_db_path)
        
        mock_prompt_builder = MagicMock()
        mock_prompt_builder.build.return_value = "Prompt de prueba"
        mock_prompt_builder.PROMPT_VERSION = "v1.0-mock"
        
        mock_estimator = MagicMock()
        mock_estimator.estimate.return_value = 5
        
        fake_worker = FakeGeminiWorker(prompt_builder=mock_prompt_builder, estimator=mock_estimator)
        self.resilient_proxy = ResilientWorkerProxy(base_worker=fake_worker, max_concurrency=3)
        
        self.dispatcher = AsyncDispatcher(
            worker=self.resilient_proxy, cache=self.cache,
            model_name="gemini-mock", prompt_version="v1.0"
        )
        self.assembler = DocumentAssembler(separator="\n\n")

    def tearDown(self):
        # Limpieza del archivo único dinámico
        for suffix in ("", "-wal", "-shm"):
            p = f"{self.test_db_path}{suffix}"
            if os.path.exists(p):
                try: 
                    os.remove(p)
                except PermissionError: 
                    pass

    async def test_translation_layer_flow(self):
        """Ajuste 2: Prueba acotada a la capa de traducción y ensamble."""
        units = [
            TranslationUnit(chunk_index=1, chunk_id="c1", chunk_type="translate", source_sequence_range=(1,1), node_count=1, reference_context="", target_payload="A", estimated_tokens=2, payload_sha256="h1"),
            TranslationUnit(chunk_index=2, chunk_id="c2", chunk_type="passthrough", source_sequence_range=(2,2), node_count=1, reference_context="", target_payload="B", estimated_tokens=2, payload_sha256="h2"),
            TranslationUnit(chunk_index=3, chunk_id="c3", chunk_type="translate", source_sequence_range=(3,3), node_count=1, reference_context="", target_payload="C", estimated_tokens=2, payload_sha256="h3")
        ]

        translated_units = await self.dispatcher.dispatch(units)
        
        # Ajuste 3: Certificación matemática contra desorden por asincronía
        self.assertEqual([u.chunk_index for u in translated_units], [1, 2, 3])

        doc = self.assembler.assemble(translated_units)

        # Corrección exacta: Validar usando el patrón basado en el hash del DTO
        self.assertIn("FAKE_TRANSLATION::h1", doc.content)
        self.assertIn("B", doc.content)
        self.assertIn("FAKE_TRANSLATION::h3", doc.content)
        
        # Auditoría de agregación de telemetría de tokens
        self.assertGreater(doc.total_input_tokens, 0)
        self.assertGreater(doc.total_output_tokens, 0)
        self.assertEqual(doc.total_chunks, 3)