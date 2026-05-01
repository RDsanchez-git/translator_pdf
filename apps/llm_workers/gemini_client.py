import os
from google import genai

class GeminiClient:
    def __init__(self, api_key: str | None = None):
        # SOTA: Fallback a variable de entorno si no se inyecta
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY no encontrada.")
        
        self.client = genai.Client(api_key=key)

    def translate(self, text: str) -> str:
        prompt = f"""
Translate to Spanish. Format strictly as raw LaTeX body text.
RULES:
1. Do NOT modify math expressions or symbols.
2. Do NOT output \\documentclass, \\usepackage, or \\begin{{document}}.
3. Do NOT wrap output in markdown blocks (e.g. ```latex). Return raw text only.

TEXT:
{text}
"""
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        result = response.text.strip()
        
        # Sanitización estructural defensiva
        if result.startswith("```latex"):
            result = result[8:]
        elif result.startswith("```tex"):
            result = result[7:]
        elif result.startswith("```"):
            result = result[3:]
            
        if result.endswith("```"):
            result = result[:-3]
            
        return result.strip()