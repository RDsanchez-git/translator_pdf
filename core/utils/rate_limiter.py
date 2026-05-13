import time
import threading
from collections import deque

class RateLimiter:
    """SOTA: Gateway concurrente con jerarquía de bloqueos invertida (Temporal -> Espacial)."""
    
    def __init__(self, rpm: int = 15, max_concurrent: int = 2):
        self.rpm = rpm
        self.window = 60.0
        self.semaphore = threading.BoundedSemaphore(max_concurrent)
        self.lock = threading.Lock()
        self.timestamps = deque()

    def acquire(self):
        # 1. Contabilidad Temporal PURA (con revalidación, sin reservas futuras)
        while True:
            sleep_time = 0.0
            with self.lock:
                now = time.monotonic()
                
                while self.timestamps and now - self.timestamps[0] > self.window:
                    self.timestamps.popleft()
                
                if len(self.timestamps) < self.rpm:
                    self.timestamps.append(now) # Solo anota en tiempo real
                    break # Token adquirido, sale del bucle
                else:
                    sleep_time = (self.timestamps[0] + self.window) - now
            
            # Pausa preventiva fuera del cerrojo
            if sleep_time > 0:
                time.sleep(sleep_time)
                
        # 2. Gating de Conexión (El hilo espera socket solo si ya tiene cuota temporal)
        self.semaphore.acquire()

        
    def release(self):
            # SOTA: Libera el slot de concurrencia para el siguiente worker
            self.semaphore.release()

# SOTA: Instancia Global
GLOBAL_RATE_LIMITER = RateLimiter(rpm=15, max_concurrent=2)