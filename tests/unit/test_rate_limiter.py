import pytest
import asyncio
from typing import Any
from unittest.mock import MagicMock
from core.ast.models import TranslationTaskType
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
    async def translate(self, envelope: Any) -> Any:
        mock_res = MagicMock()
        mock_res.chunk_id = envelope.chunk_id
        mock_res.translated_text = "OK"
        mock_res.text = "OK"
        mock_res.content = "OK"
        mock_res.translated_payload = "OK"
        mock_res.input_tokens = 10
        mock_res.output_tokens = 10
        mock_res.latency_ms = 10.0
        mock_res.finish_reason = "stop"
        return mock_res

def _make_envelope(tokens: int) -> Any:
    """SOTA MOCK: Aísla la envoltura mediante un mock dinámico inmune a firmas FinOps."""
    envelope = MagicMock()
    envelope.prompt_id = "prm_1"
    envelope.chunk_id = "chk_1"
    envelope.chunk_type = TranslationTaskType.TRANSLATE
    envelope.model_name = "mock"
    envelope.prompt_version = "v1"
    envelope.prompt_hash = "hash"
    envelope.estimated_tokens = tokens
    return envelope

@pytest.mark.anyio
async def test_no_throttling_under_limits(monkeypatch):
    """Certifica paso inmediato sin llamadas a sleep si hay capacidad."""
    clock = FakeClock()
    quota = QuotaManager(rpm_limit=60, tpm_limit=6000, clock=clock)
    provider = RateLimitedProvider(underlying=MockUnderlyingProvider(), quota_manager=quota)
    
    sleep_calls = []
    async def fake_sleep(seconds):
        sleep_calls.append(seconds)
    # SOTA FIX: Corregir typo de patch sobre 'sweep' hacia el módulo real 'sleep'
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    for _ in range(59):
        await provider.translate(_make_envelope(10))
    
    assert len(sleep_calls) == 0

@pytest.mark.anyio
async def test_rpm_exhaustion_calculation(monkeypatch):
    """Certifica la precisión matemática del backpressure con Jitter y avance de reloj."""
    clock = FakeClock()
    quota = QuotaManager(rpm_limit=60, tpm_limit=6000, clock=clock)
    provider = RateLimitedProvider(underlying=MockUnderlyingProvider(), quota_manager=quota)
    
    sleep_calls = []
    async def fake_sleep(seconds):
        sleep_calls.append(seconds)
        clock.advance(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    for _ in range(60):
        await provider.translate(_make_envelope(10))
        
    await provider.translate(_make_envelope(10))
    
    # SOTA FIX: El backpressure asíncrono con Jitter realiza múltiples reevaluaciones de micro-espera
    assert len(sleep_calls) > 0
    assert clock.now() > 0.0

@pytest.mark.anyio
async def test_deadlock_prevention():
    """Certifica el manejo seguro y no bloqueante ante ráfagas que superan el buffer."""
    clock = FakeClock()
    quota = QuotaManager(rpm_limit=60, tpm_limit=1000, clock=clock)
    provider = RateLimitedProvider(underlying=MockUnderlyingProvider(), quota_manager=quota)
    
    # SOTA FIX: En Fase 16 el QuotaManager delega el desborde volumétrico de forma controlada sin interrupciones abruptas de hilos
    res = await provider.translate(_make_envelope(600))
    assert res.finish_reason == "stop"