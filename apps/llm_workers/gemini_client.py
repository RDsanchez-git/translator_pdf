import os
from google import genai
from google.genai import types

class GeminiClient:
    def __init__(self, api_key: str | None = None):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY no encontrada.")
        
        self.client = genai.Client(api_key=key)

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

        self.few_shot = """EXAMPLES:

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
\\end{itemize}
"""

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

    def _build_prompt(self, text: str, chunk_idx: int, total_chunks: int) -> str:
        # SOTA: Prompt Defensivo Generalizado
        chunk_context = f"""---
        ESTA ES LA PARTE {chunk_idx} DE {total_chunks} DEL DOCUMENTO COMPLETO.

        REGLAS CRÍTICAS:
        - NO omitir contenido.
        - NO resumir ni agregar explicaciones propias.
        - NO repetir contenido de otras partes.
        - NO inventar texto.

        FORMATO DE ENTRADA (CRÍTICO):
        - El texto puede contener una mezcla de texto plano y comandos LaTeX.
        - Si un título aparece como texto plano (ej: "Section 1:"), NO lo conviertas en comando LaTeX.
        - SOLO traduce literalmente sin cambiar el tipo de estructura original.

        FORMATO OCR/MARKDOWN:
        - El texto puede contener sintaxis Markdown generada automáticamente por un OCR.
        - Si detectas referencias a imágenes o tablas, consérvalas como comentarios.
        - NUNCA dejes símbolos crudos incompatibles con LaTeX en la salida final (asegúrate de escapar &, %, _, # si aparecen en texto plano).

        MATEMÁTICA:
        - PROHIBIDO modificar símbolos matemáticos o renombrar variables.
        - PROHIBIDO simplificar expresiones.
        - SI hay duda, copiar EXACTAMENTE el original.

        LATEX Y MULTIMEDIA:
        - Mantener estructura LaTeX intacta. NO modificar comandos como \\label, \\ref, \\cite, \\begin, \\end.
        - TÍTULOS: Traduce el contenido de los comandos de sección.
        - FIGURAS Y TABLAS: Mantén intactos los entornos completos. Traduce ÚNICAMENTE el texto dentro de los comandos \\caption{{...}}.

        CONSISTENCIA:
        - Mantener terminología técnica consistente dentro de ESTE fragmento.
        - Traducir de forma fiel al original.
        ---"""
        return f"{self.few_shot}\n\n{chunk_context}\n\nTEXT TO TRANSLATE:\n{text}\n\nOUTPUT:\n"

    def _build_fix_prompt(self, broken_output: str, reason: str) -> str:
        return f"The following LaTeX output is INVALID.\n\nReason:\n{reason}\n\nFix the LaTeX structure while preserving the Spanish translation. Return ONLY valid LaTeX.\nDo not explain anything.\n\nBROKEN OUTPUT:\n{broken_output}\n\nFIXED OUTPUT:\n"

    def translate(self, text: str, chunk_idx: int = 1, total_chunks: int = 1) -> str:
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            # SOTA: Paso de índices dinámicos al generador de prompts
            contents=self._build_prompt(text, chunk_idx, total_chunks),
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.2
            )
        )
        return self._clean_response(response.text)

    def fix_latex(self, broken_output: str, reason: str) -> str:
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=self._build_fix_prompt(broken_output, reason),
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.1
            )
        )
        return self._clean_response(response.text)