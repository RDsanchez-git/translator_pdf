import time
import logging
from tenacity import (
    retry, wait_exponential, stop_after_attempt, 
    stop_after_delay, retry_if_exception_type, before_sleep_log
)
# SOTA Fix 1: Importar los Enums reales (NodeType es ahora solo un Union)
from core.ast.models import ASTNode
from core.metrics.metrics import Metrics
from apps.llm_workers.gemini_client import GeminiClient
from core.utils.rate_limiter import IN_FLIGHT_LIMITER
from apps.llm_workers.router_translation import TranslationRouter

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
    """
    SOTA: Procesador Puro. 
    Cero acoplamiento transaccional. Entra ASTNode, sale texto.
    """
    def __init__(self, client: GeminiClient, metrics: Metrics):
        self.client = client
        self.metrics = metrics
        self.prompt_v = "v3_latex_optimized"
        self.model_v = "gemini-2.5-flash" 
        self.projection_v = 1 

    @retry(
        wait=wait_exponential(multiplier=2, min=10, max=65),
        stop=stop_after_attempt(8) | stop_after_delay(600),
        retry=retry_if_exception_type(LLMTransientError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def execute(self, node: ASTNode, chunk_idx: int = 1, total_chunks: int = 1) -> str:
        """SOTA: Lógica de negocio aislada gobernada por política de nodo."""
        
        policy = TranslationRouter.get_strategy(node.type)
        
        # Fast-Path Nativo: Evade el consumo de TPM/RPM y previene mutaciones
        if policy == "PRESERVE":
            # SOTA Fix 2: Cast seguro a string puro para cumplir con firma -> str
            return str(node.latex or node.content or "")

        start_net = time.perf_counter()
        try:
            with IN_FLIGHT_LIMITER:
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