"""
Primitivos de coordinación concurrente del execution plane.

NADR-F18-02 §5.5:
  R16: No data races — los primitivos son thread-safe por construcción.
  R17: Primitivos explícitos — encapsulados en un objeto inyectable, no dispersos.
  R19: Superficie identificable — un único punto de acceso a todos los primitivos.

Thread-safety contract por primitivo:
  - stop_event (threading.Event):    thread-safe por diseño del stdlib.
                                     Señal unidireccional main→heartbeat→bridge.
  - bridge_ready (threading.Event):  thread-safe por diseño del stdlib.
                                     Señal unidireccional bridge_loop→main.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CoordinationPrimitives:
    """
    Encapsula todos los primitivos de coordinación del execution plane.
    Inmutable (frozen=True): la configuración de coordinación no cambia
    durante el ciclo de vida del daemon.

    Inyectado en LLMWorkerDaemon y TaskLeaseHeartbeat vía constructor.
    """
    stop_event: threading.Event = field(
        default_factory=threading.Event,
        metadata={"direction": "main→all", "purpose": "graceful shutdown signal"}
    )
    bridge_ready: threading.Event = field(
        default_factory=threading.Event,
        metadata={"direction": "bridge_loop→main", "purpose": "event loop initialized"}
    )

    @classmethod
    def create(cls) -> "CoordinationPrimitives":
        """Factory explícita para creación de primitivos frescos."""
        return cls()

    def signal_stop(self) -> None:
        """Señala shutdown a todos los threads."""
        self.stop_event.set()

    def is_stopped(self) -> bool:
        """Verifica si se señaló shutdown."""
        return self.stop_event.is_set()

    def wait_for_stop(self, timeout: float | None = None) -> bool:
        """Bloquea hasta que se señale shutdown o timeout."""
        return self.stop_event.wait(timeout=timeout)

    def signal_bridge_ready(self) -> None:
        """Señala que el event loop del bridge está inicializado."""
        self.bridge_ready.set()

    def wait_for_bridge(self, timeout: float = 5.0) -> bool:
        """Bloquea hasta que el bridge esté listo."""
        return self.bridge_ready.wait(timeout=timeout)