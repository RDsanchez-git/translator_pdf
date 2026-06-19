import time
import asyncio
import logging
from enum import Enum
import threading
from collections import deque
from typing import Callable, Any, Dict, Awaitable, Optional
from core.execution.exceptions import CircuitOpenError, CircuitTripError, TransientAPIError

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class GlobalCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, window_sec: float = 60.0, recovery_timeout: float = 30.0):
        self.state = CircuitState.CLOSED
        self.failure_threshold = failure_threshold
        self.window_sec = window_sec
        self.recovery_timeout = recovery_timeout
        
        self.failure_timestamps = deque()
        self.last_failure_time = 0.0
        
        # SOTA: Identificación por Task asíncrona única en lugar de Thread ID
        self.probe_owner_task_id: Optional[int] = None 
        self._lock = asyncio.Lock()

        self.metrics: Dict[str, int] = {
            "rejections": 0,
            "trips": 0,
            "probes_failed": 0,
            "recoveries": 0
        }

    def _prune_window(self, now: float):
        while self.failure_timestamps and now - self.failure_timestamps[0] > self.window_sec:
            self.failure_timestamps.popleft()

    async def check_state(self):
        """Validación asíncrona no bloqueante de transiciones de estado."""
        async with self._lock:
            now = time.monotonic()
            self._prune_window(now)
            
            current_task = asyncio.current_task()
            current_task_id = id(current_task) if current_task else 0
            
            if self.state == CircuitState.OPEN:
                elapsed = now - self.last_failure_time
                if elapsed >= self.recovery_timeout and self.probe_owner_task_id is None:
                    self.state = CircuitState.HALF_OPEN
                    self.probe_owner_task_id = current_task_id
                    logger.warning("CB: Transición a HALF_OPEN. Tarea sonda asíncrona asignada.")
                    return
                else:
                    self.metrics["rejections"] += 1
                    remaining = max(0.0, self.recovery_timeout - elapsed)
                    raise CircuitOpenError(cooldown_remaining=remaining)
            
            elif self.state == CircuitState.HALF_OPEN:
                if current_task_id != self.probe_owner_task_id:
                    self.metrics["rejections"] += 1
                    raise CircuitOpenError(cooldown_remaining=self.recovery_timeout)

    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """SOTA: Envoltura agnóstica para llamadas asíncronas de red."""
        await self.check_state()
        try:
            # Ejecución nativa del coroutine aguas abajo
            result = await func(*args, **kwargs)
            await self._record_success()
            return result
        except TransientAPIError as e:
            await self._record_failure()
            raise e

    async def _record_success(self):
        async with self._lock:
            current_task = asyncio.current_task()
            current_task_id = id(current_task) if current_task else 0

            if self.state == CircuitState.HALF_OPEN and current_task_id == self.probe_owner_task_id:
                logger.info("CB: CLOSED. Sonda exitosa, sistema recuperado.")
                self.state = CircuitState.CLOSED
                self.probe_owner_task_id = None
                self.failure_timestamps.clear()
                self.metrics["recoveries"] += 1

    async def _record_failure(self):
        async with self._lock:
            now = time.monotonic()
            current_task = asyncio.current_task()
            current_task_id = id(current_task) if current_task else 0
            
            if self.state == CircuitState.HALF_OPEN and current_task_id == self.probe_owner_task_id:
                self.state = CircuitState.OPEN
                self.last_failure_time = now
                self.probe_owner_task_id = None
                self.metrics["probes_failed"] += 1
                raise CircuitTripError("CB: Sonda fallida. Re-abriendo circuito.")
            
            self._prune_window(now)
            self.failure_timestamps.append(now)
            
            if len(self.failure_timestamps) >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_failure_time = now
                self.metrics["trips"] += 1
                raise CircuitTripError(f"CB: OPEN. Umbral de {self.failure_threshold} fallos alcanzado.")

    async def get_metrics_snapshot(self) -> Dict[str, int]:
        async with self._lock:
            return self.metrics.copy()


class CircuitBreakerRegistry:
    _breakers: Dict[str, GlobalCircuitBreaker] = {}
    _lock = threading.Lock()  # Se mantiene síncrono solo para la creación inicial estática

    @classmethod
    def get_breaker(cls, name: str, threshold: int = 5) -> GlobalCircuitBreaker:
        with cls._lock:
            if name not in cls._breakers:
                cls._breakers[name] = GlobalCircuitBreaker(failure_threshold=threshold)
            return cls._breakers[name]