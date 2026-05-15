import time
import sqlite3

class SystemPlaneRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def acquire_leadership(self, lease_name: str, node_id: str, ttl_sec: int) -> int:
        """SOTA: Retorna el Epoch (lease_version) o 0 si falla."""
        now = time.time()
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            cursor = self.conn.execute(
                """UPDATE system_leases
                   SET owner_id = ?, lease_expires_at = ?, updated_at = ?, lease_version = lease_version + 1
                   WHERE lease_name = ? AND (owner_id IS NULL OR lease_expires_at < ?)
                   RETURNING lease_version""",
                (node_id, now + ttl_sec, now, lease_name, now)
            )
            row = cursor.fetchone()
            self.conn.commit()
            return row[0] if row else 0
        except Exception as e:
            self.conn.rollback()
            raise e

    def renew_leadership(self, lease_name: str, node_id: str, ttl_sec: int) -> bool:
        """SOTA: Fencing temporal estricto en la renovación global."""
        now = time.time()
        cursor = self.conn.execute(
            """UPDATE system_leases
               SET lease_expires_at = ?, updated_at = ?
               WHERE lease_name = ? AND owner_id = ? AND lease_expires_at >= ?""",
            (now + ttl_sec, now, lease_name, node_id, now)
        )
        self.conn.commit()
        return cursor.rowcount > 0
        
    def release_leadership(self, lease_name: str, node_id: str) -> None:
        now = time.time()
        self.conn.execute(
            """UPDATE system_leases
               SET owner_id = NULL, lease_expires_at = NULL, updated_at = ?
               WHERE lease_name = ? AND owner_id = ?""",
            (now, lease_name, node_id)
        )
        self.conn.commit()