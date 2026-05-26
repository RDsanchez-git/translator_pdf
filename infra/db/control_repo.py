import time
import uuid
import sqlite3
import logging
from typing import Optional, List
from core.execution.ports import ControlPlanePort, TaskLease
from core.execution.exceptions import OptimisticLockError 

logger = logging.getLogger(__name__)

class ControlPlaneRepository(ControlPlanePort):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def enqueue_tasks(self, document_id: str, ast_hash: str, nodes: List[str]) -> None:
        """Inyección atómica masiva de chunks con Hash Determinístico compuesto anti-colisiones."""
        import hashlib
        now = time.time()
        
        tasks = []
        for node in nodes:
            raw_seed = f"{document_id}:{ast_hash}:{node}".encode('utf-8')
            task_hash = hashlib.sha256(raw_seed).hexdigest()[:24]
            task_id = f"task_{task_hash}"
            
            tasks.append((task_id, document_id, ast_hash, node, 'PENDING', None, now, now))
            
        self.conn.executemany(
            """INSERT OR IGNORE INTO chunk_tasks 
               (task_id, document_id, ast_hash, node_id, task_state, execution_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            tasks
        )
        self.conn.commit()

    def pick_task(self, worker_id: str, document_id: str, ast_hash: str) -> Optional[TaskLease]:
        execution_id = f"exec_{int(time.time()*1000):015d}_{uuid.uuid4().hex[:8]}" 
        now = time.time()
        lease_expires = now + 300
        
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            
            cursor = self.conn.execute(
                """UPDATE chunk_tasks 
                SET task_state = 'PROCESSING', lease_owner = ?, lease_expires_at = ?, execution_id = ?
                WHERE task_id = (
                    SELECT task_id FROM chunk_tasks 
                    WHERE document_id = ? AND ast_hash = ? 
                        AND task_state IN ('PENDING', 'RETRYABLE_ERROR')
                        AND (lease_owner IS NULL OR lease_expires_at < ?)
                    ORDER BY created_at ASC LIMIT 1
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
        except Exception:
            self.conn.rollback()
            raise

    def acknowledge_execution(self, task_id: str, worker_id: str) -> None:
        now = time.time()
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
        
        if cursor.rowcount == 0:
            raise OptimisticLockError(f"Zombie write interceptado al fallar tarea: El lease de {task_id} expiró o fue robado.")
        
    def renew_task_lease(self, task_id: str, worker_id: str, additional_ttl_sec: int = 300) -> bool:
        now = time.time()
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
        now = time.time()
        cursor = self.conn.execute(
            """UPDATE chunk_tasks
               SET task_state = 'PENDING', 
                   lease_owner = NULL, lease_expires_at = NULL, updated_at = ?
               WHERE task_id = ? AND lease_owner = ? AND lease_expires_at >= ?""",
            (now, task_id, worker_id, now)
        )
        self.conn.commit()
        if cursor.rowcount == 0:
            raise OptimisticLockError(f"Zombie write interceptado al liberar: El lease de {task_id} expiró o fue robado.")

    def mark_cqrs_reconciled(self, task_id: str, reconciliation_id: str) -> bool:
        now = time.time()
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO processed_reconciliation_commands (reconciliation_id, processed_at) VALUES (?, ?)",
                (reconciliation_id, now)
            )
            if cursor.rowcount == 0:
                self.conn.rollback()
                return False
            
            self.conn.execute(
                """UPDATE chunk_tasks 
                   SET task_state = 'COMPLETED', lease_owner = NULL, lease_expires_at = NULL, updated_at = ? 
                   WHERE task_id = ?""",
                (now, task_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e
        
    def mark_zombie_recovered(self, task_id: str, reconciliation_id: str) -> bool:
        now = time.time()
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO processed_reconciliation_commands (reconciliation_id, processed_at) VALUES (?, ?)",
                (reconciliation_id, now)
            )
            if cursor.rowcount == 0:
                self.conn.rollback()
                return False
            
            self.conn.execute(
                """UPDATE chunk_tasks 
                   SET task_state = 'PENDING', lease_owner = NULL, lease_expires_at = NULL, 
                       retry_count = retry_count + 1, updated_at = ? 
                   WHERE task_id = ?""",
                (now, task_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e
        
    def enqueue_assembler_task(self, task_id: str, document_id: str, ast_hash: str) -> bool:
        now = time.time()
        try:
            self.conn.execute("""
                INSERT INTO chunk_tasks 
                (task_id, document_id, ast_hash, node_id, task_state, worker_type, created_at, updated_at, state_version)
                VALUES (?, ?, ?, 'ROOT_ASSEMBLY', 'PENDING', 'ASSEMBLER', ?, ?, 0)
            """, (task_id, document_id, ast_hash, now, now))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            if self.conn.in_transaction:
                self.conn.rollback()
            logger.info(f"Idempotencia detectada: la tarea {task_id[:12]} ya fue encolada previamente.")
            return False
        except Exception as e:
            if self.conn.in_transaction:
                self.conn.rollback()
            logger.error(f"Fallo lasing tarea ASSEMBLER: {e}")
            raise e
        
    def find_documents_with_pending_chunks(self, sample_size: int = 10) -> list[tuple[str, str]]:
        cursor = self.conn.execute(
            """
            SELECT DISTINCT f.document_id, f.ast_hash
            FROM fsm_db.document_fsm f
            WHERE f.current_state = 'PROCESSING'
              AND (
                  EXISTS (
                      SELECT 1 FROM chunk_tasks t2
                      WHERE t2.document_id = f.document_id
                        AND t2.ast_hash = f.ast_hash
                        AND t2.task_state IN ('PENDING', 'RETRYABLE_ERROR')
                  )
                  OR NOT EXISTS (
                      SELECT 1 FROM chunk_tasks t3
                      WHERE t3.document_id = f.document_id
                        AND t3.ast_hash = f.ast_hash
                        AND t3.task_state IN ('PENDING', 'PROCESSING', 'RETRYABLE_ERROR')
                  )
              )
            ORDER BY f.updated_at ASC
            LIMIT ?
            """,
            (sample_size,)
        )
        return cursor.fetchall()