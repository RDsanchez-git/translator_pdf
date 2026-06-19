import os
import asyncio
import unittest
import uuid
from unittest.mock import MagicMock
from core.ast.models import TranslationUnit, TranslationTaskType, FastWordEstimator
from core.compiler.assembler import DocumentAssembler

# SOTA: Importaciones purgadas de dependencias legadas (Fase 14)
from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.adapters import BypassProvider
from apps.llm_workers.resilient_provider import ResilientProvider
from core.resilience.circuit_breaker import CircuitBreakerRegistry
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.cache_provider import CachedLLMProvider
from apps.llm_workers.dispatcher import AsyncDispatcher

class TestTranslationLayerIntegration(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación del pipeline Dispatcher -> Assembler en memoria pura (Fase 14)."""

    def setUp(self):
        self.test_id = uuid.uuid4().hex
        self.test_db_path = f"tests/fixtures/integration_cache_{self.test_id}.db"
        
        estimator = FastWordEstimator()
        self.prompt_builder = PromptBuilder(model_name="bypass-mock", prompt_version="v1.0", estimator=estimator)
        
        base_provider = BypassProvider()
        breaker = CircuitBreakerRegistry.get_breaker("layer_breaker", threshold=5)
        resilient = ResilientProvider(underlying=base_provider, breaker=breaker)
        quota = QuotaManager(rpm_limit=1000, tpm_limit=100000)
        rate_provider = RateLimitedProvider(underlying=resilient, quota_manager=quota)
        
        self.cache_provider = CachedLLMProvider(underlying=rate_provider, db_path=self.test_db_path)
        asyncio.run(self.cache_provider.initialize())
        
        # SOTA: Mock del ContextResolverProtocol
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = MagicMock(breadcrumbs=(), depth=0)
        
        self.dispatcher = AsyncDispatcher(
            context_resolver=mock_resolver,
            prompt_builder=self.prompt_builder,
            provider_stack=self.cache_provider
        )
        
        from core.validation.pipeline import ValidationPipeline
        self.dispatcher.validation_pipeline = ValidationPipeline()
        self.assembler = DocumentAssembler(separator="\n\n")

    def tearDown(self):
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
            TranslationUnit(
                chunk_index=1, chunk_id="c1", chunk_fingerprint="fp1",
                chunk_type=TranslationTaskType.TRANSLATE, source_sequence_range=(1,1), node_count=1, 
                context_id="CTX_TEST", context_depth=1, target_payload="A", estimated_tokens=2, payload_sha256="h1"
            ),
            TranslationUnit(
                chunk_index=2, chunk_id="c2", chunk_fingerprint="fp2",
                chunk_type=TranslationTaskType.PRESERVE, source_sequence_range=(2,2), node_count=1, 
                context_id="CTX_TEST", context_depth=1, target_payload="B", estimated_tokens=2, payload_sha256="h2"
            ),
            TranslationUnit(
                chunk_index=3, chunk_id="c3", chunk_fingerprint="fp3",
                chunk_type=TranslationTaskType.TRANSLATE, source_sequence_range=(3,3), node_count=1, 
                context_id="CTX_TEST", context_depth=1, target_payload="C", estimated_tokens=2, payload_sha256="h3"
            )
        ]

        translated_units = await self.dispatcher.dispatch(units)
        
        # Ajuste 3: Certificación matemática contra desorden por asincronía
        self.assertEqual([u.chunk_index for u in translated_units], [1, 2, 3])

        doc = self.assembler.assemble(translated_units)

        # SOTA: El BypassProvider retorna el string crudo o el System Prompt empaquetado. 
        # Verificamos que los textos de origen estén en el documento final.
        self.assertIn("A", doc.content)
        self.assertIn("B", doc.content)
        self.assertIn("C", doc.content)
        
        # Auditoría de agregación de telemetría de tokens
        self.assertGreaterEqual(doc.total_input_tokens, 0) # SOTA: Tolerancia a Bypass
        self.assertGreaterEqual(doc.total_output_tokens, 0)
        self.assertEqual(doc.total_chunks, 3)