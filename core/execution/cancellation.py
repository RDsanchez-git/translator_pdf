"""
Mecanismo de cancelación cooperativa del execution plane.

NADR-F18-02 §5.4:
  R11: Cancelación cooperativa (checkpoints explícitos, no kill abrupto).
  R12: La cancelación NO compromete ni publica evidencia científica incompleta.
  R13: La cancelación libera recursos (lease, heartbeat, locks).
  R14: Cancelación verificable (outcome COMPLETED / CANCELLED / FAILED).

Hexagonal: lógica pura de core (threading.Event del stdlib). Sin I/O, sin infra.
"""
from __future__ import annotations

import threading
from enum import Enum, auto


class TaskOutcome(Enum):
    """
    Outcome verificable de una tarea (NADR-F18-02 §5.4 R14).
    
    COMPLETED: Tarea procesada exitosamente.
    CANCELLED: Tarea cancelada por shutdown o cancelación cooperativa.
    FAILED: Tarea fallida por error del sistema.
    """
    COMPLETED = auto()
    CANCELLED = auto()
    FAILED = auto()


class CancellationToken:
    """
    Token de cancelación cooperativa, thread-safe.

    Los checkpoints invocan raise_if_cancelled(); el worker captura
    TaskCancelledError y libera recursos SIN persistir estado científico
    parcial (R12).

    El parent (stop_event global de CoordinationPrimitives) permite que una
    señal de shutdown cancele también la tarea en vuelo (R11).
    """

    __slots__ = ("_event", "_parent", "_reason", "_reason_lock")

    def __init__(self, parent: threading.Event | None = None) -> None:
        self._event = threading.Event()
        self._parent = parent
        self._reason = ""
        self._reason_lock = threading.Lock()

    def cancel(self, reason: str) -> None:
        """Cancela este token con una razón indexable."""
        with self._reason_lock:
            if not self._reason:
                self._reason = reason
        self._event.set()

    def is_cancelled(self) -> bool:
        """Verifica si hay cancelación (propia o del parent)."""
        if self._event.is_set():
            return True
        return self._parent is not None and self._parent.is_set()

    @property
    def reason(self) -> str:
        """Razón de cancelación (propia o 'global_stop' si fue el parent)."""
        with self._reason_lock:
            if self._reason:
                return self._reason
        if self._parent is not None and self._parent.is_set():
            return "global_stop"
        return ""

    def raise_if_cancelled(self) -> None:
        """
        Checkpoint cooperativo: fail-fast si hay cancelación (R11).
        
        Lanza TaskCancelledError si el token o su parent fueron cancelados.
        """
        from core.execution.exceptions import TaskCancelledError
        
        if self.is_cancelled():
            raise TaskCancelledError(self.reason)
    
    def reset(self) -> None:
        """Resetea el token para reutilización (ej. entre tareas)."""
        self._event.clear()
        with self._reason_lock:
            self._reason = ""