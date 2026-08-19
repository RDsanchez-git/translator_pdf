import asyncio
import logging
import random
import time
from typing import Optional
from enum import Enum
from dataclasses import dataclass
from typing import Protocol
from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import LLMProvider
from core.prompting.inference_result import InferenceResult
from core.execution.exceptions import PermanentQuotaRejection, QuotaTimeoutError
from core.resilience.rate_limit_store import RateLimitStore
from core.resilience.rate_limit_store import BucketState


logger = logging.getLogger(__name__)

# =====================================================================
# SOTA: DOMINIO DE CUOTAS (FASE 15.3 A y B)
# =====================================================================

class QuotaRejectionReason(str, Enum):
    """SOTA: Taxonomía exhaustiva de rechazo, incluyendo fallos de infraestructura."""
    NONE = "none"
    INSUFFICIENT_TPM = "insufficient_tpm"
    INSUFFICIENT_RPM = "insufficient_rpm"
    PAYLOAD_EXCEEDS_GLOBAL_LIMIT = "payload_exceeds_global_limit"
    QUOTA_MANAGER_UNAVAILABLE = "quota_manager_unavailable"
    CONFIGURATION_ERROR = "configuration_error"

@dataclass(frozen=True, slots=True)
class QuotaReservation:
    """SOTA: DTO Inmutable. Creación restringida a Factory Methods para proteger invariantes."""
    granted: bool
    reserved_tokens: int
    reserved_requests: int
    available_at_monotonic: float
    remaining_tpm: int
    remaining_rpm: int
    rejection_reason: QuotaRejectionReason

    @classmethod
    def create_granted(cls, tokens: int, requests: int, available_at: float, rem_tpm: int, rem_rpm: int) -> "QuotaReservation":
        return cls(
            granted=True,
            reserved_tokens=tokens,
            reserved_requests=requests,
            available_at_monotonic=available_at,
            remaining_tpm=rem_tpm,
            remaining_rpm=rem_rpm,
            rejection_reason=QuotaRejectionReason.NONE
        )

    @classmethod
    def create_rejected(cls, reason: QuotaRejectionReason, available_at: float, rem_tpm: int, rem_rpm: int) -> "QuotaReservation":
        return cls(
            granted=False,
            reserved_tokens=0,
            reserved_requests=0,
            available_at_monotonic=available_at,
            remaining_tpm=rem_tpm,
            remaining_rpm=rem_rpm,
            rejection_reason=reason
        )

class QuotaManagerProtocol(Protocol):
    """SOTA: Puerto Hexagonal Asíncrono para evaluación predictiva determinista."""
    async def reserve(self, estimated_tokens: int, estimated_requests: int = 1) -> QuotaReservation: ...

# =====================================================================
# SOTA: IMPLEMENTACIÓN MATEMÁTICA Y RED
# =====================================================================

class ClockProtocol(Protocol):
    """SOTA: Abstracción del tiempo para determinismo estricto en pruebas."""
    def now(self) -> float: ...

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

class QuotaManager(QuotaManagerProtocol):
    """SOTA: Gestor de estado predictivo adaptado al QuotaManagerProtocol."""
    def __init__(
        self,
        rpm_limit: int,
        tpm_limit: int,
        clock: ClockProtocol = SystemClock(),
        store: Optional[RateLimitStore] = None,
    ):
        self.rpm_bucket = TokenBucket(rpm_limit, rpm_limit / 60.0, clock)
        self.tpm_bucket = TokenBucket(tpm_limit, tpm_limit / 60.0, clock)
        self.tpm_limit = tpm_limit
        self.clock = clock
        self.lock = asyncio.Lock()
        self._store = store

        # DF-27: Restaurar estado persistente si existe
        if self._store is not None:
            self._restore_bucket_state("rpm", self.rpm_bucket, rpm_limit)
            self._restore_bucket_state("tpm", self.tpm_bucket, tpm_limit)

    def _restore_bucket_state(
        self,
        bucket_id: str,
        bucket: TokenBucket,
        capacity: int,
    ) -> None:
        """
        Restaura el estado de un bucket desde el store.
        
        Convierte epoch (del store) a monotonic (del bucket) y aplica
        refill por el tiempo transcurrido desde el último save.
        """
        if self._store is None:  # ← Type guard requerido por Pyright
            return
        state = self._store.load(bucket_id)
        if state is None:
            return

        elapsed = max(0.0, time.time() - state.last_update)
        refilled = min(float(capacity), state.tokens + elapsed * bucket.refill_rate)
        bucket.tokens = refilled
        bucket.last_update = self.clock.now()

    def _persist_bucket_state(self) -> None:
        """Persiste el estado actual de ambos buckets (epoch seconds)."""
        if self._store is None:  # ← Type guard ya existía, verificar que esté
            return
        now_epoch = time.time()
        self._store.save("rpm", BucketState(
            tokens=self.rpm_bucket.tokens,
            last_update=now_epoch,
        ))
        self._store.save("tpm", BucketState(
            tokens=self.tpm_bucket.tokens,
            last_update=now_epoch,
        ))

    async def reserve(self, estimated_tokens: int, estimated_requests: int = 1) -> QuotaReservation:
        if estimated_tokens > self.tpm_limit:
            return QuotaReservation.create_rejected(
                reason=QuotaRejectionReason.PAYLOAD_EXCEEDS_GLOBAL_LIMIT,
                available_at=self.clock.now(),
                rem_tpm=int(self.tpm_bucket.tokens),
                rem_rpm=int(self.rpm_bucket.tokens)
            )

        async with self.lock:
            rpm_wait = self.rpm_bucket.get_wait_time(float(estimated_requests))
            tpm_wait = self.tpm_bucket.get_wait_time(float(estimated_tokens))
            max_wait = max(rpm_wait, tpm_wait)

            if max_wait <= 0.0:
                self.rpm_bucket.consume(float(estimated_requests))
                self.tpm_bucket.consume(float(estimated_tokens))

                # DF-27: Persistir estado tras consumo exitoso
                self._persist_bucket_state()

                return QuotaReservation.create_granted(
                    tokens=estimated_tokens,
                    requests=estimated_requests,
                    available_at=self.clock.now(),
                    rem_tpm=int(self.tpm_bucket.tokens),
                    rem_rpm=int(self.rpm_bucket.tokens)
                )

            available_at = self.clock.now() + max_wait
            reason = QuotaRejectionReason.INSUFFICIENT_TPM if tpm_wait >= rpm_wait else QuotaRejectionReason.INSUFFICIENT_RPM

            return QuotaReservation.create_rejected(
                reason=reason,
                available_at=available_at,
                rem_tpm=int(self.tpm_bucket.tokens),
                rem_rpm=int(self.rpm_bucket.tokens)
            )

# =====================================================================
# SOTA: INTERCEPTOR DE RED (15.3-C)
# =====================================================================

class RateLimitedProvider(LLMProvider):
    """SOTA: Interceptor de red. Estrangulamiento predictivo, timeouts y telemetría de contención."""
    
    def __init__(
        self, 
        underlying: LLMProvider, 
        quota_manager: QuotaManagerProtocol, 
        max_wait_seconds: float = 300.0,
        min_jitter: float = 0.005,   # SOTA FIX: Jitter configurable
        max_jitter: float = 0.050    # SOTA FIX: Jitter configurable
    ):
        self._underlying = underlying
        self._quota = quota_manager
        self.max_wait_seconds = max_wait_seconds
        self.min_jitter = min_jitter
        self.max_jitter = max_jitter

    # SOTA FIX: Contrato actualizado a InferenceResult
    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        target_tokens = envelope.estimated_tokens
        total_wait_time = 0.0
        attempts = 0  # SOTA FIX: Contador de contención

        while True:
            attempts += 1
            reservation = await self._quota.reserve(
                estimated_tokens=target_tokens,
                estimated_requests=1
            )

            if reservation.granted:
                # SOTA FIX: Telemetría de contención y espera pura
                envelope.telemetry["quota_wait_seconds"] = round(total_wait_time, 3)
                envelope.telemetry["quota_reservation_attempts"] = attempts
                envelope.telemetry["remaining_tpm"] = reservation.remaining_tpm
                envelope.telemetry["remaining_rpm"] = reservation.remaining_rpm
                break

            if reservation.rejection_reason in (
                QuotaRejectionReason.PAYLOAD_EXCEEDS_GLOBAL_LIMIT,
                QuotaRejectionReason.CONFIGURATION_ERROR,
                QuotaRejectionReason.QUOTA_MANAGER_UNAVAILABLE
            ):
                raise PermanentQuotaRejection(f"Rechazo absoluto pre-red. Razón: {reservation.rejection_reason.value}")

            sleep_delta = max(0.0, reservation.available_at_monotonic - time.monotonic())
            jitter = random.uniform(self.min_jitter, self.max_jitter)
            wait_cycle = sleep_delta + jitter

            if total_wait_time + wait_cycle > self.max_wait_seconds:
                # SOTA FIX: Excepción tipada separada para Timeouts
                raise QuotaTimeoutError(
                    f"Timeout de cuota excedido ({self.max_wait_seconds}s). "
                    f"El bucket no logró liberar {target_tokens} tokens tras {attempts} intentos."
                )

            total_wait_time += wait_cycle
            await asyncio.sleep(wait_cycle)

        return await self._underlying.translate(envelope)