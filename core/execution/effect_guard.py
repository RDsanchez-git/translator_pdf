"""Per-attempt pre-provider guard; propagated through SyncProviderBridge's asyncio task.

This is operational authority only. Never carries SQLite connections across
threads and never changes scientific or generation identity.
"""
from collections.abc import Callable
from contextvars import ContextVar
from threading import Lock
import time

from core.execution.exceptions import G3ExternalEffectNotStartedError, MalformedInferenceResponse

g3_pre_effect_guard: ContextVar[Callable[[], None] | None] = ContextVar(
    "g3_pre_effect_guard", default=None,
)

# Worker-thread persistence of an operational attempt's admission evidence.
# Not a scientific or generation identity component.
g3_admission_audit_writer: ContextVar[Callable[[str, str], None] | None] = ContextVar(
    "g3_admission_audit_writer", default=None,
)


class FreeWitnessDispatchPermit:
    """In-process continuation of a committed one-shot admission.

    Construct only after the durable admission writer returns. Not an
    independent authorization or a cross-database reservation. The same object
    travels through the quota stack; no reset after a failed SDK call.
    """

    def __init__(self, request_sha256: str, valid_until_ns: int,
                 input_tokens: int, output_tokens: int) -> None:
        self._request_sha256 = request_sha256
        self._valid_until_ns = valid_until_ns
        self._input_tokens = input_tokens
        self._output_tokens = output_tokens
        self._used = False
        self._transport_entered = False
        self._lock = Lock()

    @property
    def reserved_tokens(self) -> int:
        return self._input_tokens + self._output_tokens

    def claim(self, request_sha256: str) -> None:
        with self._lock:
            if self._used:
                # A previous entry may already have caused an effect. Never
                # turn this into positive proof of no-start for the attempt.
                raise MalformedInferenceResponse("PPPR_G5_FREE_DISPATCH_ALREADY_ENTERED")
            if request_sha256 != self._request_sha256:
                raise G3ExternalEffectNotStartedError(
                    "PPPR_G5_FREE_DISPATCH_REQUEST_DRIFT", permanent=True,
                )
            guard = g3_pre_effect_guard.get()
            if guard is None:
                raise G3ExternalEffectNotStartedError(
                    "PPPR_G5_FREE_DISPATCH_AUTHORITY_REQUIRED", permanent=True,
                )
            if time.time_ns() >= self._valid_until_ns:
                raise G3ExternalEffectNotStartedError("PPPR_G5_FREE_EVIDENCE_STALE", permanent=True)
            guard()
            # The authority read may itself block on SQLite contention.
            if time.time_ns() >= self._valid_until_ns:
                raise G3ExternalEffectNotStartedError("PPPR_G5_FREE_EVIDENCE_STALE", permanent=True)
            self._used = True

    def claim_transport(self, request_sha256: str) -> None:
        """Last local HTTP boundary; SDK entry alone is not a sent request.

        Errors here are conservatively post-SDK, never positive no-start
        evidence. No reset even if the underlying transport raises.
        """
        with self._lock:
            if not self._used or self._transport_entered:
                raise MalformedInferenceResponse("PPPR_G5_FREE_HTTP_PERMIT_NOT_AVAILABLE")
            if request_sha256 != self._request_sha256:
                raise MalformedInferenceResponse("PPPR_G5_FREE_HTTP_REQUEST_DRIFT")
            guard = g3_pre_effect_guard.get()
            if guard is None or time.time_ns() >= self._valid_until_ns:
                raise MalformedInferenceResponse("PPPR_G5_FREE_HTTP_AUTHORITY_EXPIRED")
            guard()
            if time.time_ns() >= self._valid_until_ns:
                raise MalformedInferenceResponse("PPPR_G5_FREE_HTTP_AUTHORITY_EXPIRED")
            self._transport_entered = True

    def check_reported_usage(self, input_tokens: int, output_tokens: int) -> None:
        if input_tokens > self._input_tokens or output_tokens > self._output_tokens:
            raise MalformedInferenceResponse("PPPR_G5_FREE_RESPONSE_USAGE_EXCEEDS_ADMISSION")


g3_free_dispatch_permit: ContextVar[FreeWitnessDispatchPermit | None] = ContextVar(
    "g3_free_dispatch_permit", default=None,
)
