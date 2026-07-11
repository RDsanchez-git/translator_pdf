import time
import logging
from groq import AsyncGroq
import groq
import google.generativeai as genai

from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import ProviderResult
from core.execution.exceptions import TransientAPIError

from core.prompting.inference_result import InferenceResult
from core.prompting.dialects.openai_compatible import InferenceDialect
from core.prompting.renderer import PromptRenderer

logger = logging.getLogger(__name__)

class GroqProvider:
    """SOTA: Puerto Hexagonal. I/O y manejo de red puro."""
    
    def __init__(
        self, 
        api_key: str, 
        dialect: InferenceDialect,
        max_retries: int = 0
    ):
        self._client = AsyncGroq(api_key=api_key, max_retries=max_retries)
        self._dialect = dialect

    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        # 1. Renderizado Lógico (A moverse en Fase 17 fuera del Provider)
        rendered = PromptRenderer.render(envelope.schema)
        
        # 2. Construcción Física
        kwargs = self._dialect.build_request_kwargs(rendered)
        
        start_time = time.monotonic()
        
        try:
            # 3. I/O Puro
            response = await self._client.chat.completions.create(
                model=envelope.model_name,
                temperature=1e-5,
                stream=False,
                **kwargs
            )
            
            latency = (time.monotonic() - start_time) * 1000
            
            # 4. Reconstrucción de Dominio
            return self._dialect.parse_response(
                raw_response=response,
                chunk_id=envelope.chunk_id,
                latency_ms=latency,
                expected_key=rendered.expected_output_key
            )
            
        except groq.APIStatusError as e:
            if e.status_code >= 500 or e.status_code == 429:
                raise TransientAPIError(f"Groq HTTP {e.status_code}: {str(e)}") from e
            raise TransientAPIError(f"Groq Fatal Error HTTP {e.status_code}: {str(e)}") from e

#falta actualizar el gemini.
class GeminiProvider:
    """SOTA: Adaptador restaurado exclusivamente para el entorno de Benchmark Harness."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key) #type: ignore

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        start_time = time.monotonic()
        
        try:
            model = genai.GenerativeModel(#type: ignore
                model_name=envelope.model_name,
                system_instruction=envelope.system_prompt
            )
            
            response = await model.generate_content_async(
                envelope.user_prompt,
                generation_config=genai.GenerationConfig(temperature=0.0) #type: ignore
            )
            
            latency = (time.monotonic() - start_time) * 1000
            
            if not response.parts:
                raise ValueError(f"Gemini API Error: Contenido nulo o bloqueado para el chunk {envelope.chunk_id}.")

            usage = response.usage_metadata
            finish_reason = response.candidates[0].finish_reason if response.candidates else None

            return ProviderResult(
                chunk_id=envelope.chunk_id,
                translated_text=response.text,
                input_tokens=usage.prompt_token_count if usage else 0,
                output_tokens=usage.candidates_token_count if usage else 0,
                latency_ms=latency,
                finish_reason=str(finish_reason.name) if finish_reason else "unknown"
            )
            
        except Exception as e:
            raise TransientAPIError(f"Gemini Upstream Error: {str(e)}") from e