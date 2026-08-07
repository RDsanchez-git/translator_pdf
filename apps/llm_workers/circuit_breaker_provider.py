# apps/llm_workers/circuit_breaker_provider.py
"""
Decorador que conecta el GlobalCircuitBreaker existente al Provider Stack.

NADR-08 §5.2 R5: El mecanismo canónico de circuit breaking MUST estar
integrado en el plano de ejecución, interceptando todas las llamadas a
proveedores externos.

GAP-P4-01: El breaker existe en core/resilience/circuit_breaker.py pero
no está conectado al stack. Este decorador lo conecta sin introducir
nueva capacidad funcional. Es puro Production Alignment.
"""

from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import LLMProvider
from core.prompting.inference_result import InferenceResult
from core.resilience.circuit_breaker import GlobalCircuitBreaker


class CircuitBreakerProvider(LLMProvider):
    """
    Decorador de resiliencia. Conecta el breaker existente al stack.
    
    Si el circuito está OPEN, lanza CircuitOpenError sin tocar cache ni cuota.
    Si el circuito está CLOSED, delega al provider subyacente.
    """
    
    def __init__(self, underlying: LLMProvider, breaker: GlobalCircuitBreaker):
        self._underlying = underlying
        self._breaker = breaker
    
    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        """Delega al breaker, que decide si llamar al provider."""
        async def _do_translate():
            return await self._underlying.translate(envelope)
        
        return await self._breaker.call(_do_translate)