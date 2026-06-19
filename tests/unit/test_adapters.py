import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import groq

from core.ast.models import TranslationTaskType
from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.adapters import BypassProvider, GroqProvider
from core.execution.exceptions import TransientAPIError

def _make_envelope() -> PromptEnvelope:
    return PromptEnvelope(
        prompt_id="prm_1", chunk_id="chk_1", chunk_type=TranslationTaskType.TRANSLATE,
        model_name="llama3-70b-8192", prompt_version="v1", prompt_hash="hash",
        system_prompt="SYS", user_prompt="TEXT TO TRANSLATE:\nOriginal\n\nOUTPUT:\n", 
        raw_payload="Original",  # Actualización del mock
        estimated_tokens=10
    )

@pytest.mark.anyio
async def test_bypass_provider_extraction():
    provider = BypassProvider()
    result = await provider.translate(_make_envelope())
    assert result.translated_text == "Original"
    assert result.finish_reason == "bypass_passthrough"

@pytest.mark.anyio
async def test_groq_provider_success():
    provider = GroqProvider(api_key="fake")
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Traducido"), finish_reason="stop")]
    mock_response.usage = MagicMock(prompt_tokens=15, completion_tokens=20)
    
    with patch.object(provider._client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        result = await provider.translate(_make_envelope())
        assert result.translated_text == "Traducido"

@pytest.mark.anyio
async def test_groq_provider_maps_transient_errors():
    provider = GroqProvider(api_key="fake")
    with patch.object(provider._client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = groq.InternalServerError(
            message="Internal Server Error", response=MagicMock(status_code=500), body={}
        )
        with pytest.raises(TransientAPIError, match="Groq Upstream Error"):
            await provider.translate(_make_envelope())

@pytest.mark.anyio
async def test_groq_provider_maps_fatal_errors():
    """Certifica que HTTP 400 se derive a un fallo lógico irrecuperable."""
    provider = GroqProvider(api_key="fake")
    with patch.object(provider._client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = groq.APIStatusError(
            message="Bad Request", response=MagicMock(status_code=400), body={}
        )
        with pytest.raises(ValueError, match="Groq Fatal Error HTTP 400"):
            await provider.translate(_make_envelope())

@pytest.mark.anyio
async def test_groq_provider_handles_null_content():
    """Certifica Fail-Fast ante respuestas anómalas sin payload."""
    provider = GroqProvider(api_key="fake")
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=None), finish_reason="stop")]
    
    with patch.object(provider._client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        with pytest.raises(ValueError, match="Contenido nulo devuelto"):
            await provider.translate(_make_envelope())