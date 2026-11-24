"""Final HTTP guard falsifiers; only MockTransport, never sockets."""
from hashlib import sha256
import json
import time

import httpx
import pytest

from apps.llm_workers.groq_free_transport import GROQ_CHAT_URL, GroqFreeWitnessTransport
from core.execution import effect_guard as guard
from core.execution.exceptions import MalformedInferenceResponse

pytestmark = [pytest.mark.unit, pytest.mark.anyio]
BODY = {"model": "openai/gpt-oss-120b", "stream": False}
DIGEST = sha256(json.dumps(BODY, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":")).encode()).hexdigest()


@pytest.fixture
def scope():
    permit = guard.FreeWitnessDispatchPermit(DIGEST, time.time_ns()+60_000_000_000, 100, 256)
    guard_token = guard.g3_pre_effect_guard.set(lambda: None)
    permit_token = guard.g3_free_dispatch_permit.set(permit)
    try:
        permit.claim(DIGEST)
        yield permit
    finally:
        guard.g3_free_dispatch_permit.reset(permit_token)
        guard.g3_pre_effect_guard.reset(guard_token)


@pytest.mark.parametrize("method,url,body,code", [
    ("GET", GROQ_CHAT_URL, BODY, "DESTINATION_REJECTED"),
    ("POST", GROQ_CHAT_URL + "?extra=1", BODY, "DESTINATION_REJECTED"),
    ("POST", "https://example.invalid/", BODY, "DESTINATION_REJECTED"),
    ("POST", GROQ_CHAT_URL, dict(BODY, stream=True), "REQUEST_DRIFT"),
])
async def test_rejected_wire_never_delegates(scope, method, url, body, code):
    def unexpected(request):
        pytest.fail("unexpected physical transport delegation")

    async with httpx.AsyncClient(transport=GroqFreeWitnessTransport(httpx.MockTransport(unexpected)),
                                 trust_env=False, follow_redirects=False) as client:
        with pytest.raises(MalformedInferenceResponse, match=code):
            await client.request(method, url, json=body)


async def test_duplicate_json_keys_rejected(scope):
    async with httpx.AsyncClient(
        transport=GroqFreeWitnessTransport(httpx.MockTransport(lambda r: pytest.fail("unexpected I/O"))),
        trust_env=False, follow_redirects=False,
    ) as client:
        with pytest.raises(MalformedInferenceResponse, match="BODY_INVALID"):
            await client.post(GROQ_CHAT_URL, content=b'{"stream":false,"stream":false}',
                              headers={"content-type": "application/json"})


@pytest.mark.parametrize("status", [200, 429, 307])
async def test_one_delegation_and_allowlisted_quota_evidence(scope, status, caplog):
    calls = []

    def fake(request):
        calls.append(request)
        return httpx.Response(status, headers={
            "location": "https://example.invalid/", "x-ratelimit-limit-requests": "1000",
            "x-ratelimit-remaining-tokens": "7500", "x-ratelimit-limit-tokens": "invalid",
            "set-cookie": "secret-never-log",
        })

    with caplog.at_level("INFO"):
        async with httpx.AsyncClient(transport=GroqFreeWitnessTransport(httpx.MockTransport(fake)),
                                     trust_env=False, follow_redirects=False) as client:
            response = await client.post(GROQ_CHAT_URL, json=BODY)
            assert response.status_code == status
            with pytest.raises(MalformedInferenceResponse, match="PERMIT_NOT_AVAILABLE"):
                await client.post(GROQ_CHAT_URL, json=BODY)
    assert len(calls) == 1
    events = [r for r in caplog.records if r.getMessage() == "PPPR_G5_FREE_HTTP_RESPONSE"]
    assert len(events) == 1
    assert events[0].extra_data["rpd_tpm_headers"] == {
        "x-ratelimit-limit-requests": 1000, "x-ratelimit-remaining-requests": None,
        "x-ratelimit-limit-tokens": None, "x-ratelimit-remaining-tokens": 7500,
    }
    assert "secret-never-log" not in str(events[0].extra_data)


async def test_transport_failure_does_not_restore_permit(scope):
    calls = []

    def failure(request):
        calls.append(request)
        raise httpx.ReadTimeout("synthetic lost reply")

    async with httpx.AsyncClient(transport=GroqFreeWitnessTransport(httpx.MockTransport(failure)),
                                 trust_env=False, follow_redirects=False) as client:
        with pytest.raises(httpx.ReadTimeout):
            await client.post(GROQ_CHAT_URL, json=BODY)
        with pytest.raises(MalformedInferenceResponse, match="PERMIT_NOT_AVAILABLE"):
            await client.post(GROQ_CHAT_URL, json=BODY)
    assert len(calls) == 1


async def test_free_witness_stack_has_no_implicit_transport_or_default_cache():
    from dataclasses import replace
    from unittest.mock import Mock
    from apps.bootstrap.provider_stack_factory import build_groq_free_witness_stack
    from apps.llm_workers.g3_admission import GPT_OSS_120B
    from core.execution.exceptions import G3ExternalEffectNotStartedError
    from tests.unit.test_adapters import _make_envelope

    # An ordinary stack without a committed permit must never construct a
    # transport or read a live API key. The store is synthetic here.
    store = Mock()
    store.load.return_value = None
    factory = Mock(side_effect=AssertionError("implicit HTTP transport construction"))
    provider = await build_groq_free_witness_stack(
        api_key="synthetic", transport_factory=factory, rate_limit_store=store,
    )
    factory.assert_not_called()
    with pytest.raises(G3ExternalEffectNotStartedError, match="COMPOSITION_SCOPE_REQUIRED"):
        await provider.translate(replace(_make_envelope(), model_name=GPT_OSS_120B))
    factory.assert_not_called()
