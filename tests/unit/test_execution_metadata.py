"""
Tests de metadata operacional de ejecución (NADR-F18-01 §5.2 R7, R9; §5.3 R13).
Verifica resolución de DF-13.
"""
from dataclasses import FrozenInstanceError

import pytest

from core.benchmark.verification.execution_metadata import ExecutionMetadata


class TestExecutionMetadata:
    def test_metadata_is_immutable(self):
        meta = ExecutionMetadata(
            model_de_execution="sequential_regression",
            execution_timestamp_iso8601="2026-10-05T12:00:00Z",
        )
        with pytest.raises(FrozenInstanceError):
            meta.model_de_execution = "async"  # type: ignore[misc]

    def test_metadata_carries_model_de_execution(self):
        """DF-13: model_de_execution identificable (R7, R9)."""
        meta = ExecutionMetadata(
            model_de_execution="sequential_daemon",
            execution_timestamp_iso8601="2026-10-05T12:00:00Z",
        )
        assert meta.model_de_execution == "sequential_daemon"

    def test_metadata_telemetry_id_optional(self):
        """telemetry_execution_id es opcional (None por default)."""
        meta = ExecutionMetadata(
            model_de_execution="sequential_regression",
            execution_timestamp_iso8601="2026-10-05T12:00:00Z",
        )
        assert meta.telemetry_execution_id is None

    def test_metadata_separate_from_identity_chain(self):
        """R8: metadata operacional NO forma parte de IdentityChain."""
        from core.benchmark.verification.identity_chain import IdentityChain
        
        identity_fields = {f for f in IdentityChain.__dataclass_fields__}
        assert "model_de_execution" not in identity_fields
        assert "execution_metadata" not in identity_fields