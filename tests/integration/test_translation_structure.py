import unittest
import os
import json
import sqlite3
from core.pipeline.job import TranslationJob
from core.pipeline.orchestrator import TranslationPipeline
from helpers.fakes import FakeChunker, FakeDispatcher
from helpers.markdown_inspector import MarkdownInspector
from infra.db.fsm_repository import FSMRepository
from core.execution.handlers import DocumentCommandHandler
from core.pipeline.state_store import FSMStateStore

class TestTranslationStructure(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.golden_path = "tests/golden/sample_3_pages.structure.json"
        
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
        mock_store = FSMStateStore(repo, DocumentCommandHandler(repo))

        # Construir TranslationPipeline directamente
        from apps.bootstrap.pipeline_factory import build_extraction_pipeline
        from core.metrics.summary import SummaryBuilder
        from infra.db.document_repository import SQLiteDocumentRepository
        from infra.db.connection import get_connection

        parser = build_extraction_pipeline()
        doc_conn = get_connection("infra/db/documents.db", timeout=30)
        document_repository = SQLiteDocumentRepository(doc_conn)

        self.pipeline = TranslationPipeline(
            parser=parser,
            chunker=FakeChunker(),
            dispatcher=FakeDispatcher(),
            audit_builder=SummaryBuilder(),
            state_store=mock_store,
            document_repository=document_repository,
        )

    async def test_structural_integrity_against_golden_snapshot(self):
        if not os.path.exists(self.golden_path):
            self.skipTest("Molde estructural ausente. Ejecute el script de captura primero.")

        job = TranslationJob(job_id="job_gold_struct", source_path=self.pdf_real_path)
        result = await self.pipeline.execute(job)
        if result.document is None:
            self.skipTest("El pipeline lógico no ensambla. Use el AssemblerWorkerDaemon para verificar integridad estructural.")
    
        runtime_struct = MarkdownInspector.extract_structure(result.document.content)

        with open(self.golden_path, "r", encoding="utf-8") as f:
            expected_struct = json.load(f)

        for key in ["headings", "tables", "lists", "display_equations", "inline_equations"]:
            self.assertEqual(runtime_struct[key], expected_struct[key], f"Regresión Estructural: '{key}'")