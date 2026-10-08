"""
Tests del mecanismo de cancelación cooperativa (NADR-F18-02 §5.4 R11-R14).
"""
import threading
import time

import pytest

from core.execution.cancellation import CancellationToken, TaskOutcome
from core.execution.exceptions import TaskCancelledError


class TestTaskOutcomeTaxonomy:
    def test_exactly_three_outcomes(self):
        assert len(TaskOutcome) == 3

    def test_canonical_members(self):
        assert {o.name for o in TaskOutcome} == {"COMPLETED", "CANCELLED", "FAILED"}


class TestCancellationToken:
    def test_fresh_token_not_cancelled(self):
        token = CancellationToken()
        assert token.is_cancelled() is False
        token.raise_if_cancelled()  # no debe lanzar

    def test_cancel_sets_reason_and_flag(self):
        token = CancellationToken()
        token.cancel("user_request")
        assert token.is_cancelled() is True
        assert token.reason == "user_request"

    def test_raise_if_cancelled_raises_with_reason(self):
        token = CancellationToken()
        token.cancel("resource_pressure")
        with pytest.raises(TaskCancelledError) as exc:
            token.raise_if_cancelled()
        assert exc.value.reason == "resource_pressure"

    def test_first_reason_wins(self):
        token = CancellationToken()
        token.cancel("first")
        token.cancel("second")
        assert token.reason == "first"

    def test_parent_stop_cancels_child_token(self):
        parent = threading.Event()
        token = CancellationToken(parent=parent)
        assert token.is_cancelled() is False
        parent.set()
        assert token.is_cancelled() is True
        assert token.reason == "global_stop"

    def test_thread_safe_cancel_visibility(self):
        token = CancellationToken()

        def canceller():
            time.sleep(0.05)
            token.cancel("from_thread")

        threading.Thread(target=canceller, daemon=True).start()
        deadline = time.monotonic() + 1.0
        while not token.is_cancelled() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert token.is_cancelled() is True
        assert token.reason == "from_thread"
    
    def test_reset_clears_cancellation(self):
        token = CancellationToken()
        token.cancel("test")
        assert token.is_cancelled() is True
        token.reset()
        assert token.is_cancelled() is False
        assert token.reason == ""