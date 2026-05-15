import os
from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from apps.llm_workers.prompt_builder import PromptBuilder
from core.ast.models import ASTNode
from core.resilience.circuit_breaker import CircuitBreakerRegistry
from core.execution.exceptions import TransientAPIError
from core.utils.rate_limiter import GLOBAL_RATE_LIMITER

class GeminiClient:
    def __init__(self, api_key: str | None = None):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY no encontrada.")
        
        self.client = genai.Client(api_key=key)
        self.limiter = GLOBAL_RATE_LIMITER
        
        self.model_v = 'gemini-2.5-flash'
        # SOTA: Instanciación del Breaker aislado por modelo
        self.breaker = CircuitBreakerRegistry.get_breaker(self.model_v)

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

        If the input is ambiguous, produce the safest valid LaTeX translation possible.

        EXAMPLES:
        Input: The equation is x^2 + y^2 = z^2.
        Output: La ecuación es $x^2 + y^2 = z^2$.

        Input: 50% of users prefer option A & B.
        Output: El 50\\% de los usuarios prefiere la opción A \\& B.

        Input: Let f(x) = sin(x).
        Output: Sea $f(x) = \\sin(x)$.

        Input: \\begin{itemize}
        \\item First item
        \\item Second item
        Output: \\begin{itemize}
        \\item Primer elemento
        \\item Segundo elemento
        \\end{itemize}"""

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

    def _is_transient(self, e: Exception) -> bool:
        msg = str(e).lower()
        return any(sig in msg for sig in ["429", "503", "502", "500", "timeout", "quota", "connection"])

    @retry(
        wait=wait_exponential(multiplier=2, min=2, max=30),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(TransientAPIError),
        reraise=True
    )
    def _execute_with_local_retries(self, prompt: str, temp: float) -> str:
        # Breaker-awareness: Abortar reintento interno si el circuito global se abrió
        self.breaker.check_state()
        
        self.limiter.acquire()
        try:
            response = self.client.models.generate_content(
                model=self.model_v,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=temp
                )
            )
            return self._clean_response(response.text)
        except Exception as e:
            if self._is_transient(e):
                raise TransientAPIError(str(e))
            raise e
        finally:
            self.limiter.release()

    def translate(self, node: ASTNode, chunk_idx: int = 1, total_chunks: int = 1) -> str:
        prompt = PromptBuilder.build(node, chunk_idx, total_chunks)
        # El Breaker orquesta la supervivencia macro
        return self.breaker.call(lambda: self._execute_with_local_retries(prompt, temp=0.2))

    def fix_latex(self, broken_output: str, reason: str) -> str:
        prompt = self._build_fix_prompt(broken_output, reason)
        return self.breaker.call(lambda: self._execute_with_local_retries(prompt, temp=0.1))