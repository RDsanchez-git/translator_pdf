import json
from typing import Any, Dict, Protocol
from core.prompting.renderer import RenderedPrompt
from core.prompting.inference_result import InferenceResult
from core.execution.exceptions import DialectParsingError, MalformedInferenceResponse

class InferenceDialect(Protocol):
    """SOTA: Protocolo unificado de traducción bidireccional (Dominio <-> Red)."""
    def build_request_kwargs(self, rendered: RenderedPrompt) -> Dict[str, Any]: ...
    def parse_response(self, raw_response: Any, chunk_id: str, latency_ms: float, expected_key: str) -> InferenceResult: ...

class OpenAICompatibleDialect(InferenceDialect):
    """SOTA: Dialecto estándar para Groq, OpenAI, Mistral, vLLM, Together."""
    
    def __init__(self, use_json_mode: bool = True):
        self._use_json_mode = use_json_mode

    def build_request_kwargs(self, rendered: RenderedPrompt) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "messages": [
                {"role": "system", "content": rendered.system_text},
                {"role": "user", "content": rendered.user_text}
            ]
        }
        if self._use_json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        return kwargs

    def parse_response(self, raw_response: Any, chunk_id: str, latency_ms: float, expected_key: str) -> InferenceResult:
        try:
            choice = raw_response.choices[0]
            raw_content = choice.message.content
            
            if raw_content is None:
                raise MalformedInferenceResponse(f"Null content received for chunk {chunk_id}.")

            # Extracción dinámica basada en el contrato del Renderer
            if self._use_json_mode:
                try:
                    parsed_json = json.loads(raw_content)
                    extracted_content = parsed_json.get(expected_key)
                    if extracted_content is None:
                        raise DialectParsingError(f"Missing expected key '{expected_key}'. Raw: {raw_content}")
                except json.JSONDecodeError as e:
                    raise DialectParsingError(f"LLM hallucinated invalid JSON. Raw: {raw_content}") from e
            else:
                extracted_content = raw_content

            usage = raw_response.usage
            
            return InferenceResult(
                chunk_id=chunk_id,
                content=str(extracted_content),
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                latency_ms=latency_ms,
                finish_reason=choice.finish_reason
            )
        except (IndexError, AttributeError) as e:
            raise MalformedInferenceResponse(f"Unexpected API response shape: {raw_response}") from e