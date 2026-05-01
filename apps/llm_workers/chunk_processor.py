import os
import json
import hashlib
import logging
import re
from tenacity import (
    retry, 
    wait_exponential, 
    stop_after_attempt, 
    stop_after_delay, 
    retry_if_exception_type, 
    before_sleep_log
)

from core.ast.models import ASTNode
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
# Safe fallback (plain text → safe LaTeX)
# =========================
def _safe_fallback(text: str | None) -> str:
    if not text:
        return ""

    return (
        text
        .replace("\\", "\\textbackslash ")
        .replace("_", "\\_")
        .replace("%", "\\%")
    )


# =========================
# Minimal safe sanitization for LLM output
# ONLY escape % if not already escaped
# =========================
def _sanitize_llm_latex(text: str) -> str:
    return re.sub(r'(?<!\\)%', r'\%', text)


# =========================
# Structural validation (cheap but effective)
# =========================
def _is_latex_structurally_suspicious(text: str) -> bool:
    # --- Braces check (ignore escaped \{ \})
    open_braces = len(re.findall(r'(?<!\\)\{', text))
    close_braces = len(re.findall(r'(?<!\\)\}', text))
    if open_braces != close_braces:
        return True

    # --- Inline math check (ignore \$)
    dollars = len(re.findall(r'(?<!\\)\$', text))
    if dollars % 2 != 0:
        return True

    # --- begin/end balance (cheap heuristic)
    begin_count = text.count(r'\begin')
    end_count = text.count(r'\end')
    if begin_count != end_count:
        return True

    # --- Unescaped math operators in plain text check (Robust literal stripping)
    math_spans = re.findall(r'(?<!\\)\$.*?(?<!\\)\$', text, flags=re.DOTALL)
    temp_text = text
    # SOTA: Optimización iterando sobre un set para evitar múltiples pasadas del mismo span
    for span in set(math_spans):
        temp_text = temp_text.replace(span, '')

    if re.search(r'(?<!\\)[_^]', temp_text):
        return True

    # --- WAF: Fake macros, literal backslashes and morphological anomalies
    if re.search(r'[a-zA-Z]:\\[a-zA-Z]', text):
        return True
    if re.search(r'\\(?![%$\\])[ \t.,;:]', text):
        return True

    macros = re.findall(r'\\([A-Za-z]+)', text)
    for m in macros:
        # Exención explícita para macros estándar con mayúsculas intercaladas
        KNOWN_CAMEL_MACROS = {"LaTeX", "TeX", "XeLaTeX", "LuaTeX", "BibTeX"}

        if m in KNOWN_CAMEL_MACROS:
            continue
            
        # Caso 1: macro absurdamente largo
        if len(m) > 20:
            return True
            
        # Caso 2: macro probablemente concatenado (camelCase raro)
        if re.search(r'[a-z][A-Z]', m):
            return True

    return False


# =========================
# Processor
# =========================
class ChunkProcessor:
    def __init__(self, client: GeminiClient, cache_file: str = "translation_cache.json"):
        self.client = client
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self._unsaved_entries = 0
        self._prompt_version = "latex_v1"

    def _load_cache(self) -> dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Caché corrupta. Iniciando caché vacía.")
        return {}

    def _save_cache(self):
        tmp_path = f"{self.cache_file}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.cache_file)
        self._unsaved_entries = 0

    def flush_cache(self):
        if self._unsaved_entries > 0:
            self._save_cache()

    def _compute_hash(self, text: str) -> str:
        payload = f"{self._prompt_version}::{text}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # SOTA: Circuit breaker temporal. Detiene si supera 3 intentos O si el tiempo total excede 60s
        stop=stop_after_attempt(3) | stop_after_delay(60),
        retry=retry_if_exception_type(LLMTransientError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _safe_translate(self, text: str) -> str:
        text_hash = self._compute_hash(text)
        
        if text_hash in self.cache:
            logger.info(f"Cache HIT (hash: {text_hash[:8]})")
            return self.cache[text_hash]

        try:
            result = self.client.translate(text)
            self.cache[text_hash] = result
            self._unsaved_entries += 1
            
            if self._unsaved_entries >= 10:
                self._save_cache()
                
            return result
        except Exception as e:
            if _is_transient(e):
                raise LLMTransientError(e)
            raise e 

    def process(self, node: ASTNode) -> ASTNode:
        try:
            if node.type in ("text_block", "section"):
                content = node.content or ""
                
                translated = self._safe_translate(content).strip()
                translated = _sanitize_llm_latex(translated)
                
                if not translated:
                    logger.warning(f"Traducción vacía en nodo {node.node_id}, aplicando fallback")
                    return node.model_copy(update={"latex": _safe_fallback(content), "status": "fallback_empty"})
                    
                elif _is_latex_structurally_suspicious(translated):
                    logger.warning(f"Estructura LaTeX corrupta detectada en nodo {node.node_id}, aplicando fallback")
                    return node.model_copy(update={"latex": _safe_fallback(content), "status": "fallback_suspicious"})
                    
                return node.model_copy(update={"latex": translated, "status": "ok"})
                
            elif node.type == "display_equation":
                return node.model_copy(update={"latex": node.latex or node.content, "status": "ok"})
                
        except Exception as e:
            logger.error(f"Fallo terminal en nodo {node.node_id}: {e}")
            logger.warning(f"Fallback de emergencia aplicado en nodo {node.node_id}")
            return node.model_copy(update={"latex": _safe_fallback(node.content), "status": "error"})
            
        return node