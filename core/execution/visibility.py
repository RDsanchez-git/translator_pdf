"""
Visibilidad operacional mínima del execution plane.

NADR-F18-02 §5.7:
  R23: Visibilidad operacional mínima del estado de unidad de trabajo.
  R24: Propiedad observable para distinguir estado de unidad de trabajo.
  R25: Evidencia operacional separada de la evidencia científica.
  R26: Sin observabilidad profunda (F20): sin profiling, sin tracing
       distribuido, sin métricas de internals por defecto.

Hexagonal: modelo + puerto en core; implementación en runtime/.
Las observaciones son evidencia OPERACIONAL: nunca forman parte de la
identidad científica ni de identity_chain (NADR-F18-01 §5.2 R8).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, runtime_checkable
from core.execution.cancellation import TaskOutcome



class WorkUnitStatus(Enum):
    """
    Estados observables de una unidad de trabajo (R24).
    Taxonomía mínima: suficiente para distinguir estado, sin internals (R26).
    """
    CLAIMED = auto()      # Tarea reclamada por el worker
    PROCESSING = auto()   # Llamada LLM en curso
    COMPLETED = auto()    # Proyección materializada y ack confirmado
    CANCELLED = auto()    # Cancelación cooperativa (Task 3.3.1)
    FAILED = auto()       # Error no retry-able o abandono
    RELEASED = auto()     # Lease liberado sin estado parcial (retry-able)


@dataclass(frozen=True)
class WorkUnitObservation:
    """
    Observación operacional inmutable de una unidad de trabajo.

    R25: evidencia operacional separada de la científica.
    R26: solo estado + razón + timestamp monotónico; sin payloads,
    sin contenido de documento, sin métricas de internals.
    """
    task_id: str
    worker_id: str
    status: WorkUnitStatus
    reason: str = ""
    observed_at: float = field(default_factory=time.monotonic)


@runtime_checkable
class OperationalVisibilityPort(Protocol):
    """
    Puerto hexagonal de visibilidad operacional mínima.
    Implementado en runtime/operational_visibility.py.
    """
    def observe(self, observation: WorkUnitObservation) -> None:
        """
        Registra una observación de estado.
        Debe ser fail-safe: la visibilidad nunca rompe la ejecución.
        """
        ...

def outcome_to_status(outcome: TaskOutcome) -> WorkUnitStatus:
    """
    Mapeo explícito outcome → estado observable (NADR-F18-02 §5.7 R24).
    Función pura: sin I/O ni efectos secundarios (Functional Core).
    Total: cubre todos los miembros de TaskOutcome.
    """
    if outcome is TaskOutcome.COMPLETED:
        return WorkUnitStatus.COMPLETED
    if outcome is TaskOutcome.CANCELLED:
        return WorkUnitStatus.CANCELLED
    return WorkUnitStatus.FAILED