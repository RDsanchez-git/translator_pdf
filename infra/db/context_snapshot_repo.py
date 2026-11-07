"""W08-2b: queue.db-owned, generation-bound context snapshots.

The adapter owns *one local SQLite transaction* for context rows and G3
ChunkPlan/tasks. It does not migrate legacy plans, authorize LLM inference,
change a provider cache, or bridge separate SQLite databases.
"""
from __future__ import annotations

import sqlite3
import time
from typing import Sequence

from core.ast.models import ASTNode
from core.chunking.manifest_contract import ChunkPlan
from core.context.plan_context_contract import derive_verified_plan_contexts
from core.context.snapshot_contract import ContextSnapshotV1
from infra.db.control_repo import ControlPlaneRepository


_CONTEXT_SNAPSHOTS_DDL = """CREATE TABLE IF NOT EXISTS g3_context_snapshots (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    manifest_sha256 TEXT NOT NULL CHECK(length(manifest_sha256) = 64),
    context_id TEXT NOT NULL,
    snapshot_sha256 TEXT NOT NULL CHECK(length(snapshot_sha256) = 64),
    snapshot_json TEXT NOT NULL,
    created_at REAL NOT NULL,
    PRIMARY KEY (document_id, ast_hash, context_id),
    FOREIGN KEY (document_id, ast_hash)
        REFERENCES chunk_plans(document_id, ast_hash)
)"""


class DurableContextPlanRepository:
    """Explicit W08 adapter; the current OCR router does NOT invoke this API."""

    def __init__(self, repo: ControlPlaneRepository):
        self._repo = repo

    def enqueue_verified(self, plan: ChunkPlan, ast: Sequence[ASTNode]) -> None:
        """Atomically commit a verified plan, tasks and contextual snapshots.

        Existing legacy plans with the same manifest but no snapshots are not
        silently adopted. Repetition of an identical committed request is safe.
        """
        snapshots = derive_verified_plan_contexts(plan, ast)
        with self._repo.chunk_plan_write_scope():
            self._repo.enqueue_chunk_plan(plan, ast)
            self._repo.conn.execute(_CONTEXT_SNAPSHOTS_DDL)

            existing = self._read_rows(plan.document_id, plan.ast_hash)
            expected = {
                context_id: (plan.digest, snapshot.snapshot_sha256, snapshot.to_json())
                for context_id, snapshot in snapshots.items()
            }
            if existing:
                if existing != expected:
                    raise ValueError("W08_CONTEXT_SNAPSHOT_SET_CONFLICT")
                return

            # A manifest with actual inference but missing all context rows
            # indicates a legacy/corrupt generation, not a reason to infer.
            self._repo.conn.executemany(
                "INSERT INTO g3_context_snapshots "
                "(document_id, ast_hash, manifest_sha256, context_id, "
                "snapshot_sha256, snapshot_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (plan.document_id, plan.ast_hash, plan.digest, context_id,
                     snapshot.snapshot_sha256, snapshot.to_json(), time.time())
                    for context_id, snapshot in sorted(snapshots.items())
                ],
            )

    def load_verified(
        self, document_id: str, ast_hash: str, ast: Sequence[ASTNode],
    ) -> tuple[ChunkPlan, dict[str, ContextSnapshotV1]]:
        """Hydrate from a NEW SQLite connection and fail closed on any drift."""
        with self._repo.chunk_plan_write_scope():
            plan = self._repo.load_chunk_plan(document_id, ast_hash, ast)
            expected = derive_verified_plan_contexts(plan, ast)
            try:
                stored = self._read_rows(document_id, ast_hash)
            except sqlite3.OperationalError as exc:
                raise ValueError("W08_CONTEXT_SNAPSHOT_STORE_UNAVAILABLE") from exc
            if set(stored) != set(expected):
                raise ValueError("W08_CONTEXT_SNAPSHOT_COVERAGE_MISMATCH")
            for context_id, snap in expected.items():
                manifest, digest, payload = stored[context_id]
                if manifest != plan.digest or digest != snap.snapshot_sha256:
                    raise ValueError("W08_CONTEXT_SNAPSHOT_IDENTITY_MISMATCH")
                try:
                    loaded = ContextSnapshotV1.from_json(payload)
                except (ValueError, TypeError, KeyError) as exc:
                    raise ValueError("W08_CONTEXT_SNAPSHOT_CORRUPT") from exc
                if loaded != snap:
                    raise ValueError("W08_CONTEXT_SNAPSHOT_SOURCE_MISMATCH")
            return plan, expected

    def _read_rows(
        self, document_id: str, ast_hash: str,
    ) -> dict[str, tuple[str, str, str]]:
        rows = self._repo.conn.execute(
            "SELECT context_id, manifest_sha256, snapshot_sha256, snapshot_json "
            "FROM g3_context_snapshots WHERE document_id=? AND ast_hash=?",
            (document_id, ast_hash),
        ).fetchall()
        return {
            context_id: (manifest, digest, payload)
            for context_id, manifest, digest, payload in rows
        }
