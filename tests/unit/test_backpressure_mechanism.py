"""
Test del mecanismo de backpressure secuencial.

Verifica:
1. Que apply() respeta el timeout.
2. Que apply() es interrumpible por el stop_event (R8: propagación).
"""
import threading
import time

from core.execution.coordination import CoordinationPrimitives
from runtime.backpressure_mechanism import SequentialBackpressureMechanism


def test_backpressure_respects_timeout():
    """apply() debe esperar aproximadamente duration_sec."""
    coord = CoordinationPrimitives.create()
    mechanism = SequentialBackpressureMechanism(coordination=coord)

    start = time.monotonic()
    mechanism.apply(duration_sec=0.5)
    elapsed = time.monotonic() - start

    # Debe haber esperado aproximadamente 0.5 segundos
    assert 0.45 <= elapsed <= 0.65, f"Expected ~0.5s, got {elapsed}s"


def test_backpressure_is_interruptible_by_stop():
    """apply() debe ser interrumpible por stop_event (R8: propagación)."""
    coord = CoordinationPrimitives.create()
    mechanism = SequentialBackpressureMechanism(coordination=coord)

    def trigger_stop():
        time.sleep(0.1)
        coord.signal_stop()

    threading.Thread(target=trigger_stop, daemon=True).start()

    start = time.monotonic()
    # Aunque pedimos 5.0 segundos, debería interrumpirse a los ~0.1s
    mechanism.apply(duration_sec=5.0)
    elapsed = time.monotonic() - start

    # Debe haber sido interrumpido mucho antes de 5.0s
    assert elapsed < 1.0, f"Backpressure was not interruptible, took {elapsed}s"
    assert coord.is_stopped() is True