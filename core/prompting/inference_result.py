# core/prompting/inference_result.py
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class InferenceResult:
    """SOTA: DTO unificado de retorno. Agnóstico del dialecto, formato físico y proveedor."""
    chunk_id: str
    content: str  # Reemplaza 'translated_text' para soportar Judge, OCR, etc.
    input_tokens: int
    output_tokens: int
    latency_ms: float
    finish_reason: str