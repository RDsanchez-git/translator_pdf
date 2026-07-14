import asyncio
import os
import tempfile
import pytest
from typing import Any
from unittest.mock import MagicMock
from core.ast.models import TranslationTaskType
from apps.llm_workers.cache_provider import CachedLLMProvider

class MockLowLevelProvider:
    def __init__(self):
        self.calls = 0
        self.lock = asyncio.Lock()

    async def translate(self, envelope: Any) -> Any:
        async with self.lock:
            self.calls += 1
        # Simula latencia real de red para facilitar la detección de la condición de carrera
        await asyncio.sleep(0.05)
        
        mock_res = MagicMock()
        mock_res.chunk_id = getattr(envelope, "chunk_id", "chk_1")
        mock_res.translated_text = "TRANSLATED::Text"
        mock_res.text = "TRANSLATED::Text"
        mock_res.content = "TRANSLATED::Text"
        mock_res.translated_payload = "TRANSLATED::Text"
        mock_res.finish_reason = "stop"
        return mock_res

@pytest.fixture
def temp_db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.remove(path)

@pytest.mark.anyio
async def test_cache_stampede_prevention(temp_db_path):
    """Certifica que 100 peticiones simultáneas idénticas generen solo 1 llamada de red."""
    mock_network = MockLowLevelProvider()
    provider = CachedLLMProvider(underlying=mock_network, db_path=temp_db_path)
    await provider.initialize()

    # SOTA FIX: Uso de Mocks dinámicos para aislar las aserciones de la caché de las firmas de PromptEnvelope
    tasks = []
    for i in range(100):
        mock_envelope = MagicMock()
        mock_envelope.prompt_id = f"prm_{i}"
        mock_envelope.chunk_id = f"chk_{i}"
        mock_envelope.chunk_type = TranslationTaskType.TRANSLATE
        mock_envelope.model_name = "model"
        mock_envelope.prompt_version = "v1"
        mock_envelope.prompt_hash = "STAMPEDE_HASH"
        mock_envelope.estimated_tokens = 5
        
        tasks.append(provider.translate(mock_envelope))

    results = await asyncio.gather(*tasks)

    assert len(results) == 100
    assert mock_network.calls == 1, f"Fallo Crítico: Ocurrió un Cache Stampede. Llamadas: {mock_network.calls}"
    assert provider.metrics["cache_misses"] == 1
    assert provider.metrics["cache_hits"] == 99
    assert provider.metrics["cache_writes"] == 1

@pytest.mark.anyio
async def test_cache_fault_tolerance(temp_db_path):
    """Certifica que un fallo SQL no tumba el pipeline de traducción."""
    mock_network = MockLowLevelProvider()
    provider = CachedLLMProvider(underlying=mock_network, db_path=temp_db_path)
    await provider.initialize()

    provider._db_path = "/path/invalido/que/no/existe.db"

    mock_envelope = MagicMock()
    mock_envelope.prompt_id = "prm_1"
    mock_envelope.chunk_id = "chk_1"
    mock_envelope.chunk_type = TranslationTaskType.TRANSLATE
    mock_envelope.model_name = "model"
    mock_envelope.prompt_version = "v1"
    mock_envelope.prompt_hash = "hash_fail"
    mock_envelope.estimated_tokens = 5

    result = await provider.translate(mock_envelope)
    
    finish_reason = getattr(result, "finish_reason", "stop")
    assert finish_reason == "stop"
    assert provider.metrics["cache_write_failures"] == 1