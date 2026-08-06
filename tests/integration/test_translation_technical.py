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

class TestTranslationTechnical(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.golden_path = "tests/golden/sample_3_pages.latex.json"

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

    async def test_latex_token_sets_and_balances(self):
        if not os.path.exists(self.golden_path):
            self.skipTest("Molde técnico ausente. Ejecute el script de captura primero.")

        job = TranslationJob(job_id="job_gold_tech", source_path=self.pdf_real_path)
        result = await self.pipeline.execute(job)

        runtime_tokens = MarkdownInspector.extract_technical_tokens(result.document.content)
        runtime_balances = MarkdownInspector.verify_balances(result.document.content)

        with open(self.golden_path, "r", encoding="utf-8") as f:
            expected = json.load(f)

        for token_type in ["labels", "refs", "eqrefs", "cites"]:
            self.assertEqual(set(runtime_tokens[token_type]), set(expected[token_type]), f"Regresión de Token: '{token_type}'")

        for balance_key in ["braces_balanced", "brackets_balanced", "environments_balanced"]:
            self.assertTrue(runtime_balances[balance_key], f"LaTeX Desbalanceado: '{balance_key}'")