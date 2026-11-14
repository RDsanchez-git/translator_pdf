"""G5/2: SQLite authority for physical ASSEMBLER; no new lease database.

Queue owns the lease; fsm_db is attached to the same SQLite connection.
The file publication is fenced while the SQLite writer lock is held. A crash
between os.replace and COMMIT can leave a complete PDF requiring regeneration,
not a claim of atomic commit across SQLite and the filesystem.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import sqlite3
import time
import uuid

_PHASES = ('ASSEMBLING', 'READY_FOR_COMPILATION', 'COMPILING')


@dataclass(frozen=True)
class AssemblyLease:
    task_id: str
    document_id: str
    ast_hash: str
    owner: str
    execution_id: str


class AssemblyLeaseRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        # An attached physical FSM database is required; never silently create it.
        aliases = {row[1] for row in conn.execute('PRAGMA database_list')}
        if 'fsm_db' not in aliases:
            raise RuntimeError('G5_ASSEMBLER_FSM_DATABASE_NOT_ATTACHED')

    @staticmethod
    def task_id(document_id: str, ast_hash: str) -> str:
        digest = hashlib.sha256(f'{document_id}:{ast_hash}:ROOT_ASSEMBLY'.encode()).hexdigest()
        return 'task_' + digest[:24]

    def claim(self, document_id: str, ast_hash: str, owner: str, ttl_sec: int = 180) -> AssemblyLease | None:
        if not document_id or not ast_hash or not owner or ttl_sec < 30:
            raise ValueError('G5_ASSEMBLER_INVALID_CLAIM')
        now = time.time()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            fsm = self.conn.execute(
                'SELECT current_state,state_version FROM fsm_db.document_fsm WHERE document_id=? AND ast_hash=?',
                (document_id, ast_hash),
            ).fetchone()
            if fsm is None or fsm[0] != 'READY_FOR_ASSEMBLY':
                self.conn.rollback()
                return None
            # Existing historical task IDs, if any, are preserved.
            self.conn.execute(
                "INSERT OR IGNORE INTO chunk_tasks "
                "(task_id,document_id,ast_hash,node_id,task_state,worker_type,created_at,updated_at,state_version) "
                "VALUES (?,?,?,'ROOT_ASSEMBLY','PENDING','ASSEMBLER',?,?,0)",
                (self.task_id(document_id, ast_hash), document_id, ast_hash, now, now),
            )
            task = self.conn.execute(
                "SELECT task_id,task_state,lease_owner FROM chunk_tasks "
                "WHERE document_id=? AND ast_hash=? AND node_id='ROOT_ASSEMBLY' AND worker_type='ASSEMBLER'",
                (document_id, ast_hash),
            ).fetchone()
            if task is None or task[1] not in ('PENDING', 'RETRYABLE_ERROR') or task[2] is not None:
                self.conn.rollback()
                return None
            execution_id = 'assembly_' + uuid.uuid4().hex
            q = self.conn.execute(
                "UPDATE chunk_tasks SET task_state='PROCESSING',lease_owner=?,execution_id=?,"
                "lease_expires_at=?,updated_at=?,state_version=state_version+1 "
                "WHERE task_id=? AND worker_type='ASSEMBLER' "
                "AND task_state IN ('PENDING','RETRYABLE_ERROR') AND lease_owner IS NULL",
                (owner, execution_id, now + ttl_sec, now, task[0]),
            )
            f = self.conn.execute(
                "UPDATE fsm_db.document_fsm SET current_state='ASSEMBLING',state_version=state_version+1,"
                "entered_state_at=?,updated_at=? WHERE document_id=? AND ast_hash=? "
                "AND current_state='READY_FOR_ASSEMBLY' AND state_version=? AND is_terminal=0",
                (now, now, document_id, ast_hash, fsm[1]),
            )
            if q.rowcount != 1 or f.rowcount != 1:
                raise RuntimeError('G5_ASSEMBLER_CLAIM_CAS_CONFLICT')
            self.conn.commit()
            return AssemblyLease(task[0], document_id, ast_hash, owner, execution_id)
        except BaseException:
            if self.conn.in_transaction:
                self.conn.rollback()
            raise

    def _has_authority(self, lease: AssemblyLease, now: float, phases: tuple[str, ...] = _PHASES) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM chunk_tasks AS t JOIN fsm_db.document_fsm AS f "
            "ON f.document_id=t.document_id AND f.ast_hash=t.ast_hash "
            "WHERE t.task_id=? AND t.document_id=? AND t.ast_hash=? AND t.node_id='ROOT_ASSEMBLY' "
            "AND t.worker_type='ASSEMBLER' AND t.task_state='PROCESSING' "
            "AND t.lease_owner=? AND t.execution_id=? AND t.lease_expires_at>? "
            "AND f.current_state IN (" + ','.join('?' for _ in phases) + ") AND f.is_terminal=0",
            (lease.task_id, lease.document_id, lease.ast_hash, lease.owner, lease.execution_id, now, *phases),
        ).fetchone()
        return row is not None

    def renew(self, lease: AssemblyLease, ttl_sec: int = 180) -> bool:
        if ttl_sec < 30:
            raise ValueError('G5_ASSEMBLER_TTL_TOO_SHORT')
        now = time.time()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            if not self._has_authority(lease, now):
                self.conn.rollback()
                return False
            cur = self.conn.execute(
                "UPDATE chunk_tasks SET lease_expires_at=?,updated_at=? "
                "WHERE task_id=? AND task_state='PROCESSING' AND worker_type='ASSEMBLER' "
                "AND lease_owner=? AND execution_id=? AND lease_expires_at>?",
                (now + ttl_sec, now, lease.task_id, lease.owner, lease.execution_id, now),
            )
            self.conn.commit()
            return cur.rowcount == 1
        except BaseException:
            if self.conn.in_transaction:
                self.conn.rollback()
            raise

    def advance(self, lease: AssemblyLease, old_state: str, new_state: str) -> bool:
        if (old_state, new_state) not in (
            ('ASSEMBLING', 'READY_FOR_COMPILATION'),
            ('READY_FOR_COMPILATION', 'COMPILING'),
        ):
            raise ValueError('G5_ASSEMBLER_ILLEGAL_PHASE_TRANSITION')
        now = time.time()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            if not self._has_authority(lease, now, (old_state,)):
                self.conn.rollback()
                return False
            updated = self.conn.execute(
                "UPDATE fsm_db.document_fsm SET current_state=?, state_version=state_version+1,"
                "entered_state_at=?,updated_at=? WHERE document_id=? AND ast_hash=? "
                "AND current_state=? AND is_terminal=0",
                (new_state, now, now, lease.document_id, lease.ast_hash, old_state),
            )
            self.conn.commit()
            return updated.rowcount == 1
        except BaseException:
            if self.conn.in_transaction:
                self.conn.rollback()
            raise

    def publish(self, lease: AssemblyLease, staged_pdf: str, final_pdf: str) -> bool:
        """Fence file promotion + FSM completion under SQLite writer lock."""
        src = Path(staged_pdf)
        dst = Path(final_pdf)
        # Stage and final must be siblings; never accept symlinks or another directory.
        if (src.parent.resolve() != dst.parent.resolve() or src.is_symlink()
                or dst.is_symlink() or not src.is_file()
                or dst.name != f'translated_{lease.document_id}.pdf'):
            raise ValueError('G5_ASSEMBLER_INVALID_PDF_PATH')
        with src.open('rb') as stream:
            if stream.read(5) != b'%PDF-' or src.stat().st_size < 8:
                raise ValueError('G5_ASSEMBLER_INVALID_STAGED_PDF')
        now = time.time()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            if not self._has_authority(lease, now, ('COMPILING',)):
                self.conn.rollback()
                return False
            f = self.conn.execute(
                "UPDATE fsm_db.document_fsm SET current_state='COMPLETED',is_terminal=1,"
                "state_version=state_version+1,entered_state_at=?,updated_at=? "
                "WHERE document_id=? AND ast_hash=? AND current_state='COMPILING' AND is_terminal=0",
                (now, now, lease.document_id, lease.ast_hash),
            )
            q = self.conn.execute(
                "UPDATE chunk_tasks SET task_state='COMPLETED',lease_owner=NULL,lease_expires_at=NULL,"
                "updated_at=?,state_version=state_version+1 "
                "WHERE task_id=? AND task_state='PROCESSING' AND lease_owner=? AND execution_id=?",
                (now, lease.task_id, lease.owner, lease.execution_id),
            )
            if f.rowcount != 1 or q.rowcount != 1:
                raise RuntimeError('G5_ASSEMBLER_PUBLISH_CAS_CONFLICT')
            # This atomic rename is only visible for the authoritative execution.
            # If the process dies before COMMIT, recovery may regenerate the PDF.
            os.replace(src, dst)
            self.conn.commit()
            return True
        except BaseException:
            if self.conn.in_transaction:
                self.conn.rollback()
            raise

    def fail_authorized(self, lease: AssemblyLease, reason: str) -> bool:
        now = time.time()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            if not self._has_authority(lease, now):
                self.conn.rollback()
                return False
            f = self.conn.execute(
                "UPDATE fsm_db.document_fsm SET current_state='FAILED_RETRYABLE',state_version=state_version+1,"
                "entered_state_at=?,updated_at=?,failure_reason=? "
                "WHERE document_id=? AND ast_hash=? AND current_state IN ('ASSEMBLING','READY_FOR_COMPILATION','COMPILING') "
                "AND is_terminal=0",
                (now, now, reason[:250], lease.document_id, lease.ast_hash),
            )
            q = self.conn.execute(
                "UPDATE chunk_tasks SET task_state='FAILED',retry_count=retry_count+1,"
                "lease_owner=NULL,lease_expires_at=NULL,error_log=?,updated_at=?,state_version=state_version+1 "
                "WHERE task_id=? AND task_state='PROCESSING' AND lease_owner=? AND execution_id=?",
                (reason[:250], now, lease.task_id, lease.owner, lease.execution_id),
            )
            if f.rowcount != 1 or q.rowcount != 1:
                raise RuntimeError('G5_ASSEMBLER_FAILURE_CAS_CONFLICT')
            self.conn.commit()
            return True
        except BaseException:
            if self.conn.in_transaction:
                self.conn.rollback()
            raise

    def recover_expired(self, *, task_id: str, document_id: str, ast_hash: str,
                        expected_owner: str, expected_execution_id: str,
                        expected_expiry: float, expected_updated_at: float,
                        expected_version: int, reconciler_owner: str,
                        reconciler_epoch: int, stale_before: float) -> str | None:
        """Requeue only a truly expired assembler under live leader/epoch and CAS.

        Returns REQUEUED, QUARANTINED or None. Never acts on terminal FSMs.
        """
        now = time.time()
        if (not all((task_id, document_id, ast_hash, expected_owner, expected_execution_id,
                     reconciler_owner)) or type(reconciler_epoch) is not int or reconciler_epoch < 1
                or type(expected_version) is not int or expected_version < 0
                or stale_before >= now):
            raise ValueError('G5_ASSEMBLER_INVALID_RECOVERY_IDENTITY')
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            leader = self.conn.execute(
                "SELECT 1 FROM system_leases WHERE lease_name='global_reconciler' "
                "AND owner_id=? AND lease_version=? AND lease_expires_at>?",
                (reconciler_owner, reconciler_epoch, now),
            ).fetchone()
            if not leader:
                self.conn.rollback()
                return None
            task = self.conn.execute(
                "SELECT retry_count,max_retries FROM chunk_tasks "
                "WHERE task_id=? AND document_id=? AND ast_hash=? AND node_id='ROOT_ASSEMBLY' "
                "AND worker_type='ASSEMBLER' AND task_state='PROCESSING' "
                "AND lease_owner=? AND execution_id=? AND lease_expires_at=? "
                "AND updated_at=? AND state_version=? AND lease_expires_at<? AND updated_at<?",
                (task_id, document_id, ast_hash, expected_owner, expected_execution_id,
                 expected_expiry, expected_updated_at, expected_version, stale_before, stale_before),
            ).fetchone()
            fsm = self.conn.execute(
                "SELECT current_state,state_version FROM fsm_db.document_fsm WHERE document_id=? AND ast_hash=? "
                "AND current_state IN ('ASSEMBLING','READY_FOR_COMPILATION','COMPILING') AND is_terminal=0",
                (document_id, ast_hash),
            ).fetchone()
            if not task or not fsm:
                self.conn.rollback()
                return None
            exhausted = task[0] + 1 >= task[1]
            new_task_state = 'FAILED' if exhausted else 'PENDING'
            new_fsm_state = 'FAILED_RETRYABLE' if exhausted else 'READY_FOR_ASSEMBLY'
            q = self.conn.execute(
                "UPDATE chunk_tasks SET task_state=?,lease_owner=NULL,execution_id=NULL,"
                "lease_expires_at=NULL,retry_count=retry_count+1,updated_at=?,state_version=state_version+1 "
                "WHERE task_id=? AND task_state='PROCESSING' AND lease_owner=? AND execution_id=? "
                "AND state_version=? AND lease_expires_at=? AND updated_at=?",
                (new_task_state, now, task_id, expected_owner, expected_execution_id,
                 expected_version, expected_expiry, expected_updated_at),
            )
            f = self.conn.execute(
                "UPDATE fsm_db.document_fsm SET current_state=?,state_version=state_version+1,"
                "entered_state_at=?,updated_at=?,failure_reason=? "
                "WHERE document_id=? AND ast_hash=? AND current_state=? AND state_version=? AND is_terminal=0",
                (new_fsm_state, now, now,
                 'G5_ASSEMBLER_RETRY_BUDGET_EXHAUSTED' if exhausted else None,
                 document_id, ast_hash, fsm[0], fsm[1]),
            )
            if q.rowcount != 1 or f.rowcount != 1:
                raise RuntimeError('G5_ASSEMBLER_RECOVERY_CAS_CONFLICT')
            self.conn.commit()
            return 'QUARANTINED' if exhausted else 'REQUEUED'
        except BaseException:
            if self.conn.in_transaction:
                self.conn.rollback()
            raise
