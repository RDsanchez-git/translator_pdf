"""One-shot Free Tier policy and no-download cache preflight; no external I/O."""
from dataclasses import replace
from decimal import Decimal
from hashlib import sha1, sha256
import json
from pathlib import Path
import time

import pytest

from apps.llm_workers.g3_admission import (
    G3PreEffectAdmission, GroqFreeTierWitness, GPT_OSS_120B, build_groq_request_kwargs,
)
from core.execution.exceptions import G3ExternalEffectNotStartedError
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
from core.validation import estimators
from tests.unit.test_adapters import _make_envelope

pytestmark = pytest.mark.unit


class _Estimator:
    def estimate_tokens(self, text: str) -> int:
        return 100  # Synthetic, deliberately not an attested provider count.


@pytest.fixture
def policy():
    now = time.time_ns()
    return G3PreEffectAdmission(
        provider_id="groq", model_name=GPT_OSS_120B, root_config_sha256="a"*64,
        input_limit=8000, output_limit=4096, context_window=131072,
        input_estimator=_Estimator(), estimator_evidence_ref="synthetic-estimator",
        egress_authorization_ref="synthetic-egress", data_scope_ref="synthetic-data",
        purpose_ref="synthetic-purpose", retention_ref="synthetic-zdr",
        training_use_ref="synthetic-training", budget_authorization_ref="synthetic-zero",
        price_evidence_ref="synthetic-nominal-tariff",
        input_price_per_token=Decimal("0.00000015"),
        output_price_per_token=Decimal("0.00000060"), authorized_max_cost=Decimal("0"),
        free_tier_witness=GroqFreeTierWitness(
            witness_id="synthetic-one-shot", account_evidence_ref="synthetic-account",
            quota_evidence_ref="synthetic-quota", free_entitlement_ref="synthetic-entitlement",
            observed_at_ns=now-1_000_000, valid_until_ns=now+60_000_000_000,
            remaining_rpm=30, remaining_rpd=1000, remaining_tpm=8000, remaining_tpd=200000,
            plan="FREE", no_billable_overage=True, global_zdr=True, model_allowed=True,
        ),
    )


def _verify(policy, **kwargs):
    return policy.verify(provider_id="groq", root_config_sha256="a"*64,
                         envelope=replace(_make_envelope(), model_name=GPT_OSS_120B, **kwargs))


def test_free_entitlement_keeps_nominal_tariff_and_reserves_full_request(policy):
    decision = _verify(policy)
    audit = json.loads(decision.audit_json)
    assert audit["upper_bound_cost"] == audit["authorized_max_cost"] == "0"
    assert Decimal(audit["nominal_upper_bound_cost"]) == Decimal("0.00016860")
    assert audit["free_tier_witness"]["reserved_tokens"] == 356
    assert audit["free_tier_witness"]["reserved_requests"] == 1
    envelope = replace(_make_envelope(), model_name=GPT_OSS_120B)
    wire, _ = build_groq_request_kwargs(envelope, OpenAICompatibleDialect())
    assert wire["model"] == GPT_OSS_120B and wire["max_completion_tokens"] == 256
    assert wire["reasoning_effort"] == "low" and wire["include_reasoning"] is False
    assert "tools" not in wire and "service_tier" not in wire
    assert decision.request_sha256 == sha256(json.dumps(
        wire, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode()).hexdigest()


@pytest.mark.parametrize("change,match", [
    ({"plan": "DEVELOPER"}, "ENTITLEMENT"),
    ({"no_billable_overage": False}, "ENTITLEMENT"),
    ({"global_zdr": False}, "ENTITLEMENT"),
    ({"model_allowed": False}, "ENTITLEMENT"),
    ({"free_entitlement_ref": ""}, "ENTITLEMENT"),
    ({"remaining_rpm": 0}, "INSUFFICIENT_RPM"),
    ({"remaining_rpd": 0}, "INSUFFICIENT_RPD"),
    ({"remaining_tpm": 355}, "INSUFFICIENT_TPM"),
    ({"remaining_tpd": 355}, "INSUFFICIENT_TPD"),
    ({"remaining_tpm": 8001}, "INVALID_TPM"),
    ({"remaining_tpd": True}, "INVALID_TPD"),
    ({"valid_until_ns": 0}, "EVIDENCE_STALE"),
])
def test_free_witness_rejects_unaccredited_or_exhausted_scope(policy, change, match):
    with pytest.raises(G3ExternalEffectNotStartedError, match=match):
        _verify(replace(policy, free_tier_witness=replace(policy.free_tier_witness, **change)))


@pytest.mark.parametrize("change", [
    {"free_tier_witness": None},
    {"authorized_max_cost": Decimal("0.01")},
    {"input_price_per_token": Decimal("0")},
])
def test_free_model_does_not_admit_missing_entitlement_or_paid_cap(policy, change):
    with pytest.raises(G3ExternalEffectNotStartedError, match="ENTITLEMENT"):
        _verify(replace(policy, **change))


def test_free_model_rejects_fallback(policy):
    with pytest.raises(G3ExternalEffectNotStartedError, match="ENTITLEMENT"):
        _verify(policy, target_provider="fallback_large_window")


def test_harmony_preflight_never_initializes_tokenizer(tmp_path, monkeypatch):
    monkeypatch.setattr(estimators.tiktoken, "get_encoding",
                        lambda *a, **kw: pytest.fail("implicit tokenizer acquisition"))
    with pytest.raises(ValueError, match="CACHE_MISSING"):
        estimators.verify_harmony_rank_cache(tmp_path)
    path = tmp_path / sha1(estimators.HARMONY_RANKS_URL.encode()).hexdigest()
    path.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="IDENTITY_DRIFT"):
        estimators.verify_harmony_rank_cache(tmp_path)
    monkeypatch.setattr(estimators, "HARMONY_RANKS_SHA256", sha256(b"corrupt").hexdigest())
    assert estimators.verify_harmony_rank_cache(tmp_path) == path


def test_dispatch_permit_rechecks_authority_and_is_not_reusable(monkeypatch):
    from core.execution import effect_guard as guard
    from core.execution.exceptions import MalformedInferenceResponse

    clock = [100]
    monkeypatch.setattr(guard.time, "time_ns", lambda: clock[0])
    permit = guard.FreeWitnessDispatchPermit("a"*64, 200, 100, 256)
    assert permit.reserved_tokens == 356
    with pytest.raises(G3ExternalEffectNotStartedError, match="AUTHORITY_REQUIRED"):
        permit.claim("a"*64)
    seen = []
    token = guard.g3_pre_effect_guard.set(lambda: seen.append(True))
    try:
        with pytest.raises(G3ExternalEffectNotStartedError, match="REQUEST_DRIFT"):
            permit.claim("b"*64)
        permit.claim("a"*64)
        assert seen == [True]
        with pytest.raises(MalformedInferenceResponse, match="ALREADY_ENTERED"):
            permit.claim("a"*64)
        with pytest.raises(MalformedInferenceResponse, match="USAGE_EXCEEDS_ADMISSION"):
            permit.check_reported_usage(101, 1)
        with pytest.raises(MalformedInferenceResponse, match="USAGE_EXCEEDS_ADMISSION"):
            permit.check_reported_usage(100, 257)
    finally:
        guard.g3_pre_effect_guard.reset(token)


def test_dispatch_permit_rejects_expiry_during_authority_check(monkeypatch):
    from core.execution import effect_guard as guard

    clock = [100]
    monkeypatch.setattr(guard.time, "time_ns", lambda: clock[0])
    permit = guard.FreeWitnessDispatchPermit("a"*64, 200, 100, 256)
    token = guard.g3_pre_effect_guard.set(lambda: clock.__setitem__(0, 200))
    try:
        with pytest.raises(G3ExternalEffectNotStartedError, match="EVIDENCE_STALE"):
            permit.claim("a"*64)
    finally:
        guard.g3_pre_effect_guard.reset(token)


@pytest.mark.anyio
async def test_gpt_oss_adapter_without_permit_never_enters_sdk():
    from unittest.mock import AsyncMock, patch
    from apps.llm_workers.adapters import GroqProvider

    provider = GroqProvider(api_key="fake", dialect=OpenAICompatibleDialect())
    try:
        with patch.object(provider._client.chat.completions, "create", new_callable=AsyncMock) as create:
            with pytest.raises(G3ExternalEffectNotStartedError, match="DISPATCH_PERMIT_REQUIRED"):
                await provider.translate(replace(_make_envelope(), model_name=GPT_OSS_120B))
            create.assert_not_called()
    finally:
        await provider._client.close()


@pytest.mark.anyio
@pytest.mark.parametrize("base_url,retries", [
    ("https://api.groq.com/openai/v1", 0),
    ("https://api.groq.com.example.invalid", 0),
    ("http://api.groq.com", 0),
    ("https://api.groq.com", 1),
])
async def test_free_transport_rejects_wrong_sdk_origin_or_retries(base_url, retries):
    from groq import AsyncGroq
    import httpx
    from apps.llm_workers.adapters import GroqProvider
    from core.execution import effect_guard as guard
    from core.utils.telemetry import ctx_task_id, ctx_execution_id

    def reject_io(request):
        pytest.fail("Rejected transport must never receive a request")

    envelope = replace(_make_envelope(), model_name=GPT_OSS_120B)
    wire, _ = build_groq_request_kwargs(envelope, OpenAICompatibleDialect())
    digest = sha256(json.dumps(
        wire, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode()).hexdigest()
    permit = guard.FreeWitnessDispatchPermit(digest, time.time_ns() + 60_000_000_000, 100, 256)
    checked = []
    task_token = ctx_task_id.set("synthetic-task")
    execution_token = ctx_execution_id.set("synthetic-execution")
    guard_token = guard.g3_pre_effect_guard.set(lambda: checked.append(True))
    permit_token = guard.g3_free_dispatch_permit.set(permit)
    try:
        async with AsyncGroq(
            api_key="synthetic", base_url=base_url, max_retries=retries,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(reject_io),
                                         trust_env=False, follow_redirects=False),
        ) as client:
            provider = GroqProvider("synthetic", OpenAICompatibleDialect(), client=client)
            with pytest.raises(G3ExternalEffectNotStartedError, match="TRANSPORT_CONFIGURATION_REJECTED"):
                await provider.translate(envelope)
        assert checked == []  # Reject before even consuming the permit.
    finally:
        guard.g3_free_dispatch_permit.reset(permit_token)
        guard.g3_pre_effect_guard.reset(guard_token)
        ctx_execution_id.reset(execution_token)
        ctx_task_id.reset(task_token)


@pytest.fixture
def synthetic_harmony_cache(tmp_path, monkeypatch):
    """Small byte vocabulary exercises real BPE construction, not live ranks."""
    from base64 import b64encode

    vocabulary = [bytes([i]) for i in range(256)] + [b"ab", b"abc"]
    data = b"".join(
        b64encode(token) + b" " + str(rank).encode("ascii") + b"\n"
        for rank, token in enumerate(vocabulary)
    )
    path = tmp_path / sha1(estimators.HARMONY_RANKS_URL.encode()).hexdigest()
    path.write_bytes(data)
    monkeypatch.setattr(estimators, "HARMONY_RANKS_SHA256", sha256(data).hexdigest())
    monkeypatch.setattr(estimators.tiktoken, "get_encoding",
                        lambda *a, **kw: pytest.fail("implicit encoding acquisition"))
    return tmp_path, path


def test_verified_harmony_estimator_reads_local_bytes_only(synthetic_harmony_cache):
    cache, _ = synthetic_harmony_cache
    estimator = estimators.VerifiedHarmonyEstimator(cache)
    assert estimator.estimate_tokens("") == 0
    assert estimator.estimate_tokens("abc") == 1
    assert estimator.estimate_tokens("α") == 2
    assert estimator.estimate_tokens("<|start|>") == len("<|start|>")
    assert sorted(p.name for p in cache.iterdir()) == [
        sha1(estimators.HARMONY_RANKS_URL.encode()).hexdigest()
    ]


def test_verified_harmony_estimator_rejects_changed_or_missing_cache(synthetic_harmony_cache):
    cache, path = synthetic_harmony_cache
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="CACHE_IDENTITY_DRIFT"):
        estimators.VerifiedHarmonyEstimator(cache)
    path.unlink()
    with pytest.raises(ValueError, match="CACHE_MISSING"):
        estimators.VerifiedHarmonyEstimator(cache)


def test_verified_harmony_estimator_rejects_invalid_rank_data(synthetic_harmony_cache, monkeypatch):
    cache, path = synthetic_harmony_cache
    data = b"YQ== 0\nYQ== 1\n"
    path.write_bytes(data)
    monkeypatch.setattr(estimators, "HARMONY_RANKS_SHA256", sha256(data).hexdigest())
    with pytest.raises(ValueError, match="RANK_FORMAT_INVALID"):
        estimators.VerifiedHarmonyEstimator(cache)


def test_verified_harmony_estimator_feeds_existing_admission(synthetic_harmony_cache, policy):
    cache, _ = synthetic_harmony_cache
    estimator = estimators.VerifiedHarmonyEstimator(cache)
    # Synthetic vocabulary and approval only: verifies the actual consumer
    # measures the shared request, without pretending to attest Groq framing.
    policy = replace(policy, input_estimator=estimator,
                     estimator_evidence_ref="SYNTHETIC_LOCAL_BPE_NOT_PROVIDER_BOUND")
    decision = _verify(policy)
    audit = json.loads(decision.audit_json)
    wire, _ = build_groq_request_kwargs(
        replace(_make_envelope(), model_name=GPT_OSS_120B), OpenAICompatibleDialect())
    serialized = json.dumps(wire, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert audit["input_tokens"] == estimator.estimate_tokens(serialized)
    assert audit["free_tier_witness"]["reserved_tokens"] == audit["input_tokens"] + 256
    assert audit["request_sha256"] == sha256(serialized.encode()).hexdigest()
