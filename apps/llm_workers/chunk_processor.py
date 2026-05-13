import time
import logging
import sqlite3
from tenacity import (
    retry, 
    wait_exponential, 
    stop_after_attempt, 
    stop_after_delay, 
    retry_if_exception_type, 
    before_sleep_log
)

from core.ast.models import ASTNode, NodeType
from core.metrics.metrics import Metrics
from apps.llm_workers.gemini_client import GeminiClient

# SOTA: Importaciones del Motor Transaccional
from core.execution.models import ChunkExecutionEvent, ChunkPayload, ChunkLifecycle, FailureType, ProcessingStage
from core.normalization.normalizer import TextNormalizer
from core.validation.structural_validator import StructuralValidator
from infra.db.repository import DocumentRepository

logger = logging.getLogger(__name__)

class LLMTransientError(Exception):
    pass

def _is_transient(e: Exception) -> bool:
    error_str = str(e).lower()
    transient_signals = [
        "429", "rate limit", "timeout", "timed out",
        "503", "500", "unavailable", "connection",
        "disconnected"
    ]
    return any(sig in error_str for sig in transient_signals)

class ChunkProcessor:
    def __init__(self, client: GeminiClient, metrics: Metrics, db_path: str):
        self.client = client
        self.metrics = metrics
        self.db_path = db_path  # SOTA: Inyección de dependencia para conexión por hilo
        self._prompt_version = "latex_v3_strict"
        self._normalizer_version = "v1.1"
        self._validator_version = "v1.1"

    @retry(
        wait=wait_exponential(multiplier=2, min=10, max=65),
        stop=stop_after_attempt(8) | stop_after_delay(600),
        retry=retry_if_exception_type(LLMTransientError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _safe_translate(
        self, node: ASTNode, document_id: str, ast_hash: str, chunk_idx: int = 1, total_chunks: int = 1) -> ChunkExecutionEvent:
        """SOTA: Genera la llamada de red y retorna el DTO Inmutable."""
        start_net = time.perf_counter()
        
        try:
            # 1. Generación probabilística
            raw_response = self.client.translate(node, chunk_idx, total_chunks)
            latency_net = time.perf_counter() - start_net
            
            self.metrics.observe("llm_latency", latency_net)
            self.metrics.inc("llm_calls")
            logger.info("llm_call", extra={"extra_data": {"latency": round(latency_net, 3), "node_id": node.node_id}})
            
            # 2. Normalización Determinista
            normalized = TextNormalizer.normalize(raw_response)
            
            # 3. Validación de Invariantes Estructurales
            errors = StructuralValidator.validate(normalized)
            
            payload = ChunkPayload(raw_response=raw_response, normalized_response=normalized)

            if errors:
                self.metrics.inc("semantic_validation_failure")
                return ChunkExecutionEvent(
                    document_id=document_id, # SOTA: Identidad estricta
                    ast_hash=ast_hash,       # SOTA: Identidad generacional
                    node_id=node.node_id,
                    payload=payload,
                    lifecycle=ChunkLifecycle.REJECTED,
                    failure_type=FailureType.SEMANTIC_VALIDATION_FAILURE,
                    processing_stage=ProcessingStage.VALIDATION,
                    validation_errors=errors,
                    prompt_template_version=self._prompt_version,
                    normalizer_version=self._normalizer_version,
                    validator_version=self._validator_version
                )
                

            # Éxito Transaccional (Validación Estructural superada)
            self.metrics.inc("status_ok")
            return ChunkExecutionEvent(
                document_id=document_id, 
                ast_hash=ast_hash,       
                node_id=node.node_id,
                payload=payload,
                lifecycle=ChunkLifecycle.PROCESSED,
                failure_type=FailureType.NONE,
                processing_stage=ProcessingStage.VALIDATION, # <-- Mantenemos esta etapa por ahora
                prompt_template_version=self._prompt_version,
                normalizer_version=self._normalizer_version,
                validator_version=self._validator_version
            )

        except Exception as e:
            if _is_transient(e):
                raise LLMTransientError(e)
            
            # Falla catastrófica de infraestructura o de código
            self.metrics.inc("status_error")
            logger.error("terminal_error", extra={"extra_data": {"node_id": node.node_id, "error": str(e)}})
            return ChunkExecutionEvent(
                document_id=document_id, 
                ast_hash=ast_hash,       
                node_id=node.node_id,
                lifecycle=ChunkLifecycle.REJECTED,
                failure_type=FailureType.NORMALIZATION_FAILURE,
                processing_stage=ProcessingStage.NORMALIZATION,
                prompt_template_version=self._prompt_version,
                normalizer_version=self._normalizer_version,
                validator_version=self._validator_version
            )

    def process_and_commit(self, node: ASTNode, document_id: str, ast_hash: str, chunk_idx: int = 1, total_chunks: int = 1) -> str:
        """SOTA: Límite Transaccional del Worker (One Connection Per Thread)"""
        start_node = time.perf_counter()
        
        # 1. Ejecución y Validación
        if node.type in (NodeType.MACRO_CHUNK, NodeType.PARAGRAPH, NodeType.SECTION):
            event = self._safe_translate(node, document_id, ast_hash, chunk_idx, total_chunks)
            self.metrics.observe("node_latency", time.perf_counter() - start_node)
        elif node.type == NodeType.EQUATION:
            self.metrics.observe("node_latency", time.perf_counter() - start_node)
            self.metrics.inc("status_ok")
            event = ChunkExecutionEvent(
                document_id=document_id, ast_hash=ast_hash, node_id=node.node_id,
                payload=ChunkPayload(raw_response=node.latex or node.content, normalized_response=node.latex or node.content),
                lifecycle=ChunkLifecycle.PROCESSED, failure_type=FailureType.NONE,
                processing_stage=ProcessingStage.VALIDATION, prompt_template_version="bypass_equation"
            )
        else:
            event = ChunkExecutionEvent(
                document_id=document_id, ast_hash=ast_hash, node_id=node.node_id, lifecycle=ChunkLifecycle.REJECTED,
                failure_type=FailureType.SEMANTIC_VALIDATION_FAILURE, processing_stage=ProcessingStage.GENERATION
            )

        # 2. Persistencia Atómica (Conexión Pura Aislada)    
        # SOTA: Conexión limpia. Afinidad de hilo respetada. SIN check_same_thread=False
        conn = sqlite3.connect(self.db_path, timeout=15)
        try:
            repo = DocumentRepository(conn)
            repo.append_event(event)
        finally:
            conn.close()

        # 3. ACK Transaccional
        return "SUCCESS_COMMITTED" if event.lifecycle.value == "PROCESSED" else "FAILED_COMMITTED"