import time
import hashlib
import sqlite3
import logging
from tenacity import (
    retry, wait_exponential, stop_after_attempt, 
    stop_after_delay, retry_if_exception_type, before_sleep_log
)

from core.ast.models import ASTNode, NodeType
from core.metrics.metrics import Metrics
from apps.llm_workers.gemini_client import GeminiClient
from core.normalization.normalizer import TextNormalizer
from infra.db.event_repo import EventPlaneRepository
from infra.db.materialized_repo import MaterializedPlaneRepository

logger = logging.getLogger(__name__)

class LLMTransientError(Exception):
    pass

def _is_transient(e: Exception) -> bool:
    error_str = str(e).lower()
    transient_signals = [
        "429", "rate limit", "timeout", "timed out",
        "503", "500", "unavailable", "connection", "disconnected"
    ]
    return any(sig in error_str for sig in transient_signals)

class ChunkProcessor:
    def __init__(self, client: GeminiClient, metrics: Metrics, control_db_path: str, event_db_path: str, mat_db_path: str):
        self.client = client
        self.metrics = metrics
        # SOTA: Tres rutas físicas para TPS
        self.control_db_path = control_db_path
        self.event_db_path = event_db_path
        self.mat_db_path = mat_db_path
        
        self.prompt_v = "v3_latex_optimized"
        self.model_v = "gemini-2.5-flash" # Corrección aplicada
        self.projection_v = 1 

    def _get_connection(self, path: str) -> sqlite3.Connection:
        conn = sqlite3.connect(path, timeout=15)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    @retry(
        wait=wait_exponential(multiplier=2, min=10, max=65),
        stop=stop_after_attempt(8) | stop_after_delay(600),
        retry=retry_if_exception_type(LLMTransientError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _pure_llm_call(self, node: ASTNode, chunk_idx: int, total_chunks: int) -> str:
        start_net = time.perf_counter()
        try:
            raw_response = self.client.translate(node, chunk_idx, total_chunks)
            latency_net = time.perf_counter() - start_net
            self.metrics.observe("llm_latency", latency_net)
            self.metrics.inc("llm_calls")
            return raw_response
        except Exception as e:
            if _is_transient(e):
                raise LLMTransientError(e)
            logger.error("terminal_error", extra={"extra_data": {"node_id": node.node_id, "error": str(e)}})
            raise e

    def process_and_commit(self, node: ASTNode, document_id: str, ast_hash: str, execution_id: str, chunk_idx: int = 1, total_chunks: int = 1) -> str:
        if node.type not in (NodeType.MACRO_CHUNK, NodeType.PARAGRAPH, NodeType.SECTION, NodeType.EQUATION):
            return "SKIPPED_UNSUPPORTED_NODE"

        start_node = time.perf_counter()
        content = node.content or ""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Abrimos conexiones con afinidad estricta al hilo actual
        conn_evt = self._get_connection(self.event_db_path)
        conn_mat = self._get_connection(self.mat_db_path)
        
        try:
            event_repo = EventPlaneRepository(conn_evt)
            mat_repo = MaterializedPlaneRepository(conn_mat)

            # 1. Validación de Proyección Existente
            current_proj = mat_repo.get_projection(document_id, ast_hash, node.node_id)
            if current_proj and current_proj['projection_version'] == self.projection_v:
                return "ALREADY_MATERIALIZED"

            if node.type == NodeType.EQUATION:
                raw_response = node.latex or node.content
            else:
                # 2. Replay Económico Fuerte
                raw_response = event_repo.get_replay(content_hash, self.prompt_v, self.model_v)
                
                if not raw_response:
                    # 3. Llamada de Red (Costo) y WAL Append
                    raw_response = self._pure_llm_call(node, chunk_idx, total_chunks)
                    event_repo.append_wal(
                        execution_id, document_id, node.node_id, content_hash, 
                        raw_response, self.prompt_v, self.model_v, self.projection_v
                    )

            # 4. Normalización y Materialización
            normalized = TextNormalizer.normalize(raw_response) if node.type != NodeType.EQUATION else raw_response
            normalized_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
            
            mat_repo.upsert_projection(
                document_id, ast_hash, node.node_id, content_hash, 
                normalized, normalized_hash, self.projection_v
            )
            
            self.metrics.observe("node_latency", time.perf_counter() - start_node)
            return "MATERIALIZED"
            
        finally:
            conn_evt.close()
            conn_mat.close()