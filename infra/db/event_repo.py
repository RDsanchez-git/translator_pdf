import time
import uuid
import sqlite3
from typing import Optional

class EventPlaneRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_replay(self, content_hash: str, prompt_v: str, model_v: str) -> Optional[str]:
        cursor = self.conn.execute(
            """SELECT raw_response FROM chunk_events_log 
               WHERE content_hash = ? AND prompt_version = ? AND model_version = ? 
               LIMIT 1""",
            (content_hash, prompt_v, model_v)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def append_wal(self, execution_id: str, document_id: str, node_id: str, content_hash: str, 
                   raw_response: str, prompt_v: str, model_v: str, projection_v: int):
        self.conn.execute(
            """INSERT INTO chunk_events_log 
               (event_id, execution_id, document_id, node_id, content_hash, raw_response, 
                prompt_version, model_version, projection_version, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (uuid.uuid4().hex, execution_id, document_id, node_id, content_hash, raw_response, 
             prompt_v, model_v, projection_v, time.time())
        )
        self.conn.commit()