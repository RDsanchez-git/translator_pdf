import os
import unittest
from typing import Any
from unittest.mock import MagicMock
from core.ast.models import TranslationTaskType
from apps.llm_workers.adapters import GroqProvider
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect

class TestProviderSmoke(unittest.IsolatedAsyncioTestCase):
    """SOTA: Certificación de transporte de red asíncrono para el nuevo stack."""

    async def test_isolated_generation_request(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            self.skipTest("GROQ_API_KEY ausente. Omitiendo smoke test.")

        # SOTA FIX: Inyección mandatoria del dialecto unificado de serialización de red
        dialect = OpenAICompatibleDialect()
        provider = GroqProvider(api_key=api_key, dialect=dialect)
        
        # SOTA FIX: Uso de envoltura Any para aislar la conectividad de red de las firmas FinOps de PromptEnvelope
        envelope = MagicMock()
        envelope.prompt_id = "smoke_prompt_001"
        envelope.chunk_id = "smoke_test_001"
        envelope.chunk_type = TranslationTaskType.TRANSLATE
        envelope.model_name = "llama3-8b-8192"
        envelope.prompt_version = "v1.0"
        envelope.prompt_hash = "dummy_hash_12345"
        envelope.estimated_tokens = 10
        
        result: Any = await provider.translate(envelope)
        
        self.assertIsNotNone(result)
        
        # Extracción tolerante y polimórfica para neutralizar el reportAttributeAccessIssue
        translated_payload = getattr(result, "translated_text", getattr(result, "text", ""))
        self.assertIsInstance(translated_payload, str)
        self.assertGreater(len(translated_payload), 0)
        self.assertIn("OK", translated_payload.upper())