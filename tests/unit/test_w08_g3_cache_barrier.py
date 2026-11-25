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
    from decimal import Decimal
    import time

    from apps.bootstrap import provider_stack_factory as factory
    from apps.llm_workers import sync_bridge
    from apps.llm_workers.g3_admission import (
        GPT_OSS_120B, G3PreEffectAdmission, GroqFreeTierWitness,
    )
    from core.execution.exceptions import G3ExternalEffectNotStartedError
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
            captured["admission"] = kwargs["pre_effect_admission"]

    async def _stack(**kwargs: Any) -> object:
        captured["factory_kwargs"] = kwargs
        return object()

    monkeypatch.setenv("GROQ_API_KEY", "synthetic-no-network-key")
    monkeypatch.setattr(
        thread_owned_sqlite_rate_limit_store,
        "ThreadOwnedSQLiteRateLimitStore", _RateStore,
    )
    monkeypatch.delenv("TPDF_OFFLINE_LAB", raising=False)
    monkeypatch.setattr(sync_bridge, "SyncProviderBridge", _Bridge)
    # Spy at the shared factory underneath the real guarded Free factory.
    monkeypatch.setattr(factory, "build_provider_stack", _stack)

    # Credentials alone must not open the quota store or compose a provider.
    with pytest.raises(G3ExternalEffectNotStartedError, match="ADMISSION_EVIDENCE_MISSING"):
        engine._create_chunk_processor({})
    assert captured == {}

    now = time.time_ns()
    witness = GroqFreeTierWitness(
        "synthetic-w08", "synthetic-account", "synthetic-quota", "synthetic-free",
        now, now + 60_000_000_000, 30, 1000, 8000, 200000,
        "FREE", True, True, True, document_id="d" * 64,
    )
    admission = G3PreEffectAdmission(
        provider_id="groq", model_name=GPT_OSS_120B,
        root_config_sha256=engine._product_effective_config_sha256(),
        input_limit=8000, output_limit=4096, context_window=131072,
        input_estimator=_Estimator(), estimator_evidence_ref="synthetic-estimator",
        egress_authorization_ref="synthetic-egress", data_scope_ref="synthetic-data",
        purpose_ref="synthetic-purpose", retention_ref="synthetic-retention",
        training_use_ref="synthetic-training", budget_authorization_ref="synthetic-budget",
        price_evidence_ref="synthetic-price",
        input_price_per_token=Decimal("0.00000015"),
        output_price_per_token=Decimal("0.00000060"),
        authorized_max_cost=Decimal("0"), free_tier_witness=witness,
    )

    def forbidden_transport():
        raise AssertionError("W08-3_NO_PROVIDER_EGRESS_IN_TEST")

    scope = factory.ProductGroqScope(admission, _Estimator(), forbidden_transport)
    processor, store = engine._create_chunk_processor({}, product_scope=scope)
    try:
        assert processor is not None
        assert captured["factory_kwargs"]["cache_db_path"] is None
        assert captured["factory_kwargs"]["rate_limit_store"] is store
        assert captured["factory_kwargs"]["provider_override"] is not None
        assert captured["bridge_context_snapshots"] == {}
        assert captured["admission"] is admission
    finally:
        store.close()
    assert captured["rate_store_closed"] is True


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
