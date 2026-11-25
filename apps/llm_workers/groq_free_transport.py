"""Last local HTTP boundary for an explicitly composed one-shot Groq witness.

No default network transport is created here. The composition root must own
the inner transport, TLS policy and host isolation. This wrapper alone grants
neither egress nor account entitlement.
"""
from hashlib import sha256
import json
import logging
import time

import httpx

from core.execution.effect_guard import g3_free_dispatch_permit
from core.execution.exceptions import MalformedInferenceResponse
from core.utils.telemetry import ctx_task_id, ctx_execution_id

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
logger = logging.getLogger(__name__)
_MAX_BODY_BYTES = 128 * 1024


class GroqFreeWitnessTransport(httpx.AsyncBaseTransport):
    """Validate the SDK's actual serialized body before delegating once.

    Never follow redirects or retry here. The owner must also configure the
    SDK and HTTP client with zero retries, redirects off and trust_env=False.
    No headers containing credentials or payloads are logged.
    """

    def __init__(self, inner: httpx.AsyncBaseTransport):
        self._inner = inner

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        permit = g3_free_dispatch_permit.get()
        if permit is None:
            raise MalformedInferenceResponse("PPPR_G5_FREE_HTTP_PERMIT_NOT_AVAILABLE")
        if request.method != "POST" or str(request.url) != GROQ_CHAT_URL:
            raise MalformedInferenceResponse("PPPR_G5_FREE_HTTP_DESTINATION_REJECTED")
        if request.headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
            raise MalformedInferenceResponse("PPPR_G5_FREE_HTTP_CONTENT_TYPE_REJECTED")
        try:
            body = request.content
            if not body or len(body) > _MAX_BODY_BYTES:
                raise ValueError("body size")
            def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
                result: dict[str, object] = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError("duplicate key")
                    result[key] = value
                return result

            parsed = json.loads(body, object_pairs_hook=unique_object)
            if not isinstance(parsed, dict):
                raise ValueError("body shape")
            canonical = json.dumps(parsed, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":"), allow_nan=False)
        except (ValueError, TypeError, httpx.RequestNotRead) as exc:
            raise MalformedInferenceResponse("PPPR_G5_FREE_HTTP_BODY_INVALID") from exc
        digest = sha256(canonical.encode("utf-8")).hexdigest()
        # No await between final authority check and transport delegation.
        permit.claim_transport(digest)
        response = await self._inner.handle_async_request(request)
        # A response status/header observation is not proof of billing, model
        # application or remaining quota BEFORE the call. Missing stays null.
        remaining: dict[str, int | None] = {}
        for key in ("x-ratelimit-limit-requests", "x-ratelimit-remaining-requests",
                    "x-ratelimit-limit-tokens", "x-ratelimit-remaining-tokens"):
            value = response.headers.get(key, "")
            remaining[key] = int(value) if value.isascii() and value.isdecimal() and len(value) <= 12 else None
        logger.info("PPPR_G5_FREE_HTTP_RESPONSE", extra={"extra_data": {
            "task_id": ctx_task_id.get(), "execution_id": ctx_execution_id.get(),
            "request_sha256": digest, "observed_at_ns": time.time_ns(),
            "http_status": response.status_code,
            "rpd_tpm_headers": remaining,
        }})
        return response

    async def aclose(self) -> None:
        await self._inner.aclose()
