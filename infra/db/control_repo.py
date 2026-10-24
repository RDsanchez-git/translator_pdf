import time
import uuid
import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, List, Sequence
from core.execution.ports import ControlPlanePort, TaskLease
from core.execution.exceptions import OptimisticLockError 
from core.ast.models import ASTNode
from core.chunking.manifest_contract import ChunkPlan
from infra.db.connection import ensure_fsm_database_attached

logger = logging.getLogger(__name__)

_G3_CHUNK_PLAN_DDL = """CREATE TABLE IF NOT EXISTS chunk_plans (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    manifest_sha256 TEXT NOT NULL CHECK(length(manifest_sha256) = 64),
    manifest_json TEXT NOT NULL,
    created_at REAL NOT NULL,
    PRIMARY KEY (document_id, ast_hash)
)"""

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

    @contextmanager
    def _chunk_plan_write_scope(self):
        """SAVEPOINT: transaccion propia durable, ajena permanece bajo su owner."""
        name = f"g3_chunk_plan_{uuid.uuid4().hex}"
        self.conn.execute(f"SAVEPOINT {name}")
        try:
            yield
        except BaseException:
            try:
                self.conn.execute(f"ROLLBACK TO SAVEPOINT {name}")
            finally:
                self.conn.execute(f"RELEASE SAVEPOINT {name}")
            raise
        else:
            self.conn.execute(f"RELEASE SAVEPOINT {name}")

    @staticmethod
    def _chunk_plan_task_ids(plan: ChunkPlan) -> dict[str, str]:
        """Compatible con el task_id estable usado por enqueue_tasks."""
        import hashlib
        task_ids = {
            u.chunk_id: "task_" + hashlib.sha256(
                f"{plan.document_id}:{plan.ast_hash}:{u.chunk_id}".encode("utf-8")
            ).hexdigest()[:24]
            for u in plan.units
        }
        if len(task_ids) != len(plan.units) or len(set(task_ids.values())) != len(task_ids):
            raise ValueError("G3_B2_DUPLICATE_TASK_ID")
        return task_ids

    def _verify_chunk_plan_tasks(self, plan: ChunkPlan) -> None:
        expected = self._chunk_plan_task_ids(plan)
        rows = self.conn.execute(
            "SELECT node_id, task_id FROM chunk_tasks WHERE document_id = ? AND ast_hash = ?",
            (plan.document_id, plan.ast_hash),
        ).fetchall()
        actual = {node_id: task_id for node_id, task_id in rows}
        if len(rows) != len(actual) or actual != expected:
            raise ValueError("G3_B2_QUEUE_MANIFEST_DRIFT")

    def enqueue_chunk_plan(self, plan: ChunkPlan, ast: Sequence[ASTNode]) -> None:
        """Persiste plan + tareas atomicos en queue.db; reintento identico no-op.

        Este API NO habilita Engine: la respuesta estructurada va en G3-B3.
        El campo legacy chunk_tasks.node_id sigue guardando chunk_id.
        """
        verified = ChunkPlan.build(plan.document_id, plan.ast_hash, ast, plan.units)
        if verified.digest != plan.digest:
            raise ValueError("G3_B2_PLAN_VALIDATION_DRIFT")
        payload, digest = verified.to_json(), verified.digest
        now = time.time()
        with self._chunk_plan_write_scope():
            # Migracion compatible para queue.db existentes, DDL revertible.
            self.conn.execute(_G3_CHUNK_PLAN_DDL)
            row = self.conn.execute(
                "SELECT manifest_sha256, manifest_json FROM chunk_plans "
                "WHERE document_id = ? AND ast_hash = ?",
                (plan.document_id, plan.ast_hash),
            ).fetchone()
            if row is not None:
                if row != (digest, payload):
                    raise ValueError("G3_B2_GENERATION_PLAN_CONFLICT")
                self._verify_chunk_plan_tasks(verified)
                return

            # Nunca absorber automaticamente tareas legacy sin manifiesto.
            preexisting = self.conn.execute(
                "SELECT 1 FROM chunk_tasks WHERE document_id = ? AND ast_hash = ? LIMIT 1",
                (plan.document_id, plan.ast_hash),
            ).fetchone()
            if preexisting:
                raise ValueError("G3_B2_LEGACY_TASKS_WITHOUT_PLAN")

            expected = self._chunk_plan_task_ids(verified)
            self.conn.execute(
                "INSERT INTO chunk_plans "
                "(document_id, ast_hash, manifest_sha256, manifest_json, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (plan.document_id, plan.ast_hash, digest, payload, now),
            )
            self.conn.executemany(
                "INSERT INTO chunk_tasks "
                "(task_id, document_id, ast_hash, node_id, task_state, "
                "execution_id, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, 'PENDING', NULL, ?, ?)",
                [
                    (expected[u.chunk_id], plan.document_id, plan.ast_hash,
                     u.chunk_id, now, now)
                    for u in verified.units
                ],
            )
            self._verify_chunk_plan_tasks(verified)

    def load_chunk_plan(self, document_id: str, ast_hash: str,
                        ast: Sequence[ASTNode]) -> ChunkPlan:
        """Rehidrata plan comprobando checksum, AST y asociacion con queue."""
        row = self.conn.execute(
            "SELECT manifest_sha256, manifest_json FROM chunk_plans "
            "WHERE document_id = ? AND ast_hash = ?",
            (document_id, ast_hash),
        ).fetchone()
        if row is None:
            raise ValueError("G3_B2_MANIFEST_NOT_FOUND")
        digest, payload = row
        plan = ChunkPlan.from_json(payload, ast, document_id=document_id, ast_hash=ast_hash)
        if digest != plan.digest:
            raise ValueError("G3_B2_STORED_DIGEST_MISMATCH")
        self._verify_chunk_plan_tasks(plan)
        return plan

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

    def mark_task_completed(self, task_id: str, worker_id: str, state_version: int) -> None:
        """
        NADR-F18-03 §5.1 R3: Fencing local verificable con doble check (lease + state_version).
        Previene zombie writes de autoridades obsoletas.
        """
        now = time.time()
        cursor = self.conn.execute(
            """UPDATE chunk_tasks
               SET task_state = 'COMPLETED', 
                   lease_owner = NULL, 
                   lease_expires_at = NULL, 
                   updated_at = ?,
                   state_version = state_version + 1
               WHERE task_id = ? 
                 AND lease_owner = ? 
                 AND lease_expires_at >= ?
                 AND state_version = ?""",
            (now, task_id, worker_id, now, state_version)
        )
        self.conn.commit()
        if cursor.rowcount == 0:
            raise OptimisticLockError(
                f"Fencing interceptado: mark_task_completed para {task_id} falló. "
                f"Lease expirado, robado, o state_version desactualizado."
            )

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
        # Conexion, scheduler y otros consumidores comparten la propiedad
        # del alias; no repetir ATTACH ni hacer DETACH de un alias existente.
        ensure_fsm_database_attached(self.conn)
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
