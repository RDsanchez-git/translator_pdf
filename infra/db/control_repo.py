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
from core.chunking.result_contract import parse_chunk_response
from infra.db.connection import ensure_fsm_database_attached

logger = logging.getLogger(__name__)

_G3_RESULT_RECEIPTS_DDL = """CREATE TABLE IF NOT EXISTS chunk_result_receipts (
    document_id TEXT NOT NULL,
    ast_hash TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    raw_response TEXT,
    response_sha256 TEXT CHECK(response_sha256 IS NULL OR length(response_sha256) = 64),
    created_at REAL NOT NULL,
    PRIMARY KEY (document_id, ast_hash, chunk_id),
    FOREIGN KEY (task_id) REFERENCES chunk_tasks(task_id),
    CHECK ((raw_response IS NULL AND response_sha256 IS NULL) OR
           (raw_response IS NOT NULL AND response_sha256 IS NOT NULL))
)"""

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
        """Reserve the WAL writer before plan reads; preserve caller-owned transactions."""
        if not self.conn.in_transaction:
            # A deferred SAVEPOINT may read a WAL snapshot, then fail with
            # SQLITE_BUSY_SNAPSHOT when a competing task claim commits.
            self.conn.execute("BEGIN IMMEDIATE")
            try:
                yield
                self.conn.commit()
            except BaseException:
                if self.conn.in_transaction:
                    self.conn.rollback()
                raise
            return

        # Nested use: the caller owns commit/rollback and the outer snapshot.
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
            "SELECT node_id, task_id FROM chunk_tasks "
            "WHERE document_id = ? AND ast_hash = ? AND worker_type <> 'ASSEMBLER'",
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

    def stage_chunk_result(
        self,
        plan: ChunkPlan,
        ast: Sequence[ASTNode],
        *,
        chunk_id: str,
        task_id: str,
        worker_id: str,
        execution_id: str,
        raw_response: Optional[str],
    ) -> bool:
        """Fence a validated provider result in queue.db; never acknowledge here.

        Returns True when newly stored; False for an exact, already staged retry.
        A PRESERVE chunk is staged with raw_response=None and needs no provider.
        """
        from hashlib import sha256
        from core.ast.models import TranslationTaskType

        if not worker_id or not execution_id:
            raise ValueError("G3_B3_2_MISSING_LEASE_IDENTITY")
        # B2 enforces persisted digest, AST linkage, and exact queue membership.
        verified = self.load_chunk_plan(plan.document_id, plan.ast_hash, ast)
        if verified != plan:
            raise ValueError("G3_B3_2_PLAN_DRIFT")
        expected_tasks = self._chunk_plan_task_ids(verified)
        if expected_tasks.get(chunk_id) != task_id:
            raise ValueError("G3_B3_2_UNKNOWN_TASK_OR_CHUNK")
        units = {u.chunk_id: u for u in verified.units}
        unit = units[chunk_id]
        if unit.chunk_type == TranslationTaskType.PRESERVE:
            if raw_response is not None:
                raise ValueError("G3_B3_2_PRESERVE_MUST_BYPASS_PROVIDER")
            response_sha256 = None
        else:
            # Fail closed: parse the whole envelope before even acquiring a lease.
            parse_chunk_response(verified, chunk_id, raw_response)
            assert isinstance(raw_response, str)
            response_sha256 = sha256(raw_response.encode("utf-8")).hexdigest()

        with self._chunk_plan_write_scope():
            # In-place schema addition for already initialized queue.db files.
            self.conn.execute(_G3_RESULT_RECEIPTS_DDL)
            row = self.conn.execute(
                "SELECT task_state, lease_owner, execution_id, lease_expires_at, state_version "
                "FROM chunk_tasks WHERE task_id=? AND document_id=? AND ast_hash=? AND node_id=? "
                "AND worker_type='LLM'",
                (task_id, verified.document_id, verified.ast_hash, chunk_id),
            ).fetchone()
            if row is None:
                raise ValueError("G3_B3_2_TASK_NOT_FOUND")
            state, owner, active_execution, expires_at, version = row
            existing = self.conn.execute(
                "SELECT task_id, execution_id, raw_response, response_sha256 "
                "FROM chunk_result_receipts WHERE document_id=? AND ast_hash=? AND chunk_id=?",
                (verified.document_id, verified.ast_hash, chunk_id),
            ).fetchone()
            if existing is not None:
                if (state == "RESULT_STAGED" and owner == worker_id
                        and active_execution == execution_id
                        and existing == (task_id, execution_id, raw_response, response_sha256)):
                    return False  # Byte-identical retry; no change to state or timestamps.
                raise ValueError("G3_B3_2_STAGED_RECEIPT_CONFLICT")

            now = time.time()
            if (state != "PROCESSING" or owner != worker_id or active_execution != execution_id
                    or expires_at is None or expires_at <= now):
                raise ValueError("G3_B3_2_LEASE_FENCE_REJECTED")

            self.conn.execute(
                "INSERT INTO chunk_result_receipts "
                "(document_id,ast_hash,chunk_id,task_id,execution_id,raw_response,response_sha256,created_at) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (verified.document_id, verified.ast_hash, chunk_id, task_id,
                 execution_id, raw_response, response_sha256, now),
            )
            updated = self.conn.execute(
                "UPDATE chunk_tasks SET task_state='RESULT_STAGED', "
                "state_version=state_version+1, updated_at=? "
                "WHERE task_id=? AND document_id=? AND ast_hash=? AND node_id=? "
                "AND task_state='PROCESSING' AND lease_owner=? AND execution_id=? "
                "AND lease_expires_at>? AND state_version=?",
                (now, task_id, verified.document_id, verified.ast_hash, chunk_id,
                 worker_id, execution_id, now, version),
            )
            if updated.rowcount != 1:
                raise ValueError("G3_B3_2_LEASE_CAS_LOST")
        return True

    def load_staged_chunk_responses(
        self, plan: ChunkPlan, ast: Sequence[ASTNode], *, allow_completed: bool = False,
    ) -> dict[str, str]:
        """Rebuild validated response map once *all* chunks are durably staged.

        Read-only. No projections or DONE states are written here.
        """
        from hashlib import sha256
        from core.ast.models import TranslationTaskType

        verified = self.load_chunk_plan(plan.document_id, plan.ast_hash, ast)
        if verified != plan:
            raise ValueError("G3_B3_2_PLAN_DRIFT")
        expected = self._chunk_plan_task_ids(verified)
        allowed_states = ({"RESULT_STAGED", "COMPLETED"}
                          if allow_completed else {"RESULT_STAGED"})
        try:
            rows = self.conn.execute(
                "SELECT r.chunk_id,r.task_id,r.execution_id,r.raw_response,r.response_sha256,"
                "t.task_state,t.execution_id "
                "FROM chunk_result_receipts AS r JOIN chunk_tasks AS t "
                "ON t.task_id=r.task_id AND t.document_id=r.document_id "
                "AND t.ast_hash=r.ast_hash AND t.node_id=r.chunk_id "
                "WHERE r.document_id=? AND r.ast_hash=?",
                (verified.document_id, verified.ast_hash),
            ).fetchall()
        except sqlite3.OperationalError as exc:
            raise ValueError("G3_B3_2_RECEIPTS_NOT_INITIALIZED") from exc
        if len(rows) != len(verified.units):
            raise ValueError("G3_B3_2_INCOMPLETE_STAGED_PLAN")
        units = {u.chunk_id: u for u in verified.units}
        responses: dict[str, str] = {}
        seen: set[str] = set()
        for chunk_id, task_id, execution_id, raw, digest, state, active_execution in rows:
            if (chunk_id in seen or chunk_id not in units or expected[chunk_id] != task_id
                    or state not in allowed_states or execution_id != active_execution):
                raise ValueError("G3_B3_2_RECEIPT_QUEUE_DRIFT")
            seen.add(chunk_id)
            if units[chunk_id].chunk_type == TranslationTaskType.PRESERVE:
                if raw is not None or digest is not None:
                    raise ValueError("G3_B3_2_INVALID_PRESERVE_RECEIPT")
            else:
                if not isinstance(raw, str) or digest != sha256(raw.encode("utf-8")).hexdigest():
                    raise ValueError("G3_B3_2_RECEIPT_CHECKSUM_MISMATCH")
                parse_chunk_response(verified, chunk_id, raw)
                responses[chunk_id] = raw
        if seen != set(units):
            raise ValueError("G3_B3_2_INCOMPLETE_STAGED_PLAN")
        return responses

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
                        AND worker_type = 'LLM'
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

    def is_g3_chunk_task(self, task_id: str) -> bool:
        """A persisted G3 manifest owns all tasks of this document generation.

        Legacy queue databases without chunk_plans must remain supported.
        """
        if self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='chunk_plans'"
        ).fetchone() is None:
            return False
        return self.conn.execute(
            "SELECT 1 FROM chunk_tasks AS t JOIN chunk_plans AS p "
            "ON p.document_id=t.document_id AND p.ast_hash=t.ast_hash "
            "WHERE t.task_id=? LIMIT 1", (task_id,),
        ).fetchone() is not None

    def recover_expired_g3_task(
        self, *, task_id: str, document_id: str, ast_hash: str, chunk_id: str,
        expected_owner: str, expected_execution_id: str, expected_expiry: float,
        expected_updated_at: float, expected_version: int,
        reconciler_owner: str, reconciler_epoch: int, stale_before: float,
    ) -> bool:
        """Recover a G3 PROCESSING lease only under exact snapshot and epoch fencing.

        Never alter durable RESULT_STAGED receipts; legacy CQRS is not a G3 ACK.
        The queue connection must have fsm_db attached by its composition root.
        A requeued inference may be retried: no exactly-once paid call is claimed.
        """
        if (not all((task_id, document_id, ast_hash, chunk_id, expected_owner,
                     expected_execution_id, reconciler_owner))
                or type(reconciler_epoch) is not int or reconciler_epoch < 1
                or type(expected_version) is not int or expected_version < 0):
            raise ValueError('G3_B4_9_INVALID_RECOVERY_IDENTITY')
        now = time.time()
        if stale_before >= now:
            raise ValueError('G3_B4_9_INVALID_STALE_CUTOFF')
        try:
            self.conn.execute('BEGIN IMMEDIATE')
            # Older SQLite queues can have a plan but no receipt table until staging.
            self.conn.execute(_G3_RESULT_RECEIPTS_DDL)
            updated = self.conn.execute(
                "UPDATE chunk_tasks SET task_state='PENDING', lease_owner=NULL, "
                "lease_expires_at=NULL, execution_id=NULL, "
                "retry_count=retry_count+1, state_version=state_version+1, updated_at=? "
                "WHERE task_id=? AND document_id=? AND ast_hash=? AND node_id=? "
                "AND worker_type='LLM' AND task_state='PROCESSING' "
                "AND lease_owner=? AND execution_id=? AND lease_expires_at=? "
                "AND updated_at=? AND state_version=? "
                "AND lease_expires_at<? AND updated_at<? "
                "AND EXISTS (SELECT 1 FROM chunk_plans AS p "
                "WHERE p.document_id=chunk_tasks.document_id AND p.ast_hash=chunk_tasks.ast_hash) "
                "AND NOT EXISTS (SELECT 1 FROM chunk_result_receipts AS r "
                "WHERE r.task_id=chunk_tasks.task_id) "
                "AND EXISTS (SELECT 1 FROM system_leases AS s "
                "WHERE s.lease_name='global_reconciler' AND s.owner_id=? "
                "AND s.lease_version=? AND s.lease_expires_at>?) "
                "AND EXISTS (SELECT 1 FROM fsm_db.document_fsm AS f "
                "WHERE f.document_id=chunk_tasks.document_id AND f.ast_hash=chunk_tasks.ast_hash "
                "AND f.current_state='PROCESSING')",
                (now, task_id, document_id, ast_hash, chunk_id,
                 expected_owner, expected_execution_id, expected_expiry,
                 expected_updated_at, expected_version, now, stale_before,
                 reconciler_owner, reconciler_epoch, now),
            )
            self.conn.commit()
            return updated.rowcount == 1
        except BaseException:
            if self.conn.in_transaction:
                self.conn.rollback()
            raise

    def mark_cqrs_reconciled(self, task_id: str, reconciliation_id: str) -> bool:
        now = time.time()
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            # No legacy completion may acknowledge or rewrite a G3 plan task.
            if self.is_g3_chunk_task(task_id):
                self.conn.rollback()
                return False
            
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
            # No legacy completion may acknowledge or rewrite a G3 plan task.
            if self.is_g3_chunk_task(task_id):
                self.conn.rollback()
                return False
            
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
                        AND t2.worker_type = 'LLM'
                        AND t2.task_state IN ('PENDING', 'RETRYABLE_ERROR')
                  )
                  OR NOT EXISTS (
                      SELECT 1 FROM chunk_tasks t3
                      WHERE t3.document_id = f.document_id
                        AND t3.ast_hash = f.ast_hash
                        AND t3.worker_type = 'LLM'
                        AND t3.task_state IN ('PENDING', 'PROCESSING', 'RETRYABLE_ERROR', 'RESULT_STAGED')
                  )
              )
            ORDER BY f.updated_at ASC
            LIMIT ?
            """,
            (sample_size,)
        )
        return cursor.fetchall()

    def find_documents_ready_for_g3_recovery(
        self, sample_size: int = 10,
    ) -> list[tuple[str, str]]:
        """Select G3 plans with no runnable tasks needing durable resolution.

        Fully staged/completed plans can recover publication/FSM; a terminal
        FAILED + staged mix must be selected so the Engine can fail the FSM.
        Preserve the legacy pending-task selector and its existing contract.
        """
        if type(sample_size) is not int or sample_size < 1:
            raise ValueError("G3_B4_3B_INVALID_SAMPLE_SIZE")
        ensure_fsm_database_attached(self.conn)
        return self.conn.execute(
            "SELECT f.document_id, f.ast_hash FROM fsm_db.document_fsm AS f "
            "JOIN chunk_plans AS p ON p.document_id=f.document_id AND p.ast_hash=f.ast_hash "
            "WHERE f.current_state='PROCESSING' "
            "AND EXISTS (SELECT 1 FROM chunk_tasks t WHERE t.document_id=f.document_id "
            "AND t.ast_hash=f.ast_hash AND t.worker_type='LLM') "
            "AND ( "
            "NOT EXISTS (SELECT 1 FROM chunk_tasks t WHERE t.document_id=f.document_id "
            "AND t.ast_hash=f.ast_hash AND t.worker_type='LLM' "
            "AND t.task_state<>'RESULT_STAGED') "
            "OR NOT EXISTS (SELECT 1 FROM chunk_tasks t WHERE t.document_id=f.document_id "
            "AND t.ast_hash=f.ast_hash AND t.worker_type='LLM' "
            "AND t.task_state<>'COMPLETED') "
            "OR (EXISTS (SELECT 1 FROM chunk_tasks t WHERE t.document_id=f.document_id "
            "AND t.ast_hash=f.ast_hash AND t.worker_type='LLM' AND t.task_state='FAILED') "
            "AND NOT EXISTS (SELECT 1 FROM chunk_tasks t WHERE t.document_id=f.document_id "
            "AND t.ast_hash=f.ast_hash AND t.worker_type='LLM' "
            "AND t.task_state IN ('PENDING','PROCESSING','RETRYABLE_ERROR'))) "
            ") ORDER BY f.updated_at ASC LIMIT ?",
            (sample_size,),
        ).fetchall()
