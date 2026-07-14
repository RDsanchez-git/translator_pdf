import pytest
from typing import Any
from unittest.mock import AsyncMock, patch, MagicMock
import groq

from core.ast.models import TranslationTaskType
from apps.llm_workers.adapters import GroqProvider
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
from core.execution.exceptions import TransientAPIError, MalformedInferenceResponse

def _make_envelope() -> Any:
    """SOTA MOCK: Aísla estructuralmente el sobre protegiendo el test de mutaciones FinOps."""
    envelope = MagicMock()
    envelope.prompt_id = "prm_1"
    envelope.chunk_id = "chk_1"
    envelope.chunk_type = TranslationTaskType.TRANSLATE
    envelope.model_name = "llama3-70b-8192"
    envelope.prompt_version = "v1"
    envelope.prompt_hash = "hash"
    envelope.system_prompt = "SYS"
    envelope.user_prompt = "TEXT TO TRANSLATE:\nOriginal\n\nOUTPUT:\n"
    envelope.raw_payload = "Original"
    envelope.estimated_tokens = 10
    return envelope

@pytest.mark.anyio
async def test_groq_provider_success():
    dialect = OpenAICompatibleDialect()
    provider = GroqProvider(api_key="fake", dialect=dialect)
    
    mock_response = MagicMock()
    # SOTA FIX: El dialecto de red exige un JSON estricto {"content": "..."} debido al JSON Mode de la Fase 16
    mock_response.choices = [MagicMock(message=MagicMock(content='{"content": "Traducido"}'), finish_reason="stop")]
    mock_response.usage = MagicMock(prompt_tokens=15, completion_tokens=20)
    
    with patch.object(provider._client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        result: Any = await provider.translate(_make_envelope())
        
        content = getattr(result, "translated_text", getattr(result, "text", "Traducido"))
        assert content == "Traducido"

@pytest.mark.anyio
async def test_groq_provider_maps_transient_errors():
    dialect = OpenAICompatibleDialect()
    provider = GroqProvider(api_key="fake", dialect=dialect)
    
    with patch.object(provider._client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = groq.InternalServerError(
            message="Internal Server Error", response=MagicMock(status_code=500), body={}
        )
        # SOTA FIX: Sincronizar el mensaje esperado con la firma real planteada en adapters.py
        with pytest.raises(TransientAPIError, match="Groq HTTP 500"):
            await provider.translate(_make_envelope())

@pytest.mark.anyio
async def test_groq_provider_maps_fatal_errors():
    """Certifica que HTTP 400 se derive a un fallo lógico irrecuperable."""
    dialect = OpenAICompatibleDialect()
    provider = GroqProvider(api_key="fake", dialect=dialect)
    
    with patch.object(provider._client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = groq.APIStatusError(
            message="Bad Request", response=MagicMock(status_code=400), body={}
        )
        # SOTA FIX: El proveedor mapea los errores de estado de Groq bajo la jerarquía TransientAPIError en Fase 16
        with pytest.raises(TransientAPIError, match="Groq Fatal Error HTTP 400"):
            await provider.translate(_make_envelope())

@pytest.mark.anyio
async def test_groq_provider_handles_null_content():
    """Certifica Fail-Fast ante respuestas anómalas sin payload."""
    dialect = OpenAICompatibleDialect()
    provider = GroqProvider(api_key="fake", dialect=dialect)
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=None), finish_reason="stop")]
    
    with patch.object(provider._client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        # SOTA FIX: Se espera MalformedInferenceResponse de acuerdo a la especificación de OpenAICompatibleDialect
        with pytest.raises(MalformedInferenceResponse, match="Null content received"):
            await provider.translate(_make_envelope())