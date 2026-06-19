import asyncio
import logging
from tenacity import AsyncRetrying, stop_after_attempt, wait_random_exponential, retry_if_exception_type

from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import ProviderResult, LLMProvider
from core.resilience.circuit_breaker import GlobalCircuitBreaker
from core.execution.exceptions import TransientAPIError

logger = logging.getLogger(__name__)

class ResilientProvider:
    """SOTA: Decorador final del pipeline encargado de unificar Deadlines, Retries y Circuit Breaking."""
    
    def __init__(self, underlying: LLMProvider, breaker: GlobalCircuitBreaker, timeout_seconds: float = 45.0):
        self._underlying = underlying
        self._breaker = breaker
        self._timeout = timeout_seconds

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        # Configuración de reintentos exponenciales con Jitter aleatorio integrado de Tenacity
        retry_strategy = AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_random_exponential(multiplier=1, max=10),
            retry=retry_if_exception_type(TransientAPIError),
            reraise=True
        )

        # Encapsulación de la llamada de red dentro del comportamiento del Circuit Breaker refactorizado
        return await self._breaker.call(
            self._execute_with_deadline, retry_strategy, envelope
        )

    async def _execute_with_deadline(self, retry_strategy: AsyncRetrying, envelope: PromptEnvelope) -> ProviderResult:
        """Aplica la estrategia de reintentos y corta sockets colgados mediante asyncio.wait_for."""
        async for attempt in retry_strategy:
            with attempt:
                try:
                    return await asyncio.wait_for(
                        self._underlying.translate(envelope),
                        timeout=self._timeout
                    )
                except asyncio.TimeoutError as e:
                    logger.warning(f"Timeout de {self._timeout}s alcanzado en el chunk {envelope.chunk_id}.")
                    raise TransientAPIError(f"LLM Upstream Timeout final tras {self._timeout}s") from e

        # SOTA: Barrera inalcanzable requerida exclusivamente por el analizador de tipos estático.
        # Tenacity (reraise=True) siempre elevará la excepción antes de que el bucle se agote de forma pacífica.
        raise RuntimeError("Unreachable: La estrategia de reintentos finalizó sin retornar ni lanzar excepción.")