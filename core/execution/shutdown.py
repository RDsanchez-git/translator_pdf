"""
Mecanismo de shutdown ordenado del execution plane.

NADR-F18-02 §5.4 R15: Cancela trabajo en vuelo antes de terminar.
ENGINEERING_PRINCIPLES §III: Explicit over Implicit (secuencia documentada).
ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos (shutdown verificable).

Este módulo define el MECANISMO (modelo + puerto). La implementación
concreta está en runtime/coordinated_shutdown.py.

NO implementa recuperación de estado persistente (eso es Subfase 18.2).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class ShutdownReport:
    """
    Reporte verificable del shutdown (R15 + R14).
    Permite auditar que el shutdown fue ordenado y completo.
    """
    reason: str
    duration_sec: float
    bridge_shutdown_ok: bool
    connections_closed: int
    errors: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        """True si el shutdown fue ordenado sin errores."""
        return self.bridge_shutdown_ok and len(self.errors) == 0


@runtime_checkable
class ShutdownMechanismPort(Protocol):
    """
    Puerto hexagonal para shutdown ordenado.
    Implementado en runtime/coordinated_shutdown.py.
    """
    def execute(self, reason: str) -> ShutdownReport:
        """
        Ejecuta shutdown ordenado.
        
        Secuencia típica:
        1. Señalar stop global (propaga a tarea en vuelo vía CancellationToken)
        2. Shutdown del processor (bridge) con bounded join
        3. Cerrar conexiones DB
        
        Returns:
            ShutdownReport: Reporte verificable del shutdown.
        """
        ...