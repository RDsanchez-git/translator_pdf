import os
import unittest
from apps.llm_workers.adapters import GroqProvider
from apps.llm_workers.prompt_builder import PromptEnvelope
from core.ast.models import TranslationTaskType

class TestProviderSmoke(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación de transporte de red asíncrono para el nuevo stack."""

    async def test_isolated_generation_request(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            self.skipTest("GROQ_API_KEY ausente. Omitiendo smoke test.")

        provider = GroqProvider(api_key=api_key)
        
        # SOTA: Instanciación rigurosa cumpliendo todos los slots inmutables
        envelope = PromptEnvelope(
            prompt_id="smoke_prompt_001",
            chunk_id="smoke_test_001",
            chunk_type=TranslationTaskType.TRANSLATE,
            model_name="llama3-8b-8192",
            prompt_version="v1.0",
            prompt_hash="dummy_hash_12345",
            system_prompt="You are a network test bot.",
            user_prompt="Respond exactly with the word 'OK'",
            raw_payload="Respond exactly with the word 'OK'",
            estimated_tokens=10
        )
        
        # Validación de I/O directo contra la API
        result = await provider.translate(envelope)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result.translated_text, str)
        self.assertGreater(len(result.translated_text), 0)
        self.assertIn("OK", result.translated_text.upper())