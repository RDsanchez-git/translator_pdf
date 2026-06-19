import pytest
import asyncio
from core.ast.models import TranslationTaskType
from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.routing import ProviderResult
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager

class FakeClock:
    """Mock de reloj matemático O(1) puro."""
    def __init__(self, initial_time: float = 0.0):
        self._now = initial_time

    def now(self) -> float:
        return self._now

    def advance(self, seconds: float):
        self._now += seconds

class MockUnderlyingProvider:
    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        return ProviderResult(
            chunk_id=envelope.chunk_id, translated_text="OK",
            input_tokens=10, output_tokens=10, latency_ms=10.0, finish_reason="stop"
        )

def _make_envelope(tokens: int) -> PromptEnvelope:
    return PromptEnvelope(
        prompt_id="prm_1", chunk_id="chk_1", chunk_type=TranslationTaskType.TRANSLATE,
        model_name="mock", prompt_version="v1", prompt_hash="hash",
        system_prompt="sys", user_prompt="usr", estimated_tokens=tokens,
        raw_payload="Original",
    )

@pytest.mark.anyio
async def test_no_throttling_under_limits(monkeypatch):
    """Certifica paso inmediato sin llamadas a sleep si hay capacidad."""
    clock = FakeClock()
    quota = QuotaManager(rpm_limit=60, tpm_limit=6000, clock=clock)
    provider = RateLimitedProvider(MockUnderlyingProvider(), quota)
    
    sleep_calls = []
    async def fake_sleep(seconds):
        sleep_calls.append(seconds)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    # 59 peticiones (estimado * 2 = 20 TPM c/u). Entran bien en 6000 TPM y 60 RPM.
    for _ in range(59):
        await provider.translate(_make_envelope(10))
    
    assert len(sleep_calls) == 0

@pytest.mark.anyio
async def test_rpm_exhaustion_calculation(monkeypatch):
    """Certifica la precisión matemática del backpressure con Jitter y avance de reloj."""
    clock = FakeClock()
    quota = QuotaManager(rpm_limit=60, tpm_limit=6000, clock=clock)
    provider = RateLimitedProvider(MockUnderlyingProvider(), quota)
    
    sleep_calls = []
    async def fake_sleep(seconds):
        sleep_calls.append(seconds)
        # SOTA: Simulamos que el worker despierta EXACTAMENTE en el futuro exigido
        clock.advance(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    # Agotar RPM
    for _ in range(60):
        await provider.translate(_make_envelope(10))
        
    # Petición 61 gatilla backpressure.
    await provider.translate(_make_envelope(10))
    
    assert len(sleep_calls) == 1
    # 1s base + jitter estocástico (0.005 - 0.050)
    assert 1.005 <= sleep_calls[0] <= 1.050
    assert clock.now() >= 1.005

@pytest.mark.anyio
async def test_deadlock_prevention():
    """Certifica el Fail-Fast atómico calculando Input + Buffer Output."""
    clock = FakeClock()
    # Límite 1000 TPM. Un envelope de 600 (calculado como 1200 por el factor 2x) debe fallar.
    quota = QuotaManager(rpm_limit=60, tpm_limit=1000, clock=clock)
    provider = RateLimitedProvider(MockUnderlyingProvider(), quota)
    
    with pytest.raises(ValueError, match="RATE_LIMIT_DEADLOCK"):
        await provider.translate(_make_envelope(600))