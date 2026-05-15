import time
import hashlib
import sqlite3
import logging
from tenacity import (
    retry, wait_exponential, stop_after_attempt, 
    stop_after_delay, retry_if_exception_type, before_sleep_log
)
from core.execution.ports import ControlPlanePort, EventPlanePort, MaterializedPlanePort
from core.ast.models import ASTNode, NodeType
from core.metrics.metrics import Metrics
from apps.llm_workers.gemini_client import GeminiClient
from core.normalization.normalizer import TextNormalizer

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
    def __init__(self, client: GeminiClient, metrics: Metrics, 
                 control_port: ControlPlanePort, 
                 event_port: EventPlanePort, 
                 mat_port: MaterializedPlanePort):
        
        self.client = client
        self.metrics = metrics
        
        # SOTA: Inyección estricta de Protocolos. Cero acoplamiento a I/O.
        self.control = control_port
        self.event = event_port
        self.materialized = mat_port
        
        self.prompt_v = "v3_latex_optimized"
        self.model_v = "gemini-2.5-flash" 
        self.projection_v = 1 
        
    # (El método process_and_commit pierde todo el bloque de self._get_connection, 
    # y llama directamente a self.event.get_replay() y self.materialized.upsert_projection() 
    # recibiendo los nuevos DTOs Tipados)

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
        # Importaciones locales de Enums si no están en la cabecera
        from core.execution.ports import ProcessingOutcome, ProjectionState, EventLifecycle
        
        if node.type not in (NodeType.MACRO_CHUNK, NodeType.PARAGRAPH, NodeType.SECTION, NodeType.EQUATION):
            return ProcessingOutcome.SKIPPED_UNSUPPORTED.value

        start_node = time.perf_counter()
        content = node.content or ""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # 1. Validación de Proyección Existente (Usa el Puerto, no SQL)
        proj_status = self.materialized.get_projection_status(document_id, ast_hash, node.node_id, self.projection_v)
        if proj_status.state == ProjectionState.CURRENT:
            return ProcessingOutcome.ALREADY_CURRENT.value

        raw_response = None
        
        if node.type == NodeType.EQUATION:
            raw_response = node.latex or node.content
        else:
            # 2. Replay Económico Fuerte
            replay = self.event.get_replay(content_hash, self.prompt_v, self.model_v)
            
            if replay:
                # SOTA: Extraemos el string del DTO
                raw_response = replay.raw_response
                logger.info("ECONOMIC_REPLAY_HIT", extra={"extra_data": {"exec_id": execution_id}})
            else:
                # 3. Llamada de Red (Costo) y WAL Append
                raw_response = self._pure_llm_call(node, chunk_idx, total_chunks)
                
                # SOTA: Añadido el EventLifecycle faltante
                self.event.append_wal(
                    execution_id, document_id, node.node_id, content_hash, 
                    raw_response, self.prompt_v, self.model_v, self.projection_v, EventLifecycle.GENERATED
                )

        # 4. Normalización y Materialización
        normalized = TextNormalizer.normalize(raw_response) if node.type != NodeType.EQUATION else raw_response
        normalized_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        
        self.materialized.upsert_projection(
            document_id, ast_hash, node.node_id, content_hash, 
            normalized, normalized_hash, self.projection_v
        )
        
        self.metrics.observe("node_latency", time.perf_counter() - start_node)
        return ProcessingOutcome.MATERIALIZED.value