import asyncio
import logging
import random
import time
from typing import Protocol
from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import ProviderResult, LLMProvider

logger = logging.getLogger(__name__)

class ClockProtocol(Protocol):
    """SOTA: Abstracción del tiempo para determinismo estricto en pruebas."""
    def now(self) -> float:
        ...

class SystemClock:
    def now(self) -> float:
        return time.monotonic()

class TokenBucket:
    """Implementación matemática pura del Token Bucket."""
    def __init__(self, capacity: float, refill_rate_per_second: float, clock: ClockProtocol):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate_per_second)
        self.clock = clock
        self.tokens = float(capacity)
        self.last_update = self.clock.now()

    def _refill(self) -> None:
        now = self.clock.now()
        delta = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + (delta * self.refill_rate))
        self.last_update = now

    def get_wait_time(self, requested_tokens: float) -> float:
        self._refill()
        if self.tokens >= requested_tokens:
            return 0.0
        deficit = requested_tokens - self.tokens
        return deficit / self.refill_rate

    def consume(self, requested_tokens: float) -> None:
        self._refill()
        self.tokens -= requested_tokens

class QuotaManager:
    """SOTA: Gestor de estado centralizado para compartir cuotas entre instancias."""
    def __init__(self, rpm_limit: int, tpm_limit: int, clock: ClockProtocol = SystemClock()):
        self.rpm_bucket = TokenBucket(rpm_limit, rpm_limit / 60.0, clock)
        self.tpm_bucket = TokenBucket(tpm_limit, tpm_limit / 60.0, clock)
        self.tpm_limit = tpm_limit
        self.lock = asyncio.Lock()

class RateLimitedProvider:
    """Decorador de estrangulamiento proactivo con mitigación Thundering Herd."""
    def __init__(self, underlying: LLMProvider, quota_manager: QuotaManager):
        self._underlying = underlying
        self._quota = quota_manager

    async def _wait_for_capacity(self, total_expected_tokens: int) -> None:
        if total_expected_tokens > self._quota.tpm_limit:
            raise ValueError(
                f"RATE_LIMIT_DEADLOCK: El payload estimado ({total_expected_tokens} TPM) "
                f"excede la capacidad máxima del bucket ({self._quota.tpm_limit} TPM)."
            )

        while True:
            async with self._quota.lock:
                rpm_wait = self._quota.rpm_bucket.get_wait_time(1.0)
                tpm_wait = self._quota.tpm_bucket.get_wait_time(float(total_expected_tokens))
                
                max_wait = max(rpm_wait, tpm_wait)

                if max_wait <= 0.0:
                    self._quota.rpm_bucket.consume(1.0)
                    self._quota.tpm_bucket.consume(float(total_expected_tokens))
                    break

            # SOTA: Jitter estocástico para dispersar ráfagas de despertares concurrentes
            jitter = random.uniform(0.005, 0.050)
            logger.debug(f"Throttling: Durmiendo {max_wait + jitter:.3f}s")
            await asyncio.sleep(max_wait + jitter)

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        # SOTA Fase 15.3: Consumo predictivo estricto desde el DTO BudgetStats (TPM Real).
        # Se elimina la heurística ciega (x 2.0) a favor del cálculo asimétrico.
        total_expected_tokens = envelope.budget_stats.predicted_tpm
        
        await self._wait_for_capacity(total_expected_tokens)
        return await self._underlying.translate(envelope)