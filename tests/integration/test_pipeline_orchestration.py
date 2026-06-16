import unittest
import os
import sqlite3
from datetime import datetime
from typing import List
from core.ast.models import ASTNode, TranslationUnit, TranslatedUnit, TranslationTaskType
from core.pipeline.job import TranslationJob, JobStatus, PipelineStep
from apps.bootstrap.pipeline_factory import build_pipeline
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler
from core.pipeline.state_store import FSMStateStore

class FakeChunker:
    def chunk(self, nodes: List[ASTNode]) -> List[TranslationUnit]:
        return [
            TranslationUnit(
                chunk_index=1, 
                chunk_id="chk_mock_001", 
                chunk_fingerprint="mock_fp_001",
                chunk_type=TranslationTaskType.TRANSLATE,
                source_sequence_range=(1, max(1, len(nodes))), 
                node_count=len(nodes),
                context_id="CTX_ORCH_MOCK", 
                context_depth=1,
                target_payload="Payload extraído del AST real",
                estimated_tokens=150, 
                payload_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            )
        ]

class FakeDispatcher:
    async def dispatch(self, units: List[TranslationUnit]) -> List[TranslatedUnit]:
        return [
            TranslatedUnit(
                chunk_index=u.chunk_index, 
                chunk_id=u.chunk_id, 
                chunk_type=u.chunk_type.value if hasattr(u.chunk_type, "value") else u.chunk_type,
                source_sequence_range=u.source_sequence_range, 
                translated_payload="Texto traducido simulado",
                payload_sha256=u.payload_sha256, 
                model_name="gemini-2.5-flash",
                prompt_version="v3_latex_optimized", 
                input_tokens=120, 
                output_tokens=140, 
                latency_ms=45.2
            ) for u in units
        ]

class TestPipelineOrchestration(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        
        # SOTA: Inicialización de FSM en memoria aislada para tests
        self.db = sqlite3.connect(":memory:")
        self.db.execute("""
            CREATE TABLE document_fsm (
                document_id TEXT,
                ast_hash TEXT,
                current_state TEXT,
                state_version INTEGER DEFAULT 0,
                suspended_state TEXT,
                failure_reason TEXT,
                is_terminal INTEGER DEFAULT 0,
                entered_state_at REAL,
                created_at REAL,
                updated_at REAL
            )
        """)
        repo = FSMRepository(self.db)
        handler = DocumentCommandHandler(repo)
        mock_store = FSMStateStore(repo, handler)

        self.pipeline = build_pipeline(
            chunker=FakeChunker(),
            dispatcher=FakeDispatcher(),
            state_store_override=mock_store
        )

        if not os.path.exists(self.pdf_real_path):
            raise FileNotFoundError(f"Falta el binario de control: {self.pdf_real_path}")

    async def test_pipeline_executes_successfully_with_real_pdf_source(self):
        job = TranslationJob(job_id="job_orch_prod_001", source_path=self.pdf_real_path)
        self.assertEqual(job.status, JobStatus.PENDING)
        result = await self.pipeline.execute(job)
        
        self.assertIsInstance(result.document.content, str)
        self.assertGreater(len(result.document.content.strip()), 0)
        self.assertEqual(job.status, JobStatus.COMPLETED)
        self.assertEqual(job.current_step, PipelineStep.FINISHED)
        self.assertIsNone(job.error_type)
        self.assertIsNotNone(job.audit_summary)
        self.assertEqual(result.summary, job.audit_summary)
        self.assertIsInstance(job.started_at, datetime)
        self.assertIsInstance(job.finished_at, datetime)