from typing import Dict, Optional, Protocol
from enum import Enum, auto
from dataclasses import dataclass
from core.ast.models import TranslationTaskType
from apps.llm_workers.prompt_builder import PromptEnvelope

# ==============================================================================
# Contratos de Red (DTOs y Protocolos)
# ==============================================================================

@dataclass(frozen=True, slots=True)
class ProviderResult:
    """SOTA: Salida estandarizada de red, independiente del SDK del proveedor."""
    chunk_id: str
    translated_text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    finish_reason: str

class LLMProvider(Protocol):
    """SOTA: Interfaz pura de inversión de dependencias para la capa de inferencia."""
    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        ...

# ==============================================================================
# Estrategias y Ruteo
# ==============================================================================

class ProviderStrategy(Enum):
    """SOTA: Estrategias de despacho disponibles en la infraestructura (V1)."""
    GROQ_HEAVY = auto()  # Modelos de alto razonamiento (ej. llama-3-70b)
    GROQ_LIGHT = auto()  # Modelos de alta velocidad/costo bajo (ej. mixtral-8x7b)
    BYPASS = auto()      # Resolución inmediata en memoria (Latencia 0)

# Tabla de verdad inmutable por defecto
DEFAULT_ROUTING_TABLE: Dict[TranslationTaskType, ProviderStrategy] = {
    TranslationTaskType.TRANSLATE: ProviderStrategy.GROQ_HEAVY,
    TranslationTaskType.PARTIAL: ProviderStrategy.GROQ_LIGHT,
    TranslationTaskType.PRESERVE: ProviderStrategy.BYPASS,
}

class TranslationStrategyRouter:
    """SOTA: Orquestador estático O(1) de políticas de despacho LLM."""
    
    def __init__(self, routing_table: Optional[Dict[TranslationTaskType, ProviderStrategy]] = None):
        self.routing_table = routing_table if routing_table is not None else DEFAULT_ROUTING_TABLE

    def route(self, task_type: TranslationTaskType) -> ProviderStrategy:
        """Asigna la estrategia óptima de infraestructura basada en el contrato topológico."""
        try:
            return self.routing_table[task_type]
        except KeyError:
            # Fail-Fast: Previene que tipos anómalos o futuros (ej. GLOSSARY) 
            # deriven silenciosamente en consumo no planificado de red.
            raise ValueError(f"UNSUPPORTED_TASK_TYPE: No existe política de ruteo definida para '{task_type}'")