import time
import uuid
import sqlite3
from typing import Optional, List
from core.execution.ports import ControlPlanePort, TaskLease
from core.execution.exceptions import OptimisticLockError 

class ControlPlaneRepository(ControlPlanePort):
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

    def pick_task(self, worker_id: str, document_id: str, ast_hash: str) -> Optional[TaskLease]:
        # ULID/UUIDv7 simulado nativamente si no hay dependencias externas
        execution_id = f"exec_{int(time.time()*1000):015d}_{uuid.uuid4().hex[:8]}" 
        now = time.time()
        lease_expires = now + 300
        
        # SOTA: Cero reintentos manuales. Se confía estrictamente en el PRAGMA busy_timeout de SQLite.
        self.conn.execute("BEGIN IMMEDIATE")
        
        cursor = self.conn.execute(
            """UPDATE chunk_tasks 
            SET task_state = 'PROCESSING', lease_owner = ?, lease_expires_at = ?, execution_id = ?
            WHERE task_id = (
                SELECT task_id FROM chunk_tasks 
                WHERE document_id = ? AND ast_hash = ? 
                    AND task_state IN ('PENDING', 'RETRYABLE_ERROR')
                    AND (lease_owner IS NULL OR lease_expires_at < ?)
                ORDER BY created_at ASC LIMIT 1 -- SOTA: Fairness
            ) RETURNING task_id, node_id, execution_id, lease_expires_at""",
            (worker_id, lease_expires, execution_id, document_id, ast_hash, now)
        )
        row = cursor.fetchone()
        self.conn.commit()
        
        if row:
            return TaskLease(
                task_id=row[0], 
                node_id=row[1], 
                execution_id=row[2],
                lease_expires_at=row[3],
                absolute_deadline_monotonic=time.monotonic() + 720.0
            )
        return None

    def acknowledge_execution(self, task_id: str, worker_id: str) -> None:
        now = time.time()
        # SOTA: Fencing Temporal Distribuido
        cursor = self.conn.execute(
            """UPDATE chunk_tasks
               SET task_state = 'COMPLETED', lease_owner = NULL, lease_expires_at = NULL, updated_at = ?
               WHERE task_id = ? AND lease_owner = ? AND lease_expires_at >= ?""",
            (now, task_id, worker_id, now)
        )
        self.conn.commit()
        if cursor.rowcount == 0:
            raise OptimisticLockError(f"Zombie write interceptado: El lease de la tarea {task_id} expiró o fue robado.")

    def abandon_execution(self, task_id: str, worker_id: str, error: str) -> None:
        now = time.time()
        # SOTA: Fencing Temporal Distribuido
        cursor = self.conn.execute(
            """UPDATE chunk_tasks
               SET task_state = CASE 
                       WHEN retry_count + 1 >= max_retries THEN 'FAILED' 
                       ELSE 'RETRYABLE_ERROR' 
                   END,
                   retry_count = retry_count + 1, lease_owner = NULL, lease_expires_at = NULL,
                   error_log = ?, updated_at = ?
               WHERE task_id = ? AND lease_owner = ? AND lease_expires_at >= ?""",
            (error, now, task_id, worker_id, now)
        )
        self.conn.commit()
        
        # SOTA: Aserción simétrica. Si rowcount es 0, el lease ya no nos pertenece.
        if cursor.rowcount == 0:
            raise OptimisticLockError(f"Zombie write interceptado al fallar tarea: El lease de {task_id} expiró o fue robado.")
        
    def renew_task_lease(self, task_id: str, worker_id: str, additional_ttl_sec: int = 300) -> bool:
        now = time.time()
        # SOTA: Fencing temporal doble. Protege contra pausas del GC en el propio hilo de heartbeat.
        cursor = self.conn.execute(
            """UPDATE chunk_tasks
               SET lease_expires_at = ?, updated_at = ?
               WHERE task_id = ? AND lease_owner = ? 
                 AND task_state = 'PROCESSING' 
                 AND lease_expires_at >= ?""",
            (now + additional_ttl_sec, now, task_id, worker_id, now)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def release_task_untouched(self, task_id: str, worker_id: str) -> None:
        """SOTA: Requeue sin penalización con barrera de fencing."""
        now = time.time()
        self.conn.execute(
            """UPDATE chunk_tasks
               SET task_state = 'PENDING', 
                   lease_owner = NULL, lease_expires_at = NULL, updated_at = ?
               WHERE task_id = ? AND lease_owner = ? AND lease_expires_at >= ?""",
            (now, task_id, worker_id, now)
        )
        self.conn.commit()