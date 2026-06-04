import os
import json
import math
import asyncio
import unittest
import uuid
from apps.bootstrap.pipeline_factory import build_pipeline

from apps.llm_workers.gemini_client import GeminiClient
from apps.llm_workers.prompt_builder import PromptBuilder
from core.ast.models import FastWordEstimator
from apps.llm_workers.workers import GeminiWorker
from apps.llm_workers.cache import SQLiteTranslationCache
from apps.llm_workers.dispatcher import AsyncDispatcher
from tests.helpers.fakes import FakeChunker

# Modificar la sección de la cabecera de la clase en tests/integration/test_translation_semantics.py:

# All 11C
# Semantic suite currently assumes low chunk cardinality. Linear growth O(N) will saturate 15 RPM limiter.
# Mitigation strategy: Implement parallel batch embedding collection or token pooling windows.
class TestSemanticChunkRegression(unittest.IsolatedAsyncioTestCase):
    """Nivel 2 — Semántico: Validación atómica pre-ensamblado contra regresiones lingüísticas."""

    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.golden_path = "tests/golden/sample_3_pages.semantics.json"
        
        # Base de datos efímera para forzar bypass de caché (Mide Gemini real)
        self.test_id = uuid.uuid4().hex
        self.test_db_path = f"tests/fixtures/semantic_cache_{self.test_id}.db"

        if not os.environ.get("GEMINI_API_KEY"):
            self.skipTest("GEMINI_API_KEY ausente. Omitiendo prueba semántica Nightly.")

        self.client = GeminiClient()
        prompt_builder = PromptBuilder()
        estimator = FastWordEstimator()
        
        worker = GeminiWorker(client=self.client, prompt_builder=prompt_builder, estimator=estimator)
        cache = SQLiteTranslationCache(db_path=self.test_db_path)
        
        dispatcher = AsyncDispatcher(
            worker=worker, cache=cache, model_name=self.client.model_v, prompt_version=prompt_builder.PROMPT_VERSION
        )
        
        self.pipeline = build_pipeline(chunker=FakeChunker(), dispatcher=dispatcher)

    def tearDown(self):
        for suffix in ("", "-wal", "-shm"):
            p = f"{self.test_db_path}{suffix}"
            if os.path.exists(p):
                try:
                    os.remove(p)
                except PermissionError:
                    pass

    def _calculate_cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0

    async def test_chunk_semantic_similarity_bypass_cache(self):
        if not os.path.exists(self.golden_path):
            self.skipTest("Molde semántico ausente. Corra el bootstrap primero.")

        with open(self.golden_path, "r", encoding="utf-8") as f:
            golden_config = json.load(f)
        
        # Extracción de unidades puras aisladas del ensamblador
        nodes = self.pipeline.parser.parse(self.pdf_real_path)
        translation_units = self.pipeline.chunker.chunk(nodes)
        translated_units = await self.pipeline.dispatcher.dispatch(translation_units)
        
        translated_map = {u.chunk_index: u for u in translated_units}

        # Analizar iterativamente por Chunk con estrechamiento de tipos estricto
        for unit in translation_units:
            translated_unit = translated_map.get(unit.chunk_index)
            
            # SOTA Fix: Estrechamiento de tipo explícito para complacer a Pyright/mypy
            if translated_unit is None:
                self.fail(f"Falta la unidad traducida para el índice {unit.chunk_index}")

            source_text = unit.target_payload
            translated_text = translated_unit.translated_payload

            # Inferencia paralela no bloqueante contra la API real 2026
            source_vector = await asyncio.to_thread(self.client.embed_text, source_text)
            translated_vector = await asyncio.to_thread(self.client.embed_text, translated_text)

            similarity = self._calculate_cosine_similarity(source_vector, translated_vector)
            print(f"\n[Semantic Audit] Chunk {unit.chunk_index} Cosine Similarity: {similarity:.4f} (Mínimo: {golden_config['minimum_similarity']})")

            self.assertGreaterEqual(
                similarity,
                golden_config["minimum_similarity"],
                f"Regresión Semántica en Chunk {unit.chunk_index}: {similarity:.4f} < {golden_config['minimum_similarity']}"
            )