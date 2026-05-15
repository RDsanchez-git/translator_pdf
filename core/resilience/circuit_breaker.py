import time
import threading
import logging
from enum import Enum
from collections import deque
from typing import Callable, Any, Dict
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
        
        # SOTA: Ventana deslizante para evitar amnesia
        self.failure_timestamps = deque()
        self.last_failure_time = 0.0
        
        # SOTA: Control de sonda única (Probe Ownership)
        self.probe_owner_thread_id = None 
        self._lock = threading.Lock()

        # Telemetría interna
        self.metrics: Dict[str, int] = {
            "rejections": 0,
            "trips": 0,
            "probes_failed": 0,
            "recoveries": 0
        }

    def _prune_window(self, now: float):
        """SOTA: Pruning extraído para reuso en vías de lectura y escritura."""
        while self.failure_timestamps and now - self.failure_timestamps[0] > self.window_sec:
            self.failure_timestamps.popleft()

    def check_state(self):
        with self._lock:
            now = time.monotonic()
            self._prune_window(now) # Lazy pruning en vía de lectura
            
            if self.state == CircuitState.OPEN:
                elapsed = now - self.last_failure_time
                if elapsed >= self.recovery_timeout and self.probe_owner_thread_id is None:
                    self.state = CircuitState.HALF_OPEN
                    self.probe_owner_thread_id = threading.get_ident()
                    logger.warning("CB: Transición a HALF_OPEN. Hilo sonda asignado.")
                else:
                    self.metrics["rejections"] += 1
                    # SOTA: Clamping a 0.0 para evitar sleeps negativos o logs anómalos
                    remaining = max(0.0, self.recovery_timeout - elapsed)
                    raise CircuitOpenError(remaining)
            
            elif self.state == CircuitState.HALF_OPEN:
                if threading.get_ident() != self.probe_owner_thread_id:
                    self.metrics["rejections"] += 1
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
            # SOTA: Solo limpiamos el historial si venimos de una recuperación exitosa
            if self.state == CircuitState.HALF_OPEN and threading.get_ident() == self.probe_owner_thread_id:
                logger.info("CB: CLOSED. Sonda exitosa, sistema recuperado.")
                self.state = CircuitState.CLOSED
                self.probe_owner_thread_id = None
                self.failure_timestamps.clear() # Reset solo en recuperación real
                self.metrics["recoveries"] += 1
            
            # Nota: En estado CLOSED, un éxito NO limpia el failure_timestamps. 
            # Dejamos que la ventana de tiempo (window_sec) haga su trabajo.

    def _record_failure(self):
        with self._lock:
            now = time.monotonic()
            
            # Caso A: Fallo en sonda HALF_OPEN
            if self.state == CircuitState.HALF_OPEN and threading.get_ident() == self.probe_owner_thread_id:
                self.state = CircuitState.OPEN
                self.last_failure_time = now
                self.probe_owner_thread_id = None
                self.metrics["probes_failed"] += 1
                raise CircuitTripError("CB: Sonda fallida. Re-abriendo circuito.")
            
            # Caso B: Fallo en estado CLOSED (Manejo de ventana)
            self._prune_window(now) # Reemplaza por completo el viejo bucle while
            self.failure_timestamps.append(now) # Se hace UNA sola vez
            
            # Si el volumen de fallos en la ventana supera el umbral, abrimos
            if len(self.failure_timestamps) >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_failure_time = now
                self.metrics["trips"] += 1
                raise CircuitTripError(f"CB: OPEN. Umbral de {self.failure_threshold} fallos alcanzado.")
            
    def get_metrics_snapshot(self) -> Dict[str, int]:
        """SOTA: Acceso thread-safe estricto para scrapers/telemetría externa."""
        with self._lock:
            return self.metrics.copy()
        

class CircuitBreakerRegistry:
    _breakers = {}
    _lock = threading.Lock()

    @classmethod
    def get_breaker(cls, name: str, threshold: int = 5) -> GlobalCircuitBreaker:
        with cls._lock:
            if name not in cls._breakers:
                cls._breakers[name] = GlobalCircuitBreaker(failure_threshold=threshold)
            return cls._breakers[name]