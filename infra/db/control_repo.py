import time
import uuid
import sqlite3
from typing import Optional, List

class ControlPlaneRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def enqueue_tasks(self, document_id: str, ast_hash: str, nodes: List[str]) -> None:
        now = time.time()
        tasks = [
            (f"task_{uuid.uuid4().hex[:8]}", document_id, ast_hash, node, 'PENDING', None, now, now)
            for node in nodes
        ]
        self.conn.executemany(
            """INSERT OR IGNORE INTO chunk_tasks 
               (task_id, document_id, ast_hash, node_id, task_state, execution_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            tasks
        )
        self.conn.commit()

    def pick_task(self, worker_id: str, document_id: str, ast_hash: str) -> Optional[dict]:
        execution_id = f"exec_{int(time.time()*1000)}_{uuid.uuid4().hex[:4]}"
        now = time.time()
        
        cursor = self.conn.execute(
            """UPDATE chunk_tasks 
               SET task_state = 'PROCESSING', lease_owner = ?, lease_expires_at = ?, execution_id = ?
               WHERE task_id = (
                   SELECT task_id FROM chunk_tasks 
                   WHERE document_id = ? AND ast_hash = ? 
                     AND task_state IN ('PENDING', 'RETRYABLE_ERROR')
                     AND (lease_owner IS NULL OR lease_expires_at < ?)
                   LIMIT 1
               ) RETURNING task_id, node_id, execution_id""",
            (worker_id, now + 300, execution_id, document_id, ast_hash, now)
        )
        row = cursor.fetchone()
        if row:
            self.conn.commit()
            return {"task_id": row[0], "node_id": row[1], "execution_id": row[2]}
        return None

    def complete_task(self, task_id: str, worker_id: str) -> None:
        now = time.time()
        self.conn.execute(
            """UPDATE chunk_tasks
               SET task_state = 'COMPLETED', lease_owner = NULL, lease_expires_at = NULL, updated_at = ?
               WHERE task_id = ? AND lease_owner = ?""",
            (now, task_id, worker_id)
        )
        self.conn.commit()

    def fail_task(self, task_id: str, worker_id: str, error: str) -> None:
        now = time.time()
        self.conn.execute(
            """UPDATE chunk_tasks
               SET task_state = CASE 
                       WHEN retry_count + 1 >= max_retries THEN 'FAILED' 
                       ELSE 'RETRYABLE_ERROR' 
                   END,
                   retry_count = retry_count + 1, lease_owner = NULL, lease_expires_at = NULL,
                   error_log = ?, updated_at = ?
               WHERE task_id = ? AND lease_owner = ?""",
            (error, now, task_id, worker_id)
        )
        self.conn.commit()