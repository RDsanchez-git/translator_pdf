"""Test-only adapter for partial reconciler collaborators on offline guard paths.

These tests deliberately pass None or fail-fast fakes for *forbidden* legacy
paths. Keep the real ReconcilerDaemon constructor and its thread/lease setup;
confine nominal type adaptations to this test helper instead of weakening
production signatures or replacing absent dependencies with permissive mocks.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from typing import cast

from apps.daemons.reconciler import ReconcilerDaemon
from core.execution.handlers import DocumentCommandHandler, ReconciliationCommandHandler
from infra.db.control_repo import ControlPlaneRepository
from infra.db.event_repo import EventPlaneRepository
from infra.db.system_repo import SystemPlaneRepository


def make_reconciler_with_test_doubles(
    system_repo: object,
    task_repo: object,
    event_repo: object,
    recon_cmd_handler: object,
    doc_cmd_handler: object,
    *,
    heartbeat_system_factory: Callable[[], tuple[object, sqlite3.Connection]] | None = None,
) -> ReconcilerDaemon:
    """Construct the actual daemon with deliberate partial/offline test doubles."""
    return ReconcilerDaemon(
        system_repo=cast(SystemPlaneRepository, system_repo),
        task_repo=cast(ControlPlaneRepository, task_repo),
        event_repo=cast(EventPlaneRepository, event_repo),
        recon_cmd_handler=cast(ReconciliationCommandHandler, recon_cmd_handler),
        doc_cmd_handler=cast(DocumentCommandHandler, doc_cmd_handler),
        heartbeat_system_factory=cast(
            Callable[[], tuple[SystemPlaneRepository, sqlite3.Connection]] | None,
            heartbeat_system_factory,
        ),
    )
