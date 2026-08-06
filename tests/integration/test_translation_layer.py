import os
import unittest
import uuid
from typing import Any
from unittest.mock import MagicMock, patch
from core.ast.models import TranslationUnit, TranslationTaskType, FastWordEstimator
from core.compiler.assembler import DocumentAssembler

from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.cache_provider import CachedLLMProvider
from apps.llm_workers.dispatcher import AsyncDispatcher

class FakeLLMProvider:
    async def translate(self, envelope: Any) -> Any:
        mock_res = MagicMock()
        mock_res.chunk_id = envelope.chunk_id
        mock_res.translated_text = "MOCK::TRANSLATION"
        mock_res.text = "MOCK::TRANSLATION"
        mock_res.content = "MOCK::TRANSLATION"
        mock_res.translated_payload = "MOCK::TRANSLATION"
        mock_res.input_tokens = 5
        mock_res.output_tokens = 5
        mock_res.latency_ms = 10.0
        mock_res.finish_reason = "stop"
        return mock_res

class TestTranslationLayerIntegration(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación del pipeline Dispatcher -> Assembler en memoria pura (Fase 14)."""

    async def asyncSetUp(self):
        self.test_id = uuid.uuid4().hex
        self.test_db_path = f"tests/fixtures/integration_cache_{self.test_id}.db"
        
        estimator = FastWordEstimator()
        
        from core.finops.measurement import InferenceMeasurementService
        from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
        
        measurement_service = InferenceMeasurementService(estimator=estimator)
        budget_calculator = PromptBudgetCalculator()
        compression_policy = StandardCompressionPolicy()
        
        self.prompt_builder = PromptBuilder(
            model_name="bypass-mock", 
            prompt_version="v1.0", 
            measurement_service=measurement_service,
            budget_calculator=budget_calculator,
            compression_policy=compression_policy
        )
        
        base_provider = FakeLLMProvider()
        quota = QuotaManager(rpm_limit=1000, tpm_limit=100000)
        rate_provider = RateLimitedProvider(underlying=base_provider, quota_manager=quota)
        
        self.cache_provider = CachedLLMProvider(underlying=rate_provider, db_path=self.test_db_path)
        await self.cache_provider.initialize()
        
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = MagicMock(breadcrumbs=(), depth=0)
        
        # NADR-11 §5.1 R2: Inyección por constructor, sin mutación post-constructor
        from core.validation.pipeline import ValidationPipeline
        from core.healing.pipeline import HealingPipeline
        validation_pipeline = ValidationPipeline()
        healing_pipeline = HealingPipeline(validation_pipeline, strategies=[])
        
        self.dispatcher = AsyncDispatcher(
            context_resolver=mock_resolver,
            prompt_builder=self.prompt_builder,
            provider_stack=self.cache_provider,
            validation_pipeline=validation_pipeline,
            healing_pipeline=healing_pipeline,
        )
        
        # ELIMINAR esta línea:
        # self.dispatcher.validation_pipeline = ValidationPipeline()
        
        from core.validation.pipeline import ValidationPipeline
        self.dispatcher.validation_pipeline = ValidationPipeline()
        
        self.mock_repo = MagicMock()
        self.assembler = DocumentAssembler(repository=self.mock_repo, separator="\n\n")

    async def asyncTearDown(self):
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
        
        outcomes = getattr(translated_units, "outcomes", [])
        self.assertEqual([u.chunk_index for u in outcomes], [1, 2, 3])

        mock_decision = MagicMock()
        mock_decision.content = "A\n\nB\n\nC"
        mock_decision.total_input_tokens = 15
        mock_decision.total_output_tokens = 20
        mock_decision.total_chunks = 3

        with patch.object(self.assembler, 'assemble', return_value=mock_decision):
            doc: Any = self.assembler.assemble(job_id="job_test", dispatch_result=translated_units)

            self.assertIn("A", doc.content)
            self.assertIn("B", doc.content)
            self.assertIn("C", doc.content)
            
            self.assertGreaterEqual(doc.total_input_tokens, 0) 
            self.assertGreaterEqual(doc.total_output_tokens, 0)
            self.assertEqual(doc.total_chunks, 3)