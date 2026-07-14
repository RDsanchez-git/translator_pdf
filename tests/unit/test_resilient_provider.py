import pytest
from core.resilience.circuit_breaker import GlobalCircuitBreaker, CircuitState
from core.execution.exceptions import TransientAPIError, CircuitTripError

class MockNetworkFailureService:
    def __init__(self):
        self.calls = 0

    async def execute_call(self):
        self.calls += 1
        raise TransientAPIError("Fallo de red físico simulado.")

@pytest.mark.anyio
async def test_sliding_window_circuit_trip():
    """Certifica de forma pura que el disyuntor transiciona de CLOSED a OPEN ante ráfagas."""
    breaker = GlobalCircuitBreaker(failure_threshold=2, recovery_timeout=10.0)
    mock_service = MockNetworkFailureService()

    # Intento 1: Bajo el umbral de fallos, el circuito permanece CLOSED. El error burbujea.
    with pytest.raises(TransientAPIError):
        await breaker.call(mock_service.execute_call)
    assert breaker.state == CircuitState.CLOSED

    # Intento 2: Se alcanza el umbral de fallos. El disyuntor detecta la ruptura (Trip).
    with pytest.raises(CircuitTripError):
        await breaker.call(mock_service.execute_call)
    
    # Invariante de seguridad SRE: El circuito corta el paso físico de inmediato
    assert breaker.state == CircuitState.OPEN

    # Intento 3: Llamadas ulteriores rebotan en la barrera perimetral sin tocar la red (Fast-Reject).
    await breaker.check_state()
    assert breaker.state == CircuitState.OPEN
    
    # Comprobación final: Bloqueo de red efectivo
    assert mock_service.calls == 2