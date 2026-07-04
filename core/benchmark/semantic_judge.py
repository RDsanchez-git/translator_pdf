import os
import json
import asyncio
import logging
from groq import AsyncGroq
from core.benchmark.judge_models import ChunkEvaluationScore
from core.benchmark.judge_prompts import SYSTEM_PROMPT, build_judge_prompt

logger = logging.getLogger(__name__)

class SemanticJudge:
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model
        
    async def evaluate_chunk(self, source_text: str, target_text: str, max_retries: int = 5) -> ChunkEvaluationScore:
        user_content = build_judge_prompt(source_text, target_text)
        
        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_content}
                        ],
                        temperature=0.0,
                        response_format={"type": "json_object"},
                        max_tokens=600
                    ),
                    timeout=20.0
                )
                
                raw_content = response.choices[0].message.content
                if not raw_content:
                    raise ValueError("La API de Groq retornó un cuerpo de contenido vacío o nulo.")
                
                parsed_data = json.loads(raw_content)
                return ChunkEvaluationScore(**parsed_data)
                
            except (Exception, asyncio.TimeoutError) as e:
                # DIAGNÓSTICO SOTA: Extraer el tipo y mensaje real expuesto por el SDK
                error_msg = str(e)
                error_type = type(e).__name__
                print(f"\n[ALERTA FORENSE] Tipo: {error_type} | Mensaje: {error_msg}")
                
                if "429" in error_msg.lower() or isinstance(e, asyncio.TimeoutError):
                    wait_time = (2 ** attempt) * 10.0
                    logger.warning(f"Cooldown de {wait_time}s... (Intento {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Fallo de parseo JSON o validación Pydantic: {e}")
                    if attempt == max_retries - 1:
                        raise e
        
        raise RuntimeError("Máximo de reintentos alcanzado en SemanticJudge")