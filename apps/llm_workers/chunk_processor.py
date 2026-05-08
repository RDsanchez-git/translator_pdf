import time
import sqlite3
import hashlib
import logging
import re
import threading
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

logger = logging.getLogger(__name__)


# =========================
# Exceptions
# =========================
class LLMTransientError(Exception):
    pass


# =========================
# Network classification
# =========================
def _is_transient(e: Exception) -> bool:
    error_str = str(e).lower()
    transient_signals = [
        "429", "rate limit", "timeout", "timed out",
        "503", "500", "unavailable", "connection"
    ]
    return any(sig in error_str for sig in transient_signals)


# =========================
# Safe fallback (Esterilización SOTA para Tectonic)
# =========================
def _safe_fallback(content: str | None) -> str:
    if not content:
        return ""
    
    # Neutralizar la barra invertida primero para evitar doble escape
    safe = content.replace("\\", "\\textbackslash ")
    
    # Escapar caracteres reservados que rompen el compilador en modo texto
    for char in ["_", "$", "%", "&", "#", "{", "}"]:
        safe = safe.replace(char, f"\\{char}")
        
    # Reemplazar tildes y acentos circunflejos con sus comandos de texto
    safe = safe.replace("~", "\\textasciitilde ").replace("^", "\\textasciicircum ")
    
    return safe


# =========================
# Minimal safe sanitization for LLM output
# ONLY escape % if not already escaped
# =========================
def _sanitize_llm_latex(text: str) -> str:
    return re.sub(r'(?<!\\)%', r'\%', text)


# =========================
# Structural validation SOTA (Explicable)
# =========================
def validate_latex(text: str) -> tuple[bool, str]:
    cleaned = re.sub(r"\\\$", "", text)
    if cleaned.count("$") % 2 != 0:
        return False, "Unbalanced $ math delimiters"
    if text.count("{") != text.count("}"):
        return False, "Unbalanced curly braces"
    if "\\begin{itemize}" in text and "\\end{itemize}" not in text:
        return False, "Unclosed itemize environment"

    # Aislar bloques matemáticos legítimos
    math_spans = re.findall(r'(?<!\\)\$.*?(?<!\\)\$', text, flags=re.DOTALL)
    temp_text = text
    for span in set(math_spans):
        temp_text = temp_text.replace(span, '')

    # Detectar operadores fuera de contexto matemático
    if re.search(r'(?<!\\)[_^]', temp_text):
        return False, "Unescaped math operator (_ or ^) outside math mode"

    return True, ""


# =========================
# Processor
# =========================

class ChunkProcessor:
    def __init__(self, client: GeminiClient, metrics: Metrics, db_path: str = "translation_cache.db"):
        self.client = client
        self.metrics = metrics
        self.db_path = db_path
        self._prompt_version = "latex_v3_strict"
        self._local = threading.local() # SOTA: Aislamiento de memoria por hilo
        self._init_db()

    def _get_conn(self):
        # Cada hilo instancia su propia conexión la primera vez que la pide
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.db_path, timeout=10)
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        return self._local.conn

    def _init_db(self):
        # La tabla se inicializa en el hilo principal una sola vez
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                hash TEXT PRIMARY KEY,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _get_cache(self, text_hash: str) -> str | None:
        cursor = self._get_conn().execute("SELECT result FROM translations WHERE hash = ?", (text_hash,))
        row = cursor.fetchone()
        return row[0] if row else None

    def _set_cache(self, text_hash: str, result: str):
        conn = self._get_conn()
        conn.execute("INSERT INTO translations (hash, result) VALUES (?, ?) ON CONFLICT(hash) DO NOTHING", (text_hash, result))
        conn.commit()

    def _compute_hash(self, text: str, chunk_idx: int, total_chunks: int) -> str:
        # FIX 1: Hash dependiente del contexto semántico
        payload = f"{self._prompt_version}::{chunk_idx}/{total_chunks}::{text}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @retry(
        wait=wait_exponential(multiplier=2, min=5, max=45),
        stop=stop_after_attempt(5) | stop_after_delay(300),
        retry=retry_if_exception_type(LLMTransientError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _safe_translate(self, text: str, chunk_idx: int = 1, total_chunks: int = 1) -> str:
        text_hash = self._compute_hash(text, chunk_idx, total_chunks)
        
        cached_result = self._get_cache(text_hash)
        if cached_result:
            self.metrics.inc("cache_hit")
            logger.info("cache_hit", extra={"extra_data": {"hash": text_hash[:8]}})
            return cached_result

        self.metrics.inc("cache_miss")
        
        try:
            # --- Intento 1
            start_net = time.perf_counter()
            # SOTA: Transmisión de índices al cliente
            result = self.client.translate(text, chunk_idx, total_chunks)
            latency_net = time.perf_counter() - start_net
            
            self.metrics.observe("llm_latency", latency_net)
            self.metrics.inc("llm_calls")
            logger.info("llm_call", extra={"extra_data": {"latency": round(latency_net, 3), "hash": text_hash[:8], "attempt": 1}})
            
            valid, reason = validate_latex(result)
            if valid:
                self._set_cache(text_hash, result)
                time.sleep(12)  # SOTA: Throttle preventivo 5 RPM
                return result

            # --- Intento 2 (Self-reflection)
            self.metrics.inc("llm_fix_attempt")
            logger.warning("latex_validation_failed", extra={"extra_data": {"hash": text_hash[:8], "reason": reason}})
            
            start_fix = time.perf_counter()
            fixed = self.client.fix_latex(result, reason)
            latency_fix = time.perf_counter() - start_fix
            
            self.metrics.observe("llm_latency", latency_fix)
            self.metrics.inc("llm_calls")
            logger.info("llm_call", extra={"extra_data": {"latency": round(latency_fix, 3), "hash": text_hash[:8], "attempt": 2}})
            
            valid_fix, _ = validate_latex(fixed)
            if valid_fix:
                self._set_cache(text_hash, fixed)
                time.sleep(12)  # SOTA: Throttle preventivo 5 RPM
                return fixed

            # --- Fallo total
            self.metrics.inc("llm_fix_failed")
            time.sleep(12)
            return ""

        except Exception as e:
            if _is_transient(e):
                raise LLMTransientError(e)
            raise e

    def process(self, node: ASTNode, chunk_idx: int = 1, total_chunks: int = 1) -> ASTNode:
        start_node = time.perf_counter()
        try:
            # SOTA: Enrutamiento semántico por Enum
            if node.type in (NodeType.MACRO_CHUNK, NodeType.PARAGRAPH, NodeType.SECTION):
                content = node.content or ""
                
                translated = self._safe_translate(content, chunk_idx, total_chunks)
                if translated:
                    translated = translated.strip("\n")
                    translated = _sanitize_llm_latex(translated)
                
                latency_total = time.perf_counter() - start_node
                self.metrics.observe("node_latency", latency_total)
                
                if not translated:
                    self.metrics.inc("status_fallback_empty")
                    return node.model_copy(update={"latex": _safe_fallback(content), "status": "fallback_empty"})
                    
                self.metrics.inc("status_ok")
                return node.model_copy(update={"latex": translated, "status": "ok"})
                
            elif node.type == NodeType.EQUATION:
                latency_total = time.perf_counter() - start_node
                self.metrics.observe("node_latency", latency_total)
                self.metrics.inc("status_ok")
                return node.model_copy(update={"latex": node.latex or node.content, "status": "ok"})
                
        except Exception as e:
            self.metrics.inc("status_error")
            logger.error("terminal_error", extra={"extra_data": {"node_id": node.node_id, "error": str(e)}})
            return node.model_copy(update={"latex": _safe_fallback(node.content), "status": "error"})
            
        return node