import time
import sqlite3
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
                             last_updated = excluded.last_updated""",
            (document_id, ast_hash, node_id, content_hash, normalized_text, normalized_hash, projection_v, time.time())
        )
        self.conn.commit()

    def get_assemblable_chunks(self, document_id: str, ast_hash: str, expected_node_ids: List[str], required_projection_v: int) -> List[ProjectionRecord]:
        placeholders = ",".join("?" * len(expected_node_ids))
        query = f"""
            SELECT node_id, normalized_response, projection_version 
            FROM valid_chunks_cache 
            WHERE document_id = ? AND ast_hash = ? AND projection_version = ?
              AND node_id IN ({placeholders})
        """
        params = [document_id, ast_hash, required_projection_v] + expected_node_ids
        cursor = self.conn.execute(query, params)
        
        # SOTA: Emite DTOs. El orquestador ya no manipula tuplas.
        return [
            ProjectionRecord(node_id=row[0], normalized_response=row[1], projection_version=row[2])
            for row in cursor.fetchall()
        ]