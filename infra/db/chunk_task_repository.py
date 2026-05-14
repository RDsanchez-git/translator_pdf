import time
import sqlite3
import uuid
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class ChunkTaskRepository:
    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection

    def enqueue_tasks(self, document_id: str, ast_hash: str, nodes: List[str]) -> None:
        """SOTA: Encolado masivo idempotente."""
        now = time.time()
        tasks = [
            (f"task_{uuid.uuid4().hex[:8]}", document_id, ast_hash, node, 'PENDING', now, now)
            for node in nodes
        ]
        self.db.executemany(
            """INSERT OR IGNORE INTO chunk_tasks 
               (task_id, document_id, ast_hash, node_id, task_state, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            tasks
        )

    def pick_task(self, worker_id: str, document_id: str, ast_hash: str) -> Optional[dict]:
        execution_id = f"exec_{uuid.uuid4().hex[:8]}" # SOTA: Nueva llave de idempotencia
        now = time.time()
        ttl = now + 300
        
        cursor = self.db.execute(
            """UPDATE chunk_tasks
            SET task_state = 'PROCESSING',
                lease_owner = ?,
                lease_expires_at = ?,
                execution_id = ? -- Blindamos causalidad
            WHERE task_id = (
                SELECT task_id FROM chunk_tasks 
                WHERE document_id = ? AND ast_hash = ?
                    AND task_state IN ('PENDING', 'RETRYABLE_ERROR')
                    AND (lease_owner IS NULL OR lease_expires_at < ?)
                LIMIT 1
            )
            RETURNING task_id, node_id, execution_id""",
            (worker_id, ttl, execution_id, document_id, ast_hash, now)
        )
        row = cursor.fetchone()
        return {"task_id": row[0], "node_id": row[1], "retry_count": row[2]} if row else None

    def renew_task_lease(self, task_id: str, worker_id: str, ttl_sec: int = 300) -> None:
        """SOTA: Heartbeat granular para operaciones largas de red (LLMs)."""
        now = time.time()
        expires = now + ttl_sec
        cursor = self.db.execute(
            """UPDATE chunk_tasks
               SET last_heartbeat_at = ?,
                   lease_expires_at = ?,
                   updated_at = ?
               WHERE task_id = ? AND lease_owner = ? AND lease_expires_at >= ?""",
            (now, expires, now, task_id, worker_id, now)
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Fallo al renovar lease de task {task_id}. Propiedad perdida.")

    def complete_task(self, task_id: str, worker_id: str) -> None:
        """SOTA: Cierre con Fencing Temporal estricto para evitar zombie writes."""
        now = time.time()
        cursor = self.db.execute(
            """UPDATE chunk_tasks
               SET task_state = 'COMPLETED',
                   lease_owner = NULL,
                   lease_expires_at = NULL,
                   updated_at = ?
               WHERE task_id = ? AND lease_owner = ? AND lease_expires_at >= ?""",
            (now, task_id, worker_id, now)
        )
        if cursor.rowcount == 0:
            logger.warning(f"ZOMBIE WRITE REJECTED: Worker {worker_id} intentó completar {task_id} con lease expirado.")

    def fail_task(self, task_id: str, worker_id: str, error: str) -> None:
        """SOTA: Poison Pill Prevention. La DB decide matemáticamente el estado de retry."""
        now = time.time()
        cursor = self.db.execute(
            """UPDATE chunk_tasks
               SET task_state = CASE 
                       WHEN retry_count + 1 >= max_retries THEN 'FAILED' 
                       ELSE 'RETRYABLE_ERROR' 
                   END,
                   retry_count = retry_count + 1,
                   lease_owner = NULL,
                   lease_expires_at = NULL,
                   error_log = ?,
                   updated_at = ?
               WHERE task_id = ? AND lease_owner = ? AND lease_expires_at >= ?""",
            (error, now, now, task_id, worker_id, now)
        )
        if cursor.rowcount == 0:
            logger.warning(f"ZOMBIE FAIL REJECTED: Worker {worker_id} intentó fallar {task_id} con lease expirado.")