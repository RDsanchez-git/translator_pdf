import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from core.ast.models import TranslationUnit, TranslatedUnit
from apps.llm_workers.workers import TranslationWorkerProtocol
from core.execution.exceptions import TransientAPIError
from tenacity import RetryCallState

logger = logging.getLogger(__name__)

class ResilientWorkerProxy(TranslationWorkerProtocol):
    """SOTA: Proxy decorador que inyecta Rate Limiting por Semáforo y Tolerancia Exponencial a Fallos."""

    def __init__(self, base_worker: TranslationWorkerProtocol, max_concurrency: int = 5):
        self.base_worker = base_worker
        # 10C.5: Semáforo asíncrono para limitar ráfagas concurrentes (RPM/TPM Control)
        self.semaphore = asyncio.Semaphore(max_concurrency)

    # Función de soporte estática para extraer los atributos de forma segura ante el linter
    @staticmethod
    def _log_retry_attempt(retry_state: RetryCallState) -> None:
        sleep_sec = retry_state.next_action.sleep if retry_state.next_action else 0.0
        error_detail = retry_state.outcome.exception() if retry_state.outcome else "Error transitorio no registrado"
        logger.warning(
            f"Fallo efímero detectado. Reintentando intento nº {retry_state.attempt_number} tras "
            f"{sleep_sec}s... Detalle: {error_detail}"
    )

    # 10C.4: Política de reintento con backoff exponencial estricto ante fallos transitorios
    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TransientAPIError, ConnectionError, asyncio.TimeoutError)),
        before_sleep=_log_retry_attempt  # Corrección exacta: Remoción de .__func__
    )
    async def _execute_with_retry(self, unit: TranslationUnit) -> TranslatedUnit:
        return await self.base_worker.translate(unit)

    async def translate(self, unit: TranslationUnit) -> TranslatedUnit:
        # Adquisición atómica del slot en el semáforo
        async with self.semaphore:
            return await self._execute_with_retry(unit)