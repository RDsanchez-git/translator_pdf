import unittest
import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from core.ast.models import TranslationUnit, TranslationTaskType
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.execution.exceptions import ChunkExecutionError

from apps.llm_workers.prompt_builder import PromptEnvelope, PromptBuilder

class TestAsyncDispatcher(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación del orquestador concurrente unificado (Fase 14)."""

    def setUp(self):
        self.mock_provider = AsyncMock()
        
        self.mock_resolver = MagicMock()
        self.mock_resolver.resolve.return_value = MagicMock(breadcrumbs=(), depth=0)
        
        mock_estimator = MagicMock()
        mock_estimator.estimate_tokens.return_value = 5  # SOTA FIX: .estimate_tokens
        
        from core.finops.measurement import InferenceMeasurementService
        from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
        
        measurement_service = InferenceMeasurementService(estimator=mock_estimator)
        budget_calculator = PromptBudgetCalculator()
        compression_policy = StandardCompressionPolicy()
        
        self.prompt_builder = PromptBuilder(
            model_name="fake-gemini", 
            prompt_version="v1.0", 
            measurement_service=measurement_service,
            budget_calculator=budget_calculator,
            compression_policy=compression_policy
        )
        
        self.dispatcher = AsyncDispatcher(
            context_resolver=self.mock_resolver,
            prompt_builder=self.prompt_builder,
            provider_stack=self.mock_provider
        )

    def _create_mock_unit(self, chunk_index: int, chunk_type: TranslationTaskType) -> TranslationUnit:
        return TranslationUnit(
            chunk_index=chunk_index,
            chunk_id=f"chunk_{chunk_index:04d}",
            chunk_fingerprint=f"fp_{chunk_index:04d}",
            chunk_type=chunk_type,
            source_sequence_range=(chunk_index, chunk_index),
            node_count=1,
            context_id="CTX_DISPATCH_MOCK",
            context_depth=1,
            target_payload=f"Payload {chunk_index}",
            estimated_tokens=5,
            payload_sha256=f"hash_{chunk_index}"
        )

    def _mock_translate_side_effect(self, envelope: PromptEnvelope) -> Any:
        """SOTA: Responde estrictamente al contrato del LLMProvider."""
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

    async def test_case_D_worker_failure(self):
        units = [self._create_mock_unit(1, TranslationTaskType.TRANSLATE)]
        self.mock_provider.translate.side_effect = ConnectionError("Simulated Network Drop")
        
        with self.assertRaises(ChunkExecutionError):
            await self.dispatcher.dispatch(units)

    async def test_case_E_out_of_order_resolution(self):
        units = [self._create_mock_unit(i, TranslationTaskType.TRANSLATE) for i in range(1, 4)]
        
        async def _variable_latency(envelope: PromptEnvelope):
            index = int(envelope.chunk_id.split('_')[1])
            if index == 1:
                await asyncio.sleep(0.04)
            elif index == 2:
                await asyncio.sleep(0.01)
            return self._mock_translate_side_effect(envelope)
            
        self.mock_provider.translate.side_effect = _variable_latency
        results = await self.dispatcher.dispatch(units)
        
        self.assertEqual(results.outcomes[0].chunk_index, 1)
        self.assertEqual(results.outcomes[2].chunk_index, 3)

    async def test_case_F_passthrough_with_simultaneous_failure(self):
        units = [self._create_mock_unit(1, TranslationTaskType.PRESERVE), self._create_mock_unit(2, TranslationTaskType.TRANSLATE)]
        self.mock_provider.translate.side_effect = ConnectionError("Timeout")
        
        with self.assertRaises(ChunkExecutionError) as context:
            await self.dispatcher.dispatch(units)
        self.assertEqual(context.exception.chunk_index, 1)

    async def test_case_G_duplicate_chunk_index_rejected(self):
        units = [self._create_mock_unit(5, TranslationTaskType.TRANSLATE), self._create_mock_unit(5, TranslationTaskType.PRESERVE)]
        
        with self.assertRaises(ValueError):
            await self.dispatcher.dispatch(units)

    async def test_case_H_provider_result_mapping(self):
        """SOTA: Certifica el mapeo estructural desde ProviderResult hacia TranslatedUnit."""
        unit = self._create_mock_unit(1, TranslationTaskType.TRANSLATE)
        
        mock_inference = MagicMock()
        mock_inference.chunk_id = unit.chunk_id
        mock_inference.translated_text = "Mapeo perfecto"
        mock_inference.text = "Mapeo perfecto"
        mock_inference.content = "Mapeo perfecto"
        mock_inference.translated_payload = "Mapeo perfecto"
        mock_inference.input_tokens = 100
        mock_inference.output_tokens = 200
        mock_inference.latency_ms = 150.0
        mock_inference.finish_reason = "stop"
        
        self.mock_provider.translate.return_value = mock_inference
    
        results = await self.dispatcher.dispatch([unit])
    
        self.assertEqual(len(results.outcomes), 1)
        outcome = results.outcomes[0]
        
        payload = outcome.translated_unit.translated_payload if outcome.translated_unit else ""
        self.assertEqual(payload, "Mapeo perfecto")