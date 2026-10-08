"""
Tests de visibilidad operacional mínima (NADR-F18-02 §5.7 R23-R26).
"""
import logging
from dataclasses import FrozenInstanceError

import pytest

from core.execution.visibility import (
    OperationalVisibilityPort,
    WorkUnitObservation,
    WorkUnitStatus,
)
from runtime.operational_visibility import StructuredLogVisibility


class TestWorkUnitStatusTaxonomy:
    def test_exactly_six_statuses(self):
        assert len(WorkUnitStatus) == 6

    def test_canonical_members(self):
        assert {s.name for s in WorkUnitStatus} == {
            "CLAIMED", "PROCESSING", "COMPLETED",
            "CANCELLED", "FAILED", "RELEASED",
        }


class TestWorkUnitObservation:
    def test_observation_is_immutable(self):
        obs = WorkUnitObservation(
            task_id="t1", worker_id="w1", status=WorkUnitStatus.CLAIMED
        )
        with pytest.raises(FrozenInstanceError):
            obs.status = WorkUnitStatus.FAILED  # type: ignore[misc]

    def test_observation_carries_no_scientific_payload(self):
        """R25/R26: la observación no transporta contenido científico."""
        obs = WorkUnitObservation(
            task_id="t1", worker_id="w1", status=WorkUnitStatus.COMPLETED
        )
        fields = {f for f in obs.__dataclass_fields__}
        assert fields == {"task_id", "worker_id", "status", "reason", "observed_at"}


class TestStructuredLogVisibility:
    def test_implements_port(self):
        assert isinstance(StructuredLogVisibility(), OperationalVisibilityPort)

    def test_observe_does_not_raise(self, caplog):
        vis = StructuredLogVisibility()
        with caplog.at_level(logging.INFO):
            vis.observe(WorkUnitObservation(
                task_id="abcdef123456", worker_id="node-1",
                status=WorkUnitStatus.PROCESSING,
            ))
        assert any("[VISIBILITY]" in r.message for r in caplog.records)

    def test_observe_is_fail_safe(self, caplog, monkeypatch):
        """Si el sink falla, observe() no propaga ni silencia (§IV)."""
        vis = StructuredLogVisibility()

        def broken_info(*args, **kwargs):
            raise RuntimeError("sink down")

        monkeypatch.setattr(
            "runtime.operational_visibility.logger.info", broken_info
        )
        with caplog.at_level(logging.ERROR):
            vis.observe(WorkUnitObservation(
                task_id="t1", worker_id="w1", status=WorkUnitStatus.FAILED
            ))
        assert any("observe failed" in r.message for r in caplog.records)