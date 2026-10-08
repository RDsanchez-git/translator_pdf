"""
Implementación del mecanismo de shutdown ordenado para daemon secuencial.

NADR-F18-02 §5.4 R15: Cancela trabajo en vuelo antes de terminar.
DC-01: el daemon es secuencial, el shutdown es una secuencia lineal.
"""
from __future__ import annotations

import time
from typing import Callable

from core.execution.coordination import CoordinationPrimitives
from core.execution.shutdown import ShutdownReport


class CoordinatedShutdownMechanism:
    """
    Mecanismo de shutdown ordenado para daemon secuencial.
    
    Secuencia garantizada:
    1. signal_stop() → propaga a CancellationToken (cancela tarea en vuelo)
    2. processor.shutdown() → bounded join del thread del bridge
    3. close_connections() → cierra conexiones DB
    
    Cada paso es best-effort: si uno falla, se registra en ShutdownReport.errors
    y se continúa con el siguiente (no silencioso, ENGINEERING_PRINCIPLES §IV).
    """

    def __init__(
        self,
        coordination: CoordinationPrimitives,
        processor_shutdown: Callable[[], None],
        connection_closers: list[Callable[[], None]],
    ) -> None:
        """
        Args:
            coordination: Primitivos de coordinación compartidos (stop_event).
            processor_shutdown: Función que cierra el bridge (processor.shutdown).
            connection_closers: Lista de funciones que cierran conexiones DB.
        """
        self._coord = coordination
        self._processor_shutdown = processor_shutdown
        self._connection_closers = connection_closers

    def execute(self, reason: str) -> ShutdownReport:
        """
        Ejecuta shutdown ordenado con secuencia garantizada.
        
        Args:
            reason: Razón del shutdown (ej. "resource_exhaustion", "normal_termination").
            
        Returns:
            ShutdownReport: Reporte verificable del shutdown.
        """
        start = time.monotonic()
        errors: list[str] = []

        # ── Paso 1: Señalar stop global ──
        # Propaga automáticamente a CancellationToken (parent=stop_event)
        # que cancela la tarea en vuelo cooperativamente (R15).
        try:
            self._coord.signal_stop()
        except Exception as e:
            errors.append(f"signal_stop failed: {e}")

        # ── Paso 2: Shutdown del processor (bridge) ──
        bridge_ok = True
        try:
            self._processor_shutdown()
        except Exception as e:
            bridge_ok = False
            errors.append(f"processor shutdown failed: {e}")

        # ── Paso 3: Cerrar conexiones DB ──
        connections_closed = 0
        for closer in self._connection_closers:
            try:
                closer()
                connections_closed += 1
            except Exception as e:
                errors.append(f"connection close failed: {e}")

        duration = time.monotonic() - start

        return ShutdownReport(
            reason=reason,
            duration_sec=duration,
            bridge_shutdown_ok=bridge_ok,
            connections_closed=connections_closed,
            errors=errors,
        )