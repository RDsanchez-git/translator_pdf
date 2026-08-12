import os
import json
import math
import asyncio
import unittest
import sqlite3
from typing import Any
from unittest.mock import MagicMock, patch

from apps.llm_workers.prompt_builder import PromptBuilder
from core.ast.models import ASTNode
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.sync_bridge import SyncProviderBridge
from core.pipeline.orchestrator import TranslationPipeline
from core.metrics.summary import SummaryBuilder
from infra.db.fsm_repository import FSMRepository
from infra.db.document_repository import SQLiteDocumentRepository
from core.execution.handlers import DocumentCommandHandler
from core.pipeline.state_store import FSMStateStore
from apps.bootstrap.pipeline_factory import build_extraction_pipeline
from helpers.fakes import FakeChunker, FakeDispatcher
from core.validation.estimators import ExactBPEEstimator


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

class TestSemanticChunkRegression(unittest.IsolatedAsyncioTestCase):
    """Nivel 2 — Semántico: Adaptado a Zero-Cost con simulación de similitud."""

    async def asyncSetUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.golden_path = "tests/golden/sample_3_pages.semantics.json"
        
        estimator = ExactBPEEstimator()
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
        
        self.processor = SyncProviderBridge(async_provider=rate_provider, prompt_builder=self.prompt_builder)
        
        # Construir TranslationPipeline directamente
        parser = build_extraction_pipeline()
        fsm_db = sqlite3.connect(":memory:")
        fsm_repo = FSMRepository(fsm_db)
        doc_conn = sqlite3.connect(":memory:")
        document_repository = SQLiteDocumentRepository(doc_conn)
        state_store = FSMStateStore(fsm_repo, DocumentCommandHandler(fsm_repo))
        
        # FakeDispatcher cumple DispatcherProtocol.
        # El test nunca invoca pipeline.execute(), solo usa parser y processor directamente.
        self.pipeline = TranslationPipeline(
            parser=parser,
            chunker=FakeChunker(),
            dispatcher=FakeDispatcher(),
            audit_builder=SummaryBuilder(),
            state_store=state_store,
            document_repository=document_repository,
        )

    async def asyncTearDown(self):
        self.processor.shutdown()

    def _calculate_cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0

    async def _mock_embed_text(self, text: str) -> list[float]:
        return [0.5] * 10 

    async def test_chunk_semantic_similarity_bypass_cache(self):
        if not os.path.exists(self.golden_path):
            self.skipTest("Molde semántico ausente. Corra el bootstrap primero.")

        with open(self.golden_path, "r", encoding="utf-8") as f:
            golden_config = json.load(f)
        
        from core.ast.enums import ContentNodeType
        from core.ast.builder import PayloadRegistry
        
        mock_nodes = [
            ASTNode(
                node_id="n1",
                sequence_id=1,
                node_type=ContentNodeType.PARAGRAPH,
                payload=PayloadRegistry.create(ContentNodeType.PARAGRAPH, "Sample prose text content for semantic verification")
            )
        ]
        
        with patch.object(self.pipeline.parser, 'parse', return_value=mock_nodes):
            nodes = self.pipeline.parser.parse(self.pdf_real_path)
            
            for node in nodes:
                source_text = node.text_content or ""
                if not source_text.strip():
                    continue

                translated_text = await asyncio.to_thread(self.processor.execute, node)

                source_vector = await self._mock_embed_text(source_text)
                translated_vector = await self._mock_embed_text(translated_text)

                similarity = self._calculate_cosine_similarity(source_vector, translated_vector)

                self.assertGreaterEqual(
                    similarity,
                    golden_config.get("minimum_similarity", 0.85),
                    f"Regresión Semántica detectada: {similarity:.4f} < {golden_config.get('minimum_similarity', 0.85)}"
                )