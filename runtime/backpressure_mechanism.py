"""
Implementación del mecanismo de backpressure para daemon secuencial.

NADR-F18-02 §5.3 R8: propagación de presión.
DC-01: el daemon es secuencial y pull-based. El mecanismo de backpressure
es "esperar sin busy-wait" cuando admission decide HOLD.
"""
from __future__ import annotations

from core.execution.coordination import CoordinationPrimitives


class SequentialBackpressureMechanism:
    """
    Mecanismo de backpressure para daemon secuencial pull-based.
    
    Aplica backpressure bloqueando la ejecución del daemon por un tiempo
    configurable, permitiendo interrupción temprana por stop_event.
    
    NADR-F18-02 §5.3 R9: El "bounded buffering" es la cola SQLite subyacente.
    Este mecanismo es el "equivalente" para un sistema pull-based: detener
    el pull propaga la presión al buffer acotado sin busy-wait.
    
    NADR-F18-02 §5.3 R8: La propagación se logra al dejar de hacer pick_task(),
    lo que permite que la cola retenga tareas sin que el daemon consuma
    recursos adicionales.
    """

    def __init__(self, coordination: CoordinationPrimitives) -> None:
        """
        Args:
            coordination: Primitivos de coordinación compartidos (stop_event).
        """
        self._coord = coordination

    def apply(self, duration_sec: float) -> None:
        """
        Bloquea la ejecución del daemon por `duration_sec`, permitiendo
        interrupción temprana por stop_event.
        
        Esto propaga la presión al productor (la cola no se vacía) sin
        consumir ciclos de CPU activos.
        
        Args:
            duration_sec: Segundos de pausa (puede interrumpirse antes por stop).
        """
        self._coord.wait_for_stop(timeout=duration_sec)