"""Physical SQLite maintenance only.

Logical recovery belongs to the existing fenced G3/G5 recovery paths.
Document age alone cannot establish authority to fail or requeue a generation.
"""
import logging
import os
import random
import time
from contextlib import closing
from pathlib import Path

from core.utils.logger import setup_logger
from infra.db.connection import get_connection, resolve_sqlite_path

logger = logging.getLogger(__name__)

FSM_DB_PATH = os.getenv("FSM_DB_PATH", "infra/db/fsm.db")
QUEUE_DB_PATH = os.getenv("QUEUE_DB_PATH", "infra/db/queue.db")
EVENT_DB_PATH = os.getenv("EVENT_DB_PATH", "infra/db/event.db")
MAT_DB_PATH = os.getenv("MAT_DB_PATH", "infra/db/materialized.db")


class RecoveryDaemon:
    """Retain the existing service entrypoint, with no logical FSM authority."""

    def __init__(self):
        self.identity = "sweeper_daemon"

    def _force_wal_checkpoint(self, db_path: str, plane_name: str) -> None:
        """Maintain an existing plane; do not bootstrap absent state."""
        try:
            resolved = resolve_sqlite_path(db_path)
            if not Path(resolved).is_file():
                logger.warning("SWEEPER_WAL_PLANE_MISSING plane=%s", plane_name)
                return
            # sqlite3 connection context managers do not close connections.
            with closing(get_connection(resolved)) as conn:
                row = conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
                if row is None or row[0] != 0:
                    logger.warning("SWEEPER_WAL_CHECKPOINT_INCOMPLETE plane=%s", plane_name)
                else:
                    logger.info("SWEEPER_WAL_CHECKPOINT_OK plane=%s", plane_name)
        except Exception:
            logger.exception("SWEEPER_WAL_CHECKPOINT_FAILED plane=%s", plane_name)

    def run_sweep_cycle(self) -> None:
        """Physical maintenance only, never age-based logical recovery."""
        self._force_wal_checkpoint(EVENT_DB_PATH, "Event Plane")
        self._force_wal_checkpoint(MAT_DB_PATH, "Materialized Plane")
        self._force_wal_checkpoint(FSM_DB_PATH, "FSM Plane")
        self._force_wal_checkpoint(QUEUE_DB_PATH, "Queue Plane")


if __name__ == "__main__":
    setup_logger()
    daemon = RecoveryDaemon()
    logger.info("SWEEPER_WAL_MAINTENANCE_ONLY")
    while True:
        daemon.run_sweep_cycle()
        time.sleep(30 + random.uniform(0.0, 5.0))
