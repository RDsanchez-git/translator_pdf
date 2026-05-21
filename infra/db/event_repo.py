import time
import uuid
import sqlite3
from typing import Optional
from core.execution.ports import EventPlanePort, ReplayPayload, EventLifecycle 
from collections import namedtuple

EventRecord = namedtuple(
    "EventRecord",
    [
        'execution_id',
        'document_id',
        'node_id',
        'content_hash',
        'raw_response',
        'prompt_version',
        'model_version',
        'projection_version',
        'lifecycle',
        'timestamp'
    ]
)

class EventPlaneRepository(EventPlanePort):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_replay(self, content_hash: str, prompt_v: str, model_v: str) -> Optional[ReplayPayload]:
        # SOTA: Causal Ordering utilizando execution_id monotónico en lugar de timestamp
        cursor = self.conn.execute(
            """SELECT raw_response, projection_version, execution_id FROM chunk_events_log 
               WHERE content_hash = ? AND prompt_version = ? AND model_version = ? 
               ORDER BY execution_id DESC LIMIT 1""",
            (content_hash, prompt_v, model_v)
        )
        row = cursor.fetchone()
        if row:
            return ReplayPayload(raw_response=row[0], projection_version=row[1], execution_id=row[2])
        return None

    def append_wal(self, execution_id: str, document_id: str, node_id: str, content_hash: str, 
                   raw_response: str, prompt_v: str, model_v: str, projection_v: int, lifecycle: EventLifecycle) -> None:
        # SOTA: Idempotencia fuerte. ON CONFLICT DO NOTHING evita duplicación si el worker colapsa en el CQRS y re-ejecuta
        self.conn.execute(
            """INSERT INTO chunk_events_log 
               (event_id, execution_id, document_id, node_id, content_hash, raw_response, 
                prompt_version, model_version, projection_version, lifecycle, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(execution_id, node_id) DO NOTHING""",
            (uuid.uuid4().hex, execution_id, document_id, node_id, content_hash, raw_response, 
             prompt_v, model_v, projection_v, lifecycle.value, time.time())
        )
        self.conn.commit()

    def get_latest_event(self, node_id: str):
        cursor = self.conn.execute(
            """
            SELECT execution_id, document_id, node_id,
                content_hash, raw_response,
                prompt_version, model_version,
                projection_version, lifecycle, timestamp
            FROM chunk_events_log
            WHERE node_id = ?
            ORDER BY execution_id DESC
            LIMIT 1
            """,
            (node_id,)
        )

        row = cursor.fetchone()

        if not row:
            return None

        return EventRecord(*row)