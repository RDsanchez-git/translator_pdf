"""W08-3: G3 must never access prompt_hash-only legacy cache by default.

Synthetic, offline witnesses. The full versioned cache/replay contract is still
OPEN; this test proves only the opt-out barrier for the existing G3 Engine.
"""
from __future__ import annotations

from typing import Any

import pytest

from runtime import engine


@pytest.mark.unit
def test_g3_processor_explicitly_disables_legacy_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.llm_workers import sync_bridge
    from core.validation import estimators
    from infra.resilience import thread_owned_sqlite_rate_limit_store

    captured: dict[str, Any] = {}

    class _RateStore:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured["rate_store_opened"] = True

        def close(self) -> None:
            captured["rate_store_closed"] = True

    class _Estimator:
        def estimate_tokens(self, text: str) -> int:
            return len(text.split())

    class _Bridge:
        def __init__(self, **kwargs: object) -> None:
            captured["bridge_context_snapshots"] = kwargs["context_snapshots"]

    async def _stack(**kwargs: Any) -> object:
        captured["factory_kwargs"] = kwargs
        return object()

    monkeypatch.setenv("GROQ_API_KEY", "synthetic-no-network-key")
    monkeypatch.setattr(
        thread_owned_sqlite_rate_limit_store,
        "ThreadOwnedSQLiteRateLimitStore", _RateStore,
    )
    monkeypatch.setattr(estimators, "ExactBPEEstimator", _Estimator)
    monkeypatch.setattr(sync_bridge, "SyncProviderBridge", _Bridge)
    monkeypatch.setattr(engine, "build_provider_stack", _stack)

    processor, store = engine._create_chunk_processor({})
    assert processor is not None
    assert store is not None
    assert captured["factory_kwargs"]["cache_db_path"] is None
    assert captured["bridge_context_snapshots"] == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_no_cache_factory_keeps_required_provider_wrappers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.bootstrap import provider_stack_factory as factory
    from apps.llm_workers.circuit_breaker_provider import CircuitBreakerProvider

    class _NeverCreateLegacyCache:
        def __init__(self, *args: object, **kwargs: object) -> None:
            raise AssertionError("W08-3_G3_LEGACY_CACHE_FORBIDDEN")

    class _FakeProvider:
        def __init__(self, api_key: str, dialect: object) -> None:
            assert api_key == "synthetic-no-network-key"

        async def translate(self, envelope: object) -> object:
            raise AssertionError("W08-3_NO_PROVIDER_EGRESS_IN_TEST")

    monkeypatch.setattr(factory, "CachedLLMProvider", _NeverCreateLegacyCache)
    monkeypatch.setattr(factory, "GroqProvider", _FakeProvider)
    provider = await factory.build_provider_stack(
        api_key="synthetic-no-network-key", cache_db_path=None,
    )
    assert isinstance(provider, CircuitBreakerProvider)
