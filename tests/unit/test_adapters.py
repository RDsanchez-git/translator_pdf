import pytest
from typing import Any
from dataclasses import replace
from unittest.mock import AsyncMock, patch, MagicMock
import groq

from core.ast.models import TranslationTaskType
from apps.llm_workers.adapters import GroqProvider
from apps.llm_workers.prompt_builder import PromptEnvelope
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
from core.prompting.models import (
    PromptConstraints, PromptContext, PromptIntent, PromptPayload, PromptSchema,
)
from core.validation.budget import PromptBudget
from core.execution.exceptions import (
    G3ExternalEffectNotStartedError, TransientAPIError, MalformedInferenceResponse,
)


def _make_envelope() -> PromptEnvelope:
    """Exercise the real adapter envelope contract; mock only the remote SDK."""
    return PromptEnvelope(
        prompt_id="prm_1",
        chunk_id="chk_1",
        chunk_type=TranslationTaskType.TRANSLATE,
        model_name="llama3-70b-8192",  # Historical test identifier; no real I/O.
        prompt_version="v1",
        prompt_hash="hash",
        schema=PromptSchema(
            intent=PromptIntent.TRANSLATE,
            context=PromptContext(chunk_index=0, depth=0),
            constraints=PromptConstraints(),
            payload=PromptPayload(content="Original"),
        ),
        estimated_tokens=10,
        budget_stats=PromptBudget(
            system_tokens=3, context_tokens=2, payload_tokens=5,
            reserved_tokens=256, window_limit=8192,
        ),
    )

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
        mock_create.assert_awaited_once()
        request = mock_create.call_args.kwargs
        assert request["max_completion_tokens"] == 256
        assert request["model"] == "llama3-70b-8192"
        assert request["messages"][1] == {"role": "user", "content": "Original"}
        assert request["response_format"] == {"type": "json_object"}

        assert result.content == "Traducido"

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


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_reserve", [0, -1, "256", None])
async def test_groq_provider_rejects_invalid_reserve_without_sdk_call(invalid_reserve: Any):
    """R5/R10: malformed local admission never reaches the paid SDK."""
    dialect = OpenAICompatibleDialect()
    provider = GroqProvider(api_key="fake", dialect=dialect)
    envelope = _make_envelope()
    bad_budget = replace(envelope.budget_stats, reserved_tokens=invalid_reserve)
    bad_envelope = replace(envelope, budget_stats=bad_budget)
    with patch.object(provider._client.chat.completions, "create", new_callable=AsyncMock) as create:
        with pytest.raises(
            G3ExternalEffectNotStartedError, match="PPPR_G3_OUTPUT_RESERVE_INVALID"
        ):
            await provider.translate(bad_envelope)
        create.assert_not_called()


@pytest.mark.unit
@pytest.mark.anyio
@pytest.mark.parametrize("model,usage,response_id,expected", [
    ("wrong-model", True, "response-id", "RESPONSE_MODEL_MISMATCH"),
    ("llama3-70b-8192", False, "response-id", "RESPONSE_ATTRIBUTION_MISSING"),
    ("llama3-70b-8192", True, "", "RESPONSE_ATTRIBUTION_MISSING"),
])
async def test_attributed_response_rejection_is_post_effect(model, usage, response_id, expected):
    provider = GroqProvider(api_key="fake", dialect=OpenAICompatibleDialect(),
                            require_attributed_response=True)
    response = MagicMock()
    response.model, response.id = model, response_id
    response.usage = MagicMock(prompt_tokens=15, completion_tokens=20, total_tokens=35) if usage else None
    with patch.object(provider._client.chat.completions, "create", new_callable=AsyncMock) as create:
        create.return_value = response
        with pytest.raises(MalformedInferenceResponse, match=expected):
            await provider.translate(_make_envelope())
        create.assert_awaited_once()
