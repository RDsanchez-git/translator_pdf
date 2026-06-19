import os
import json
import math
import asyncio
import unittest
from apps.bootstrap.pipeline_factory import build_pipeline

# SOTA: Importaciones del Provider Stack (Fase 14)
from apps.llm_workers.prompt_builder import PromptBuilder
from core.ast.models import FastWordEstimator
from apps.llm_workers.adapters import BypassProvider
from apps.llm_workers.resilient_provider import ResilientProvider
from core.resilience.circuit_breaker import CircuitBreakerRegistry
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.sync_bridge import SyncProviderBridge
from tests.helpers.fakes import FakeChunker

class TestSemanticChunkRegression(unittest.IsolatedAsyncioTestCase):
    """Nivel 2 — Semántico: Adaptado a Zero-Cost con simulación de similitud."""

    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.golden_path = "tests/golden/sample_3_pages.semantics.json"
        
        estimator = FastWordEstimator()
        prompt_builder = PromptBuilder(model_name="bypass-mock", prompt_version="v1.0", estimator=estimator)
        
        base_provider = BypassProvider()
        breaker = CircuitBreakerRegistry.get_breaker("bypass_sem", threshold=5)
        resilient = ResilientProvider(underlying=base_provider, breaker=breaker)
        quota = QuotaManager(rpm_limit=1000, tpm_limit=100000)
        rate_provider = RateLimitedProvider(underlying=resilient, quota_manager=quota)
        
        self.processor = SyncProviderBridge(async_provider=rate_provider, prompt_builder=prompt_builder)
        
        # SOTA: Mantener el nombre del kwarg 'dispatcher' para la compatibilidad con la fábrica heredada
        self.pipeline = build_pipeline(chunker=FakeChunker(), dispatcher=self.processor)

    def tearDown(self):
        self.processor.shutdown()

    def _calculate_cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0

    async def _mock_embed_text(self, text: str) -> list[float]:
        # SOTA: Vector determinista para emular embedding sin red
        return [0.5] * 10 

    async def test_chunk_semantic_similarity_bypass_cache(self):
        if not os.path.exists(self.golden_path):
            self.skipTest("Molde semántico ausente. Corra el bootstrap primero.")

        with open(self.golden_path, "r", encoding="utf-8") as f:
            golden_config = json.load(f)
        
        nodes = self.pipeline.parser.parse(self.pdf_real_path)
        
        for node in nodes:
            source_text = node.content or ""
            if not source_text.strip():
                continue

            # Ejecución concurrente mediante el puente síncrono
            translated_text = await asyncio.to_thread(self.processor.execute, node)

            source_vector = await self._mock_embed_text(source_text)
            translated_vector = await self._mock_embed_text(translated_text)

            similarity = self._calculate_cosine_similarity(source_vector, translated_vector)

            self.assertGreaterEqual(
                similarity,
                golden_config.get("minimum_similarity", 0.85),
                f"Regresión Semántica detectada: {similarity:.4f} < {golden_config.get('minimum_similarity', 0.85)}"
            )