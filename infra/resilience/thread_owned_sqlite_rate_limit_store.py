"""Thread-confined persistent quota store for the threaded G3 Engine.

The existing SQLiteRateLimitStore and its sqlite3.Connection are created, used,
and closed exclusively in the same dedicated executor thread.  The public
RateLimitStore load/save protocol stays synchronous and unchanged.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from core.resilience.rate_limit_store import BucketState
from infra.db.connection import get_connection
from infra.resilience.sqlite_rate_limit_store import SQLiteRateLimitStore


class ThreadOwnedSQLiteRateLimitStore:
    def __init__(self, db_path: str, *, timeout: int = 30) -> None:
        self._gate = Lock()
        self._closed = False
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="quota-sqlite")
        try:
            self._executor.submit(self._open_in_owner, db_path, timeout).result()
        except BaseException:
            self._executor.shutdown(wait=True)
            raise

    def _open_in_owner(self, db_path: str, timeout: int) -> None:
        conn = get_connection(db_path, timeout=timeout)
        try:
            store = SQLiteRateLimitStore(conn)
        except BaseException:
            conn.close()
            raise
        self._conn = conn
        self._store = store

    def _submit(self, method, *args):
        with self._gate:
            if self._closed:
                raise RuntimeError("G3_B4_7B_RATE_LIMIT_STORE_CLOSED")
            future = self._executor.submit(method, *args)
        return future.result()

    def _load_in_owner(self, bucket_id: str):
        return self._store.load(bucket_id)

    def _save_in_owner(self, bucket_id: str, state: BucketState) -> None:
        self._store.save(bucket_id, state)

    def load(self, bucket_id: str):
        return self._submit(self._load_in_owner, bucket_id)

    def save(self, bucket_id: str, state: BucketState) -> None:
        self._submit(self._save_in_owner, bucket_id, state)

    def close(self) -> None:
        """Idempotently close the connection on its owner thread, then join it."""
        with self._gate:
            if self._closed:
                return
            self._closed = True
            future = self._executor.submit(self._close_in_owner)
        try:
            future.result()
        finally:
            self._executor.shutdown(wait=True)

    def _close_in_owner(self) -> None:
        self._conn.close()
