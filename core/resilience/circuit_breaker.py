import time
import threading
import logging
from enum import Enum
from collections import deque
from typing import Callable, Any
from core.execution.exceptions import CircuitOpenError, CircuitTripError, TransientAPIError

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class GlobalCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, window_sec: float = 60.0, recovery_timeout: float = 120.0):
        self.state = CircuitState.CLOSED
        self.failure_threshold = failure_threshold
        self.window_sec = window_sec
        self.recovery_timeout = recovery_timeout
        
        # SOTA (Punto 4): Sliding Window real
        self.failure_timestamps = deque()
        self.last_failure_time = 0.0
        
        # SOTA (Punto 2): Probe Ownership
        self.probe_owner_thread_id = None 
        self._lock = threading.Lock()

    def check_state(self):
        with self._lock:
            if self.state == CircuitState.OPEN:
                elapsed = time.monotonic() - self.last_failure_time
                if elapsed >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.probe_owner_thread_id = threading.get_ident() # Candado atado al hilo
                    logger.warning("CIRCUIT_BREAKER_HALF_OPEN: Hilo sonda asignado.")
                else:
                    raise CircuitOpenError(self.recovery_timeout - elapsed)
            
            elif self.state == CircuitState.HALF_OPEN:
                if threading.get_ident() != self.probe_owner_thread_id:
                    raise CircuitOpenError(self.recovery_timeout)

    def call(self, func: Callable, *args, **kwargs) -> Any:
        self.check_state()
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except TransientAPIError as e:
            self._record_failure()
            raise e

    def _record_success(self):
        with self._lock:
            if self.state == CircuitState.HALF_OPEN and threading.get_ident() == self.probe_owner_thread_id:
                logger.info("CIRCUIT_BREAKER_CLOSED: Sonda exitosa. Circuito restablecido.")
                self.state = CircuitState.CLOSED
                self.probe_owner_thread_id = None
                self.failure_timestamps.clear()

    def _record_failure(self):
        with self._lock:
            now = time.monotonic()
            if self.state == CircuitState.HALF_OPEN and threading.get_ident() == self.probe_owner_thread_id:
                self.state = CircuitState.OPEN
                self.last_failure_time = now
                self.probe_owner_thread_id = None
                raise CircuitTripError("Sonda HALF_OPEN fallida. Circuito bloqueado nuevamente.")
            
            # Pruning de la ventana deslizante
            while self.failure_timestamps and now - self.failure_timestamps[0] > self.window_sec:
                self.failure_timestamps.popleft()
                
            self.failure_timestamps.append(now)
            
            if len(self.failure_timestamps) >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_failure_time = now
                raise CircuitTripError(f"Circuito abierto: {self.failure_threshold} fallos en {self.window_sec}s.")

# SOTA (Punto 5): Segmentación por upstream/modelo
class CircuitBreakerRegistry:
    _breakers = {}
    _lock = threading.Lock()

    @classmethod
    def get_breaker(cls, name: str, threshold: int = 5) -> GlobalCircuitBreaker:
        with cls._lock:
            if name not in cls._breakers:
                cls._breakers[name] = GlobalCircuitBreaker(failure_threshold=threshold)
            return cls._breakers[name]