import json
from core.execution.models import ChunkExecutionEvent
import logging

logger = logging.getLogger(__name__)

class DocumentRepository:
    def __init__(self, db_connection):
        self.db = db_connection
        self.db.execute("PRAGMA foreign_keys = ON;")

    def append_event(self, event: ChunkExecutionEvent) -> None:
        """SOTA: Persistencia atómica. Excepciones se propagan al hilo llamador."""
        with self.db: # Auto commit/rollback
            # SOTA: Persistencia idempotente con observabilidad de red
            cursor = self.db.execute(
                """INSERT OR IGNORE INTO chunk_events_log 
                   (event_id, document_id, ast_hash, node_id, content_hash, raw_response, normalized_response, 
                    lifecycle, failure_type, processing_stage, validation_errors, prompt_hash, 
                    prompt_template_version, normalizer_version, validator_version, timestamp) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.event_id, event.document_id, event.ast_hash, event.node_id, event.content_hash, 
                    event.payload.raw_response, event.payload.normalized_response, 
                    event.lifecycle.value, event.failure_type.value, event.processing_stage.value,
                    json.dumps([e.__dict__ for e in event.validation_errors]),
                    event.prompt_hash, event.prompt_template_version, event.normalizer_version, 
                    event.validator_version, event.timestamp
                )
            )
            
            # Alerta telemétrica pasiva (No aborta la transacción)
            if cursor.rowcount == 0:
                logger.warning("IDEMPOTENT_REPLAY_DETECTED", extra={
                    "extra_data": {
                        "document_id": event.document_id, 
                        "ast_hash": event.ast_hash,
                        "node_id": event.node_id, 
                        "content_hash": event.content_hash  # SOTA: La verdadera identidad deduplicada
                    }
                })
            
            # SOTA: La verdadera invariante es si es ensamblable, no si "terminó"
            if event.is_assemblable:
                self.db.execute(
                    """INSERT INTO valid_chunks_cache 
                       (document_id, ast_hash, node_id, content_hash, normalized_response, last_updated) 
                       VALUES (?, ?, ?, ?, ?, ?)
                       ON CONFLICT(document_id, ast_hash, node_id) DO UPDATE SET 
                           content_hash=excluded.content_hash,
                           normalized_response=excluded.normalized_response,
                           last_updated=excluded.last_updated
                       WHERE excluded.last_updated > valid_chunks_cache.last_updated""",
                    (event.document_id, event.ast_hash, event.node_id, event.content_hash, event.payload.normalized_response, event.timestamp)
                )

    def get_assemblable_chunks(self, document_id: str, ast_hash: str, ordered_node_ids: list[str]) -> list[tuple[str, str]]:
        if not ordered_node_ids:
            return []
        
        placeholders = ','.join('?' for _ in ordered_node_ids)
        order_clauses = " ".join([f"WHEN '{n_id}' THEN {i}" for i, n_id in enumerate(ordered_node_ids)])
        
        # SOTA: Solo extrae fragmentos de ESTE documento y ESTA generación de AST
        query = f"""
            SELECT node_id, normalized_response 
            FROM valid_chunks_cache 
            WHERE document_id = ? AND ast_hash = ? AND node_id IN ({placeholders})
            ORDER BY CASE node_id {order_clauses} END
        """
        params = [document_id, ast_hash] + ordered_node_ids
        cursor = self.db.execute(query, params)
        return [(row[0], row[1]) for row in cursor.fetchall()]