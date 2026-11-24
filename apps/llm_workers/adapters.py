import time
import json
import logging
from hashlib import sha256
from groq import AsyncGroq
import groq
import google.generativeai as genai

from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.g3_admission import GPT_OSS_120B, build_groq_request_kwargs
from core.execution.exceptions import (
    TransientAPIError, DialectParsingError, MalformedInferenceResponse,
    G3ExternalEffectNotStartedError,
)

from core.prompting.inference_result import InferenceResult
from core.prompting.dialects.openai_compatible import InferenceDialect
from core.prompting.renderer import PromptRenderer
from core.execution.effect_guard import g3_pre_effect_guard, g3_free_dispatch_permit
from core.utils.telemetry import ctx_task_id, ctx_execution_id
from core.finops.cost_observation import SDK_RESPONSE

logger = logging.getLogger(__name__)

class GroqProvider:
    """SOTA: Puerto Hexagonal. I/O y manejo de red puro."""
    
    def __init__(
        self, 
        api_key: str, 
        dialect: InferenceDialect,
        max_retries: int = 0,
        *, client: AsyncGroq | None = None,
        require_attributed_response: bool = False,
    ):
        self._client = client if client is not None else AsyncGroq(api_key=api_key, max_retries=max_retries)
        self._dialect = dialect
        self._require_attributed_response = require_attributed_response

    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        # Share the exact physical request with the pre-effect admission.
        # max_completion_tokens enforces the requested output reserve on wire.
        kwargs, expected_key = build_groq_request_kwargs(envelope, self._dialect)
        
        start_time = time.monotonic()
        
        try:
            # 3. I/O Puro
            # This is a local SDK entry boundary, not proof of a sent HTTP
            # request, remote application or provider billing. Only G3's
            # correlated route contributes to the PPPR observation contract.
            task_id, execution_id = ctx_task_id.get(), ctx_execution_id.get()
            correlated = g3_pre_effect_guard.get() is not None and task_id != "-" and execution_id != "-"
            permit = g3_free_dispatch_permit.get()
            free = envelope.model_name == GPT_OSS_120B
            if free or permit is not None:
                if permit is None or not correlated:
                    raise G3ExternalEffectNotStartedError(
                        "PPPR_G5_FREE_DISPATCH_PERMIT_REQUIRED", permanent=True,
                    )
                if (not free or self._client.max_retries != 0
                        or str(self._client.base_url).rstrip("/") != "https://api.groq.com/openai/v1"):
                    raise G3ExternalEffectNotStartedError(
                        "PPPR_G5_FREE_TRANSPORT_CONFIGURATION_REJECTED", permanent=True,
                    )
                digest = sha256(json.dumps(
                    kwargs, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                ).encode("utf-8")).hexdigest()
                permit.claim(digest)
            if correlated:
                logger.info("PPPR_G3_CLIENT_SDK_ENTRY", extra={"extra_data": {
                    "task_id": task_id, "execution_id": execution_id,
                    "chunk_id": envelope.chunk_id, "observed_at_ns": time.time_ns(),
                }})
            response = await self._client.chat.completions.create(**kwargs)
            if correlated or self._require_attributed_response or free:
                # Record the observed SDK response before parsing its scientific
                # payload. Missing usage is unavailable, never zero. A response
                # is not an invoice or proof of a unique external application.
                model = getattr(response, "model", None)
                response_id = getattr(response, "id", None)
                usage = getattr(response, "usage", None)
                input_tokens = getattr(usage, "prompt_tokens", None)
                output_tokens = getattr(usage, "completion_tokens", None)
                total_tokens = getattr(usage, "total_tokens", None)
                valid_usage = (
                    type(input_tokens) is int and input_tokens > 0
                    and type(output_tokens) is int and output_tokens >= 0
                    and type(total_tokens) is int and total_tokens == input_tokens + output_tokens
                )
                valid_model = isinstance(model, str) and model == envelope.model_name
                valid_id = isinstance(response_id, str) and bool(response_id.strip())
                if correlated:
                    digest = sha256(json.dumps(
                        kwargs, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                    ).encode("utf-8")).hexdigest()
                    logger.info(SDK_RESPONSE, extra={"extra_data": {
                        "task_id": task_id, "execution_id": execution_id,
                        "chunk_id": envelope.chunk_id, "request_sha256": digest,
                        "observed_at_ns": time.time_ns(),
                        "response_model": model if isinstance(model, str) else None,
                        "response_id": response_id if valid_id else None,
                        "input_tokens": input_tokens if valid_usage else None,
                        "output_tokens": output_tokens if valid_usage else None,
                        "total_tokens": total_tokens if valid_usage else None,
                    }})
                if self._require_attributed_response or free:
                    if not valid_model:
                        raise MalformedInferenceResponse("PPPR_G5_RESPONSE_MODEL_MISMATCH")
                    if not valid_id or not valid_usage:
                        # This is AFTER SDK invocation. Never classify it as
                        # proven no-start or grant a retry based on missing usage.
                        raise MalformedInferenceResponse("PPPR_G5_RESPONSE_ATTRIBUTION_MISSING")
                if free and permit is not None:
                    permit.check_reported_usage(input_tokens, output_tokens)
                    if len(response.choices) != 1 or response.choices[0].finish_reason != "stop":
                        raise MalformedInferenceResponse("PPPR_G5_FREE_RESPONSE_NOT_COMPLETE")
            
            latency = (time.monotonic() - start_time) * 1000
            
            # 4. Reconstrucción de Dominio
            return self._dialect.parse_response(
                raw_response=response,
                chunk_id=envelope.chunk_id,
                latency_ms=latency,
                expected_key=expected_key
            )
            
        except groq.APIStatusError as e:
            if e.status_code >= 500 or e.status_code == 429:
                raise TransientAPIError(f"Groq HTTP {e.status_code}: {str(e)}") from e
            raise TransientAPIError(f"Groq Fatal Error HTTP {e.status_code}: {str(e)}") from e


class GeminiProvider:
    """SOTA: Adaptador restaurado exclusivamente para el entorno de Benchmark Harness."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key) #type: ignore

    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        # 1. Renderizado Lógico
        rendered = PromptRenderer.render(envelope.schema)
        
        start_time = time.monotonic()
        
        try:
            model = genai.GenerativeModel( # type: ignore
                model_name=envelope.model_name,
                system_instruction=rendered.system_text
            )
            
            # SOTA FIX: Usamos un diccionario puro (GenerationConfigDict) 
            # para evadir los problemas de exportación de clases del SDK.
            response = await model.generate_content_async( # type: ignore
                rendered.user_text,
                generation_config={
                    "temperature": 0.0,
                    "response_mime_type": "application/json"
                }
            )
            
            latency = (time.monotonic() - start_time) * 1000
            
            if not response.parts:
                raise MalformedInferenceResponse(f"Gemini API Error: Contenido nulo o bloqueado para el chunk {envelope.chunk_id}.")

            raw_content = response.text
            
            # Extracción estructurada para cumplir el nuevo contrato SOTA
            try:
                parsed_json = json.loads(raw_content)
                extracted_content = parsed_json.get(rendered.expected_output_key)
                if extracted_content is None:
                    raise DialectParsingError(f"Missing expected key '{rendered.expected_output_key}'. Raw: {raw_content}")
            except json.JSONDecodeError as e:
                raise DialectParsingError(f"Gemini hallucinated invalid JSON. Raw: {raw_content}") from e

            usage = response.usage_metadata
            finish_reason = response.candidates[0].finish_reason if response.candidates else None

            return InferenceResult(
                chunk_id=envelope.chunk_id,
                content=str(extracted_content),
                input_tokens=usage.prompt_token_count if usage else 0,
                output_tokens=usage.candidates_token_count if usage else 0,
                latency_ms=latency,
                finish_reason=str(finish_reason.name) if finish_reason else "unknown"
            )
            
        except Exception as e:
            # Captura de errores del SDK subyacente
            raise TransientAPIError(f"Gemini Upstream Error: {str(e)}") from e