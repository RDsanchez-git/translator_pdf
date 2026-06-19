import os
import requests
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from apps.llm_workers.prompt_builder import PromptBuilder
from core.ast.models import ASTNode
from core.resilience.circuit_breaker import CircuitBreakerRegistry
from core.execution.exceptions import TransientAPIError
from core.ast.models import TranslationUnit
from core.utils.rate_limiter import GLOBAL_RATE_LIMITER
from core.utils.telemetry import ctx_execution_id, ctx_worker_id

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada.")
        
        self.base_url = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com")
        self.model_v = 'gemini-2.5-flash'
        self.limiter = GLOBAL_RATE_LIMITER
        self.breaker = CircuitBreakerRegistry.get_breaker(self.model_v)
        
        self.session = requests.Session()

        self.system_instruction = """You are an expert LaTeX translator.
        Your ONLY task is to translate the given text to Spanish while maintaining strictly VALID LaTeX formatting.

        STRICT RULES:
        1. Do NOT modify math expressions, variables, or symbols.
        2. Output ONLY raw LaTeX body text.
        3. Do NOT output \\documentclass, \\usepackage, or \\begin{document}.
        4. Do NOT include explanations.
        5. Do NOT wrap output in markdown blocks.
        6. All environments must be properly closed.
        7. All brackets {}, (), [] must be balanced.
        8. Escape special characters: %, $, _, &, #.

        If the input is ambiguous, produce the safest valid LaTeX translation possible."""

    def _clean_response(self, text: str | None) -> str:
        result = (text or "").strip()
        if result.startswith("```latex"):
            result = result[8:]
        elif result.startswith("```tex"):
            result = result[7:]
        elif result.startswith("```"):
            result = result[3:]
            
        if result.endswith("```"):
            result = result[:-3]
            
        return result.strip()

    def _build_fix_prompt(self, broken_output: str, reason: str) -> str:
        return f"The following LaTeX output is INVALID.\n\nReason:\n{reason}\n\nFix the LaTeX structure while preserving the Spanish translation. Return ONLY valid LaTeX.\nDo not explain anything.\n\nBROKEN OUTPUT:\n{broken_output}\n\nFIXED OUTPUT:\n"

    def _is_transient(self, status_code: int) -> bool:
        return status_code in [429, 500, 502, 503, 504]

    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=30),
        stop=stop_after_attempt(1),
        retry=retry_if_exception_type(TransientAPIError),
        reraise=True
    )
    def _execute_with_local_retries(self, prompt: str, temp: float) -> str:
        self.breaker.check_state()
        self.limiter.acquire()
        
        url = f"{self.base_url}/v1beta/models/{self.model_v}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": self.system_instruction}]},
            "generationConfig": {"temperature": temp}
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-execution-id": ctx_execution_id.get("unknown_exec"),
            "x-worker-id": ctx_worker_id.get("unknown_worker")
        }

        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=(5.0, 30.0))
            
            if not response.ok:
                logger.warning(f"HTTP Error {response.status_code}: {response.text[:200]}")
                if self._is_transient(response.status_code):
                    raise TransientAPIError(f"HTTP {response.status_code}: {response.text}")
                response.raise_for_status()

            try:
                data = response.json()
            except ValueError as e:
                raise TransientAPIError(f"Malformed JSON: {str(e)}")

            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return self._clean_response(raw_text)
            
        except requests.exceptions.RequestException as e:
            raise TransientAPIError(f"Network Failure: {str(e)}")
        finally:
            self.limiter.release()


    # Reemplazar el método completo dentro de la clase GeminiClient:
    def translate(self, node: ASTNode, chunk_idx: int = 1, total_chunks: int = 1) -> str:
        """SOTA Fallback: Traduce un nodo individual empaquetándolo en una unidad 
        efímera para cumplir con el contrato del nuevo PromptBuilder de producción.
        """
        # 1. Construcción de la unidad de traducción en caliente
        mock_unit = TranslationUnit(
            chunk_index=chunk_idx,
            chunk_id=node.node_id,
            chunk_type="translate",
            source_sequence_range=(chunk_idx, chunk_idx),
            node_count=1,
            reference_context="",
            target_payload=node.content or "",
            estimated_tokens=0,
            payload_sha256=""
        )
        
        # 2. Instanciación e invocación limpia del método de instancia
        builder = PromptBuilder()
        prompt = builder.build(mock_unit)
        
        return self.breaker.call(lambda: self._execute_with_local_retries(prompt, temp=0.2))

    def fix_latex(self, broken_output: str, reason: str) -> str:
        prompt = self._build_fix_prompt(broken_output, reason)
        return self.breaker.call(lambda: self._execute_with_local_retries(prompt, temp=0.1))
    
    def generate(self, prompt: str) -> str:
        """SOTA: Punto de entrada público y encapsulado para procesar prompts crudos 
        bajo el control del Circuit Breaker y Rate Limiter del perímetro de red.
        """
        return self.breaker.call(lambda: self._execute_with_local_retries(prompt, temp=0.2))
    
    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=30),
        stop=stop_after_attempt(1),
        retry=retry_if_exception_type(TransientAPIError),
        reraise=True
    )
    def _embed_with_local_retries(self, text: str) -> list[float]:
        self.breaker.check_state()
        self.limiter.acquire()
        
        # SOTA 2026: Actualización obligatoria a gemini-embedding-001 por apagón de v004
        url = f"{self.base_url}/v1beta/models/gemini-embedding-001:embedContent?key={self.api_key}"
        payload = {"content": {"parts": [{"text": text}]}}
        headers = {
            "Content-Type": "application/json",
            "x-execution-id": ctx_execution_id.get("unknown_exec"),
            "x-worker-id": ctx_worker_id.get("unknown_worker")
        }

        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=(5.0, 30.0))
            if not response.ok:
                logger.warning(f"HTTP Error {response.status_code} en Embeddings: {response.text[:200]}")
                if self._is_transient(response.status_code):
                    raise TransientAPIError(f"HTTP {response.status_code}: {response.text}")
                response.raise_for_status()

            try:
                data = response.json()
            except ValueError as e:
                raise TransientAPIError(f"Malformed JSON: {str(e)}")

            return data["embedding"]["values"]
        except requests.exceptions.RequestException as e:
            raise TransientAPIError(f"Network Failure on Embeddings: {str(e)}")
        finally:
            self.limiter.release()

    def embed_text(self, text: str) -> list[float]:
        """SOTA: Punto de entrada encapsulado para vectorización cross-lingual con gemini-embedding-001."""
        if not text or not text.strip():
            return []
        return self.breaker.call(lambda: self._embed_with_local_retries(text))