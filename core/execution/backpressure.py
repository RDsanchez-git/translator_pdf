"""
Mecanismo de backpressure del execution plane.

NADR-F18-02 §5.3:
  R8: Propagación de presión consumidores→productores.
  R9: Bounded buffering o mecanismo equivalente.
  R10: Mecanismo distinguible de la política de backpressure (18.3).

En un daemon secuencial pull-based (DC-01):
  - Bounded Buffering: La cola SQLite (ControlPlaneRepository) actúa como
    el buffer acotado y persistente.
  - Propagación: Cuando el consumidor (daemon) entra en estado HOLD (decisión
    de admission), deja de hacer pick_task(), propagando la presión de vuelta
    al productor (la cola), que retiene las tareas sin que el daemon consuma
    memoria/CPU adicional.
  - Distinción: El mecanismo (el bucle de espera inactivo) está separado de
    la política (los umbrales de RSS que deciden CUÁNDO hacer HOLD), la cual
    será definida en la Subfase 18.3.

Relación con Admission (Task 3.2.1):
  - AdmissionMechanism: Decide SI admitir nueva tarea (ALLOW/HOLD/REJECT).
  - BackpressureMechanism: Define CÓMO aplicar pausas interrumpibles.
  
  Son mecanismos SEPARADOS (R10):
  - Admission USA backpressure cuando decide HOLD.
  - Pero backpressure puede usarse en otros contextos (post-task, durante 
    task, rate limiting, etc.) en futuras subfases.
  
  La separación conceptual se mantiene aunque actualmente backpressure solo
  sea invocado por admission. Esto permite evolución sin acoplamiento.

Este módulo define el MECANISMO (puerto). La implementación concreta está
en runtime/backpressure_mechanism.py.


"""


from __future__ import annotations

from typing import Protocol, runtime_checkable




@runtime_checkable
class BackpressureMechanismPort(Protocol):
    """
    Puerto hexagonal para el mecanismo de backpressure.
    
    Define CÓMO se aplica la presión, no CUÁNDO (eso es política).
    NADR-F18-02 §5.3 R10: mecanismo distinguible de la política.
    
    Implementado en runtime/backpressure_mechanism.py.
    """
    def apply(self, duration_sec: float) -> None:
        """
        Aplica backpressure deteniendo la extracción de trabajo por un tiempo.
        
        En un daemon secuencial, esto es equivalente a no hacer pick_task().
        Debe ser interrumpible por una señal de shutdown (R8: propagación).
        
        Args:
            duration_sec: Segundos de pausa (puede interrumpirse antes por stop).
        """
        ...