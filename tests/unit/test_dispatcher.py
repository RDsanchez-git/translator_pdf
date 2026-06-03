import unittest
from unittest.mock import AsyncMock
from core.ast.models import TranslationUnit, TranslatedUnit
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.execution.exceptions import ChunkExecutionError

class TestAsyncDispatcher(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación del orquestador concurrente unificado (Fase 10C.7)."""

    def setUp(self):
        self.mock_worker = AsyncMock()
        self.mock_cache = AsyncMock()
        # Cache Miss por defecto para mantener la retrocompatibilidad de los tests previos
        self.mock_cache.get.return_value = None
        
        self.dispatcher = AsyncDispatcher(
            worker=self.mock_worker,
            cache=self.mock_cache,
            model_name="fake-gemini",
            prompt_version="v1.0"
        )

    def _create_mock_unit(self, chunk_index: int, chunk_type: str) -> TranslationUnit:
        return TranslationUnit(
            chunk_index=chunk_index,
            chunk_id=f"chunk_{chunk_index:04d}",
            chunk_type=chunk_type,
            source_sequence_range=(chunk_index, chunk_index),
            node_count=1,
            reference_context="",
            target_payload=f"Payload {chunk_index}",
            estimated_tokens=5,
            payload_sha256=f"hash_{chunk_index}"
        )

    def _mock_translate_side_effect(self, unit: TranslationUnit) -> TranslatedUnit:
        return TranslatedUnit(
            chunk_index=unit.chunk_index,
            chunk_id=unit.chunk_id,
            chunk_type=unit.chunk_type,
            source_sequence_range=unit.source_sequence_range,
            translated_payload=f"MOCK::{unit.target_payload}",
            payload_sha256=unit.payload_sha256,
            model_name="fake-gemini",
            prompt_version="v1.0",
            input_tokens=5,
            output_tokens=5,
            latency_ms=10.0
        )

    async def test_case_A_all_passthrough(self):
        units = [self._create_mock_unit(i, "passthrough") for i in range(1, 4)]
        results = await self.dispatcher.dispatch(units)
        self.mock_worker.translate.assert_not_called()
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].model_name, "bypass_passthrough")

    async def test_case_B_all_translate(self):
        units = [self._create_mock_unit(i, "translate") for i in range(1, 4)]
        self.mock_worker.translate.side_effect = self._mock_translate_side_effect
        
        results = await self.dispatcher.dispatch(units)
        
        # Corrección: Validar la densidad del lote de salida para consumir la variable
        self.assertEqual(len(results), 3)
        self.assertEqual(self.mock_worker.translate.call_count, 3)
        self.mock_cache.set.assert_called() # Certifica el guardado pos-miss

    async def test_case_C_mixed_payloads(self):
        units = [
            self._create_mock_unit(1, "translate"),
            self._create_mock_unit(2, "passthrough"),
            self._create_mock_unit(3, "translate")
        ]
        self.mock_worker.translate.side_effect = self._mock_translate_side_effect
        results = await self.dispatcher.dispatch(units)
        self.assertEqual(self.mock_worker.translate.call_count, 2)
        self.assertEqual(results[1].model_name, "bypass_passthrough")

    async def test_case_D_worker_failure(self):
        units = [self._create_mock_unit(1, "translate")]
        self.mock_worker.translate.side_effect = ConnectionError("Simulated Network Drop")
        with self.assertRaises(ChunkExecutionError):
            await self.dispatcher.dispatch(units)

    async def test_case_E_out_of_order_resolution(self):
        import asyncio
        units = [self._create_mock_unit(i, "translate") for i in range(1, 4)]
        async def _variable_latency(unit):
            if unit.chunk_index == 1:
                await asyncio.sleep(0.04)
            elif unit.chunk_index == 2:
                await asyncio.sleep(0.01)
            return self._mock_translate_side_effect(unit)
        self.mock_worker.translate.side_effect = _variable_latency
        results = await self.dispatcher.dispatch(units)
        self.assertEqual(results[0].chunk_index, 1)
        self.assertEqual(results[2].chunk_index, 3)

    async def test_case_F_passthrough_with_simultaneous_failure(self):
        units = [self._create_mock_unit(1, "passthrough"), self._create_mock_unit(2, "translate")]
        self.mock_worker.translate.side_effect = ConnectionError("Timeout")
        with self.assertRaises(ChunkExecutionError) as context:
            await self.dispatcher.dispatch(units)
        self.assertEqual(context.exception.chunk_index, 2)

    async def test_case_G_duplicate_chunk_index_rejected(self):
        units = [self._create_mock_unit(5, "translate"), self._create_mock_unit(5, "passthrough")]
        with self.assertRaises(ValueError):
            await self.dispatcher.dispatch(units)

    async def test_case_H_cache_hit_bypass_worker(self):
        """10C.7.1: Certifica que ante un hit de caché se evite la llamada al LLM y la latencia sea cero."""
        unit = self._create_mock_unit(1, "translate")
        self.mock_cache.get.return_value = "Texto Traducido Recuperado"

        results = await self.dispatcher.dispatch([unit])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].translated_payload, "Texto Traducido Recuperado")
        self.assertEqual(results[0].model_name, "cache_hit:fake-gemini")
        # Invariante crítica: El worker de red no debió ser contactado
        self.mock_worker.translate.assert_not_called()
        self.mock_cache.set.assert_not_called()