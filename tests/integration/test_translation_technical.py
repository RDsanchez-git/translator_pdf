import unittest
import os
import json
from core.pipeline.job import TranslationJob
from apps.bootstrap.pipeline_factory import build_pipeline
from tests.helpers.fakes import FakeChunker, FakeDispatcher
from tests.helpers.markdown_inspector import MarkdownInspector

class TestTranslationTechnical(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pdf_real_path = "tests/fixtures/sample_3_pages.pdf"
        self.golden_path = "tests/golden/sample_3_pages.latex.json"
        self.pipeline = build_pipeline(chunker=FakeChunker(), dispatcher=FakeDispatcher())

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