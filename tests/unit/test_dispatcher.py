import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from core.ast.models import TranslationUnit, TranslationTaskType
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.execution.exceptions import ChunkExecutionError

# SOTA: Contratos de la nueva arquitectura de Proveedores
from apps.llm_workers.routing import ProviderResult
from apps.llm_workers.prompt_builder import PromptEnvelope, PromptBuilder

class TestAsyncDispatcher(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación del orquestador concurrente unificado (Fase 14)."""

    def setUp(self):
        self.mock_provider = AsyncMock()
        
        # SOTA: Inyección de contexto y estimador falsos para aislar al orquestador
        self.mock_resolver = MagicMock()
        self.mock_resolver.resolve.return_value = MagicMock(breadcrumbs=(), depth=0)
        
        mock_estimator = MagicMock()
        mock_estimator.estimate.return_value = 5
        self.prompt_builder = PromptBuilder(model_name="fake-gemini", prompt_version="v1.0", estimator=mock_estimator)
        
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

    def _mock_translate_side_effect(self, envelope: PromptEnvelope) -> ProviderResult:
        """SOTA: Responde estrictamente al contrato del LLMProvider."""
        return ProviderResult(
            chunk_id=envelope.chunk_id,
            translated_text=f"MOCK::{envelope.raw_payload}",
            input_tokens=5,
            output_tokens=5,
            latency_ms=10.0,
            finish_reason="stop"
        )

    async def test_case_D_worker_failure(self):
        units = [self._create_mock_unit(1, TranslationTaskType.TRANSLATE)]
        self.mock_provider.translate.side_effect = ConnectionError("Simulated Network Drop")
        
        with self.assertRaises(ChunkExecutionError):
            await self.dispatcher.dispatch(units)

    async def test_case_E_out_of_order_resolution(self):
        units = [self._create_mock_unit(i, TranslationTaskType.TRANSLATE) for i in range(1, 4)]
        
        async def _variable_latency(envelope: PromptEnvelope):
            # Extrae el índice del chunk_id (e.g. "chunk_0001")
            index = int(envelope.chunk_id.split('_')[1])
            if index == 1:
                await asyncio.sleep(0.04)
            elif index == 2:
                await asyncio.sleep(0.01)
            return self._mock_translate_side_effect(envelope)
            
        self.mock_provider.translate.side_effect = _variable_latency
        results = await self.dispatcher.dispatch(units)
        
        self.assertEqual(results[0].chunk_index, 1)
        self.assertEqual(results[2].chunk_index, 3)

    async def test_case_F_passthrough_with_simultaneous_failure(self):
        units = [self._create_mock_unit(1, TranslationTaskType.PRESERVE), self._create_mock_unit(2, TranslationTaskType.TRANSLATE)]
        self.mock_provider.translate.side_effect = ConnectionError("Timeout")
        
        with self.assertRaises(ChunkExecutionError) as context:
            await self.dispatcher.dispatch(units)
        # SOTA: El error detona en el chunk 1 porque el orquestador ya no filtra los PRESERVE
        self.assertEqual(context.exception.chunk_index, 1)

    async def test_case_G_duplicate_chunk_index_rejected(self):
        units = [self._create_mock_unit(5, TranslationTaskType.TRANSLATE), self._create_mock_unit(5, TranslationTaskType.PRESERVE)]
        
        with self.assertRaises(ValueError):
            await self.dispatcher.dispatch(units)

    async def test_case_H_provider_result_mapping(self):
        """SOTA: Certifica el mapeo estructural desde ProviderResult hacia TranslatedUnit."""
        unit = self._create_mock_unit(1, TranslationTaskType.TRANSLATE)
        
        self.mock_provider.translate.return_value = ProviderResult(
            chunk_id=unit.chunk_id,
            translated_text="Mapeo perfecto",
            input_tokens=100,
            output_tokens=200,
            latency_ms=150.0,
            finish_reason="stop"
        )
    
        results = await self.dispatcher.dispatch([unit])
    
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].translated_payload, "Mapeo perfecto")
        self.assertEqual(results[0].input_tokens, 100)
        self.assertEqual(results[0].output_tokens, 200)
        self.assertEqual(results[0].latency_ms, 150.0)