"""Per-attempt pre-provider guard; propagated through SyncProviderBridge's asyncio task.

This is operational authority only. Never carries SQLite connections across
threads and never changes scientific or generation identity.
"""
from collections.abc import Callable
from contextvars import ContextVar

g3_pre_effect_guard: ContextVar[Callable[[], None] | None] = ContextVar(
    "g3_pre_effect_guard", default=None,
)
