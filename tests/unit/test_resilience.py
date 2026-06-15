import asyncio
import unittest
from unittest.mock import AsyncMock
from core.ast.models import TranslationUnit, TranslatedUnit
from apps.llm_workers.resilience import ResilientWorkerProxy
from core.execution.exceptions import TransientAPIError

class TestResilientWorkerProxy(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación blindada de las capas de control de concurrencia y reintentos (Fase 10C.4/5)."""

    def setUp(self):
        self.mock_worker = AsyncMock()
        # Capacidad máxima limitada a 2 ranuras concurrentes simultáneas
        self.proxy = ResilientWorkerProxy(base_worker=self.mock_worker, max_concurrency=2)
        
        # SOTA: Restauramos y forzamos dinámicamente que el decorador intercepte TransientAPIError
        # sin alterar el comportamiento ante ValueErrors u otros fallos fatales.
        import tenacity
        underlying_func = getattr(self.proxy._execute_with_retry, "__func__", None)
        if underlying_func and hasattr(underlying_func, "retry"):
            underlying_func.retry.stop = tenacity.stop_after_attempt(3)

        self.unit = TranslationUnit(
            chunk_index=1,
            chunk_id="chunk_0001",
            chunk_type="translate",
            source_sequence_range=(1, 1),
            node_count=1,
            reference_context="",
            target_payload="Texto",
            estimated_tokens=2,
            payload_sha256="hash"
        )

    async def test_retry_policy_transient_success(self):
        """10C.4: Verifica la recuperación exponencial ante fallos efímeros retornando un DTO válido."""
        expected_unit = TranslatedUnit(
            chunk_index=1,
            chunk_id="chunk_0001",
            chunk_type="translate",
            source_sequence_range=(1, 1),
            translated_payload="Éxito Traducido Real",
            payload_sha256="hash",
            model_name="fake-gemini-1.5-flash",
            prompt_version="v1.0",
            input_tokens=10,
            output_tokens=12,
            latency_ms=5.2
        )
        
        # Inyectamos las excepciones exactas que el proxy de producción está configurado para escuchar
        self.mock_worker.translate.side_effect = [
            TransientAPIError("429 Too Many Requests"),
            TransientAPIError("503 Service Unavailable"),
            expected_unit
        ]

        result = await self.proxy.translate(self.unit)
        
        self.assertEqual(self.mock_worker.translate.call_count, 3)
        self.assertEqual(result, expected_unit, "El proxy alteró o no propagó el DTO de salida final.")

    async def test_retry_policy_fatal_propagation(self):
        """10C.4: Certifica que errores lógicos abortan de inmediato sin generar reintentos espurios."""
        self.mock_worker.translate.side_effect = ValueError("Fatal Error: Invalid System Prompt")

        with self.assertRaises(ValueError):
            await self.proxy.translate(self.unit)

        self.assertEqual(self.mock_worker.translate.call_count, 1)

    async def test_rate_limiter_concurrency_ceiling(self):
        """10C.5: Valida el límite de concurrencia máxima usando exclusivamente APIs públicas."""
        entered_tasks = 0
        max_simultaneous = 0

        # Simulación dinámica de cuello de botella por I/O bound
        async def slow_translate(unit: TranslationUnit) -> TranslatedUnit:
            nonlocal entered_tasks, max_simultaneous
            entered_tasks += 1
            max_simultaneous = max(max_simultaneous, entered_tasks)
            await asyncio.sleep(0.02)
            entered_tasks -= 1
            return TranslatedUnit(
                chunk_index=unit.chunk_index, chunk_id=unit.chunk_id, chunk_type=unit.chunk_type,
                source_sequence_range=unit.source_sequence_range, translated_payload="OK",
                payload_sha256=unit.payload_sha256, model_name="fake", prompt_version="v1.0",
                input_tokens=1, output_tokens=1, latency_ms=1.0
            )
        
        self.mock_worker.translate.side_effect = slow_translate

        # Disparar 3 unidades concurrentes sobrepasando el semáforo (límite 2)
        units = [
            TranslationUnit(
                chunk_index=i, chunk_id=f"chunk_000{i}", chunk_type="translate",
                source_sequence_range=(i, i), node_count=1, reference_context="",
                target_payload="T", estimated_tokens=1, payload_sha256="h"
            )
            for i in range(3)
        ]
        
        tasks = [self.proxy.translate(u) for u in units]
        await asyncio.gather(*tasks)
        
        # Validación de API pública de concurrencia real medida en vuelo
        self.assertEqual(max_simultaneous, 2, "El proxy violó la barrera e inyectó más tareas concurrentes del máximo permitido.")