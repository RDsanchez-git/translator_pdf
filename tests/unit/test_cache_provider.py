import asyncio
import os
import tempfile
import pytest
from core.ast.models import TranslationTaskType
from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import ProviderResult
from apps.llm_workers.cache_provider import CachedLLMProvider

class MockLowLevelProvider:
    def __init__(self):
        self.calls = 0
        self.lock = asyncio.Lock()

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        async with self.lock:
            self.calls += 1
        # Simula latencia real de red para facilitar la detección de la condición de carrera
        await asyncio.sleep(0.05)
        return ProviderResult(
            chunk_id=envelope.chunk_id,
            translated_text=f"TRANSLATED::{envelope.user_prompt.strip()}",
            input_tokens=10, output_tokens=15, latency_ms=50.0, finish_reason="stop"
        )

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

    # Disparar 100 tareas concurrentes exactas (Dogpile Effect inducido)
    tasks = [
        provider.translate(
            PromptEnvelope(
                prompt_id=f"prm_{i}", chunk_id=f"chk_{i}", chunk_type=TranslationTaskType.TRANSLATE,
                model_name="model", prompt_version="v1", prompt_hash="STAMPEDE_HASH",
                system_prompt="sys", user_prompt="Text", estimated_tokens=5,
                raw_payload="Original",
            )
        )
        for i in range(100)
    ]

    results = await asyncio.gather(*tasks)

    # Aserciones de Nivel Producción
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

    # Corrompemos el path internamente para forzar un OperationalError
    provider._db_path = "/path/invalido/que/no/existe.db"

    envelope = PromptEnvelope(
        prompt_id="prm_1", chunk_id="chk_1", chunk_type=TranslationTaskType.TRANSLATE,
        model_name="model", prompt_version="v1", prompt_hash="hash_fail",
        system_prompt="sys", user_prompt="Text", estimated_tokens=5,
        raw_payload="Original",
    )

    result = await provider.translate(envelope)
    
    assert result.finish_reason == "stop"
    assert provider.metrics["cache_write_failures"] == 1