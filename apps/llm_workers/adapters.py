import time
import logging
from groq import AsyncGroq
import groq

from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import ProviderResult
from core.execution.exceptions import TransientAPIError

logger = logging.getLogger(__name__)

class BypassProvider:
    """SOTA: Adaptador simulado para TranslationTaskType.PRESERVE. Costo 0, Latencia 0."""
    
    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        # Extracción directa SOTA. Inmune a mutaciones del prompt engineering.
        return ProviderResult(
            chunk_id=envelope.chunk_id,
            translated_text=envelope.raw_payload,
            input_tokens=0,
            output_tokens=0,
            latency_ms=0.0,
            finish_reason="bypass_passthrough"
        )

class GroqProvider:
    """SOTA: Adaptador físico para la API de Groq con mapeo estricto de excepciones y validación de nulidad."""
    
    def __init__(self, api_key: str, max_retries: int = 0):
        self._client = AsyncGroq(api_key=api_key, max_retries=max_retries)

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        start_time = time.monotonic()
        
        try:
            response = await self._client.chat.completions.create(
                messages=[
                    {"role": "system", "content": envelope.system_prompt},
                    {"role": "user", "content": envelope.user_prompt}
                ],
                model=envelope.model_name,
                temperature=0.0,
                stream=False
            )
            
            latency = (time.monotonic() - start_time) * 1000
            choice = response.choices[0]
            content = choice.message.content
            
            # SOTA Fail-Fast: Prevención de propagación de nulos (ej. tool calls inesperados)
            if content is None:
                raise ValueError(f"Groq API Error: Contenido nulo devuelto para el chunk {envelope.chunk_id}.")

            usage = response.usage
            
            return ProviderResult(
                chunk_id=envelope.chunk_id,
                translated_text=content,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                latency_ms=latency,
                finish_reason=choice.finish_reason
            )
            
        except (groq.APIConnectionError, groq.RateLimitError, groq.InternalServerError) as e:
            raise TransientAPIError(f"Groq Upstream Error: {str(e)}") from e
        except groq.APIStatusError as e:
            if e.status_code >= 500 or e.status_code == 429:
                raise TransientAPIError(f"Groq HTTP {e.status_code}: {str(e)}") from e
            raise ValueError(f"Groq Fatal Error HTTP {e.status_code}: {str(e)}") from e