import time
import sqlite3
from hashlib import sha256
from typing import List
from core.execution.ports import MaterializedPlanePort, ProjectionRecord, ProjectionStatus, ProjectionState

class MaterializedPlaneRepository(MaterializedPlanePort):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_projection_status(self, document_id: str, ast_hash: str, node_id: str, required_version: int) -> ProjectionStatus:
        cursor = self.conn.execute(
            """SELECT projection_version, normalized_hash FROM valid_chunks_cache 
               WHERE document_id = ? AND ast_hash = ? AND node_id = ?""",
            (document_id, ast_hash, node_id)
        )
        row = cursor.fetchone()
        if not row:
            return ProjectionStatus(state=ProjectionState.MISSING, projection_version=None, normalized_hash=None)
            
        proj_v = row[0]
        if proj_v < required_version:
            state = ProjectionState.STALE
        else:
            state = ProjectionState.CURRENT
            
        return ProjectionStatus(state=state, projection_version=proj_v, normalized_hash=row[1])

    def upsert_projection(self, document_id: str, ast_hash: str, node_id: str, content_hash: str, 
                          normalized_text: str, normalized_hash: str, projection_v: int) -> None:
        self.conn.execute(
            """INSERT INTO valid_chunks_cache 
               (document_id, ast_hash, node_id, content_hash, normalized_response, normalized_hash, projection_version, last_updated)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?) 
               ON CONFLICT(document_id, ast_hash, node_id) 
               DO UPDATE SET normalized_response = excluded.normalized_response, 
                             normalized_hash = excluded.normalized_hash,
                             projection_version = excluded.projection_version, 
                             last_updated = excluded.last_updated
               WHERE excluded.projection_version >= valid_chunks_cache.projection_version""",
            (document_id, ast_hash, node_id, content_hash, normalized_text, normalized_hash, projection_v, time.time())
        )
        self.conn.commit()

    def get_assemblable_chunks(self, document_id: str, ast_hash: str, expected_node_ids: List[str], required_projection_v: int) -> List[ProjectionRecord]:
        if not expected_node_ids:
            return []
        placeholders = ",".join("?" * len(expected_node_ids))
        query = f"""
            SELECT node_id, normalized_response, projection_version, normalized_hash
            FROM valid_chunks_cache
            WHERE document_id = ? AND ast_hash = ? AND projection_version = ?
              AND node_id IN ({placeholders})
        """
        params = [document_id, ast_hash, required_projection_v] + expected_node_ids
        rows = self.conn.execute(query, params).fetchall()
        result = []
        for node_id, normalized_text, version, stored_hash in rows:
            # The B4/3b barrier protects the FSM transition, not a later DB edit.
            # Validate the exact bytes the compiler will consume, before handing
            # any ProjectionRecord to the assembly resolver.
            if not isinstance(normalized_text, str) or not isinstance(stored_hash, str):
                raise ValueError("G3_B4_4_INVALID_PROJECTION: " + str(node_id))
            actual_hash = sha256(normalized_text.encode("utf-8")).hexdigest()
            if stored_hash != actual_hash:
                raise ValueError("G3_B4_4_PROJECTION_HASH_DRIFT: " + str(node_id))
            result.append(ProjectionRecord(
                node_id=node_id, normalized_response=normalized_text,
                projection_version=version,
            ))
        return result
