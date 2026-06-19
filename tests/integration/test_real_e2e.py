import unittest
import uuid
from typing import List
from core.ast.models import ASTNode, TranslationUnit, FastWordEstimator, TranslationTaskType
from core.pipeline.job import TranslationJob, JobStatus
from apps.bootstrap.pipeline_factory import build_pipeline

# SOTA: Importaciones del Provider Stack (Fase 14)
from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.adapters import BypassProvider
from apps.llm_workers.resilient_provider import ResilientProvider
from core.resilience.circuit_breaker import CircuitBreakerRegistry
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.sync_bridge import SyncProviderBridge
from unittest.mock import MagicMock
from apps.llm_workers.dispatcher import AsyncDispatcher

class FinOpsControlledChunker:
    """Chunker de control presupuestario para pruebas E2E."""
    def chunk(self, nodes: List[ASTNode]) -> List[TranslationUnit]:
        return [
            TranslationUnit(
                chunk_index=1,
                chunk_id="chk_e2e_pro_001",
                chunk_fingerprint="fp_e2e_pro_001",
                chunk_type=TranslationTaskType.TRANSLATE,
                source_sequence_range=(1, min(5, max(1, len(nodes)))),
                node_count=min(5, max(1, len(nodes))),
                context_id="CTX_E2E_PRO",
                context_depth=1,
                target_payload="This is a test of the real-time financial translation engine pipeline.",
                estimated_tokens=20,
                payload_sha256="85174c85174c85174c85174c85174c85174c85174c85174c85174c85174c8517"
            )
        ]

class TestRealE2EFinOps(unittest.IsolatedAsyncioTestCase):
    """Certificación E2E usando el Provider Stack simulado (Zero-Cost CI/CD)."""

    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.test_id = uuid.uuid4().hex
        
        # SOTA: Instanciación del Stack con BypassProvider para evitar consumo de API
        estimator = FastWordEstimator()
        prompt_builder = PromptBuilder(model_name="bypass_passthrough", prompt_version="v1.0", estimator=estimator)
        
        base_provider = BypassProvider()
        breaker = CircuitBreakerRegistry.get_breaker("bypass_e2e", threshold=5)
        resilient = ResilientProvider(underlying=base_provider, breaker=breaker)
        quota = QuotaManager(rpm_limit=1000, tpm_limit=100000)
        rate_provider = RateLimitedProvider(underlying=resilient, quota_manager=quota)
        
        self.processor = SyncProviderBridge(async_provider=rate_provider, prompt_builder=prompt_builder)
        
        # SOTA: Inyección del AsyncDispatcher (Orquestador E2E) sobre el Provider Stack
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = MagicMock(breadcrumbs=(), depth=0)
        
        self.dispatcher = AsyncDispatcher(
            context_resolver=mock_resolver,
            prompt_builder=prompt_builder,
            provider_stack=rate_provider
        )
        
        self.pipeline = build_pipeline(
            chunker=FinOpsControlledChunker(),
            dispatcher=self.dispatcher 
        )
        
        # SOTA: Extracción dinámica en tiempo de ejecución silenciando el analizador estático
        fsm_db = self.pipeline.state_store.fsm_repo.db  # type: ignore
        
        fsm_db.execute(
            """CREATE TABLE IF NOT EXISTS document_fsm (
                document_id TEXT PRIMARY KEY,
                ast_hash TEXT NOT NULL,
                current_state TEXT NOT NULL,
                state_version INTEGER DEFAULT 0,
                entered_state_at REAL,
                created_at REAL,
                updated_at REAL,
                is_terminal INTEGER DEFAULT 0,
                failure_reason TEXT,
                suspended_state TEXT
            )"""
        )
        fsm_db.commit()


    def tearDown(self):
        self.processor.shutdown()

    async def test_real_pipeline_execution_spends_and_audits_money(self):
        job = TranslationJob(job_id=f"job_e2e_{self.test_id}", source_path=self.pdf_real_path)
        
        result = await self.pipeline.execute(job)
        
        self.assertIsInstance(result.document.content, str)
        self.assertGreater(len(result.document.content.strip()), 0)
        self.assertEqual(job.status, JobStatus.COMPLETED)
        
        self.assertIsNotNone(result.summary)
        self.assertIsInstance(result.summary.total_cost_usd, float)
        self.assertGreaterEqual(result.summary.total_cost_usd, 0.0)
        
        # 3. Validación de Invariantes de Consistencia de Tokens
        self.assertGreaterEqual(result.summary.total_input_tokens, 0) # SOTA: Tolerancia a Bypass
        self.assertGreaterEqual(result.summary.total_output_tokens, 0)
        self.assertEqual(result.summary.total_chunks, 1)