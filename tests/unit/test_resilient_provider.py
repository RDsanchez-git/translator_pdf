import pytest
from core.ast.models import TranslationTaskType
from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import ProviderResult
from core.resilience.circuit_breaker import GlobalCircuitBreaker, CircuitState
from apps.llm_workers.resilient_provider import ResilientProvider
# SOTA: Importar la excepción que marca la ruptura del circuito
from core.execution.exceptions import TransientAPIError, CircuitOpenError, CircuitTripError

class MockNetworkFailureProvider:
    def __init__(self):
        self.calls = 0

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        self.calls += 1
        raise TransientAPIError("Fallo de red físico simulado.")

def _make_envelope() -> PromptEnvelope:
    return PromptEnvelope(
        prompt_id="prm_1", chunk_id="chk_1", chunk_type=TranslationTaskType.TRANSLATE,
        model_name="mock", prompt_version="v1", prompt_hash="hash",
        system_prompt="sys", user_prompt="usr", raw_payload="text", estimated_tokens=10
    )

@pytest.mark.anyio
async def test_sliding_window_circuit_trip():
    """Certifica que el circuito se abre y lanza la excepción de ruptura (Trip)."""
    breaker = GlobalCircuitBreaker(failure_threshold=2, recovery_timeout=10.0)
    mock_api = MockNetworkFailureProvider()
    provider = ResilientProvider(underlying=mock_api, breaker=breaker, timeout_seconds=1.0)

    # Intento 1: Falla 3 veces internamente por Tenacity, suma 1 fallo en la ventana. 
    # El circuito sigue cerrado, así que deja burbujear el error de red original.
    with pytest.raises(TransientAPIError):
        await provider.translate(_make_envelope())
    assert breaker.state == CircuitState.CLOSED

    # Intento 2: Segunda ráfaga. Alcanza el umbral (2). 
    # El circuito detecta la ruptura y lanza la excepción de Trip (La gota que rebalsa el vaso).
    with pytest.raises(CircuitTripError):
        await provider.translate(_make_envelope())
    
    # El circuito debe estar rígidamente abierto
    assert breaker.state == CircuitState.OPEN

    # Intento 3: Falla instantáneamente en la barrera perimetral.
    with pytest.raises(CircuitOpenError):
        await provider.translate(_make_envelope())
        
    # SOTA: 2 intentos lógicos x 3 reintentos de Tenacity por intento = 6 llamadas físicas
    assert mock_api.calls == 6