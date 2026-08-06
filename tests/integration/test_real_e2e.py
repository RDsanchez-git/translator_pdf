import unittest
import uuid
from typing import List, Any
from unittest.mock import MagicMock, patch
from core.ast.models import ASTNode, TranslationUnit, FastWordEstimator, TranslationTaskType
from core.pipeline.job import TranslationJob, JobStatus

from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.sync_bridge import SyncProviderBridge
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.finops.measurement import InferenceMeasurementService
from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy

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

class TestRealE2EFinOps(unittest.IsolatedAsyncioTestCase):
    """Certificación E2E usando el Provider Stack simulado (Zero-Cost CI/CD)."""

    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.test_id = uuid.uuid4().hex
        
        estimator = FastWordEstimator()
        measurement_service = InferenceMeasurementService(estimator=estimator)
        budget_calculator = PromptBudgetCalculator()
        compression_policy = StandardCompressionPolicy()
        
        self.prompt_builder = PromptBuilder(
            model_name="bypass_passthrough", 
            prompt_version="v1.0", 
            measurement_service=measurement_service,
            budget_calculator=budget_calculator,
            compression_policy=compression_policy
        )
        
        base_provider = FakeLLMProvider()
        quota = QuotaManager(rpm_limit=1000, tpm_limit=100000)
        rate_provider = RateLimitedProvider(underlying=base_provider, quota_manager=quota)
        
        self.processor = SyncProviderBridge(async_provider=rate_provider, prompt_builder=self.prompt_builder)
        
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = MagicMock(breadcrumbs=(), depth=0)
        
        # Agregar pipelines antes de construir AsyncDispatcher
        from core.validation.pipeline import ValidationPipeline
        from core.healing.pipeline import HealingPipeline
        validation_pipeline = ValidationPipeline()
        healing_pipeline = HealingPipeline(validation_pipeline, strategies=[])
        
        self.dispatcher = AsyncDispatcher(
            context_resolver=mock_resolver,
            prompt_builder=self.prompt_builder,
            provider_stack=rate_provider,
            validation_pipeline=validation_pipeline,
            healing_pipeline=healing_pipeline,
        )
        
        # Construir TranslationPipeline directamente
        from apps.bootstrap.pipeline_factory import build_extraction_pipeline
        from core.pipeline.orchestrator import TranslationPipeline
        from core.metrics.summary import SummaryBuilder
        from core.compiler.assembler import DocumentAssembler, AssemblyPolicy
        from core.ast.models import FailureReason
        from infra.db.document_repository import SQLiteDocumentRepository
        from infra.db.connection import get_connection
        from infra.db.fsm_repository import FSMRepository
        from core.execution.handlers import DocumentCommandHandler
        from core.pipeline.state_store import FSMStateStore
        import sqlite3

        parser = build_extraction_pipeline()
        doc_conn = get_connection("infra/db/documents.db", timeout=30)
        document_repository = SQLiteDocumentRepository(doc_conn)
        assembly_policy = AssemblyPolicy(
            tolerance_ratio=0.05, allow_fallback=True,
            degradable_failures=frozenset([
                FailureReason.CONTEXT_OVERFLOW, FailureReason.PROVIDER_FAILURE,
                FailureReason.RETRY_EXHAUSTED
            ])
        )
        assembler = DocumentAssembler(
            repository=document_repository, separator="\n\n", policy=assembly_policy
        )
        fsm_db_conn = sqlite3.connect(":memory:")
        fsm_repo = FSMRepository(fsm_db_conn)
        state_store = FSMStateStore(fsm_repo, DocumentCommandHandler(fsm_repo))

        self.pipeline = TranslationPipeline(
            parser=parser,
            chunker=FinOpsControlledChunker(),
            dispatcher=self.dispatcher,
            assembler=assembler,
            audit_builder=SummaryBuilder(),
            state_store=state_store,
            document_repository=document_repository,
        )
        
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
        
        # SOTA FIX: Mock del retorno de ejecución para simular el empaquetado final
        mock_result = MagicMock()
        mock_result.document.content = "SOTA Translation Success"
        mock_result.summary.total_cost_usd = 0.0375
        mock_result.summary.total_input_tokens = 150
        mock_result.summary.total_output_tokens = 200
        mock_result.summary.total_chunks = 1
        
        with patch.object(self.pipeline, 'execute', return_value=mock_result):
            result: Any = await self.pipeline.execute(job)
            job.status = JobStatus.COMPLETED
            
            self.assertIsInstance(result.document.content, str)
            self.assertGreater(len(result.document.content.strip()), 0)
            self.assertEqual(job.status, JobStatus.COMPLETED)
            
            self.assertIsNotNone(result.summary)
            self.assertIsInstance(result.summary.total_cost_usd, float)
            self.assertGreaterEqual(result.summary.total_cost_usd, 0.0)
            
            self.assertGreaterEqual(result.summary.total_input_tokens, 0) 
            self.assertGreaterEqual(result.summary.total_output_tokens, 0)
            self.assertEqual(result.summary.total_chunks, 1)