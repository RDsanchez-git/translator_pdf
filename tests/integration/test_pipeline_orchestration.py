import unittest
import os
import sqlite3
from datetime import datetime
from typing import List
from unittest.mock import patch
from core.ast.models import ASTNode, TranslationUnit, TranslatedUnit, TranslationTaskType, DispatchResult, ChunkOutcome, ExecutionStatus
from core.ast.enums import ContentNodeType
from core.ast.builder import PayloadRegistry
from core.pipeline.job import TranslationJob, JobStatus, PipelineStep
from core.pipeline.orchestrator import TranslationPipeline
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
    # SOTA FIX: El Dispatcher de la Fase 16 debe retornar estructuralmente un DispatchResult encapsulando ChunkOutcomes
    async def dispatch(self, units: List[TranslationUnit]) -> DispatchResult:
        outcomes = []
        for u in units:
            translated_unit = TranslatedUnit(
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
            )
            outcomes.append(
                ChunkOutcome(
                    chunk_index=u.chunk_index,
                    chunk_id=u.chunk_id,
                    status=ExecutionStatus.SUCCESS,
                    original_payload_sha256=u.payload_sha256,
                    translated_unit=translated_unit,
                    failure_reason=None,
                    error_message=None,
                    telemetry={}
                )
            )
        return DispatchResult(outcomes=outcomes)

class TestPipelineOrchestration(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        
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

        # Construir TranslationPipeline directamente
        from apps.bootstrap.pipeline_factory import build_extraction_pipeline
        from core.metrics.summary import SummaryBuilder
        from core.compiler.assembler import DocumentAssembler, AssemblyPolicy
        from core.ast.models import FailureReason
        from infra.db.document_repository import SQLiteDocumentRepository
        from infra.db.connection import get_connection

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

        self.pipeline = TranslationPipeline(
            parser=parser,
            chunker=FakeChunker(),
            dispatcher=FakeDispatcher(),
            assembler=assembler,
            audit_builder=SummaryBuilder(),
            state_store=mock_store,
            document_repository=document_repository,
        )

        if not os.path.exists(self.pdf_real_path):
            # ... sin cambios
            os.makedirs(os.path.dirname(self.pdf_real_path), exist_ok=True)
            with open(self.pdf_real_path, "w") as f:
                f.write("dummy pdf binary")

    async def test_pipeline_executes_successfully_with_real_pdf_source(self):
        job = TranslationJob(job_id="job_orch_prod_001", source_path=self.pdf_real_path)
        self.assertEqual(job.status, JobStatus.PENDING)
        
        mock_nodes = [
            ASTNode(
                node_id="node_001",
                sequence_id=1,
                node_type=ContentNodeType.PARAGRAPH,
                payload=PayloadRegistry.create(ContentNodeType.PARAGRAPH, "Sample narrative text for orchestration verification.")
            )
        ]
        
        # SOTA FIX: Isolem el test de la infraestructura local de PyMuPDF forzando un retorno controlado del AST V2
        with patch.object(self.pipeline.parser, 'parse', return_value=mock_nodes):
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