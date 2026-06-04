import os
import unittest
from apps.llm_workers.gemini_client import GeminiClient

class TestEmbeddingSmoke(unittest.TestCase):
    """Certificación de transporte de red para el endpoint gemini-embedding-001."""

    def test_isolated_embedding_request(self):
        if not os.environ.get("GEMINI_API_KEY"):
            self.skipTest("GEMINI_API_KEY ausente. Omitiendo smoke test.")

        client = GeminiClient()
        vector = client.embed_text("hello world")
        
        self.assertIsInstance(vector, list)
        self.assertGreater(len(vector), 0, "El vector de embeddings regresó vacío.")
        self.assertIsInstance(vector[0], float)