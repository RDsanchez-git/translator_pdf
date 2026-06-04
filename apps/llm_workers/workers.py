import time
import asyncio
from typing import Protocol
from core.ast.models import TranslationUnit, TranslatedUnit, TokenEstimator
from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.gemini_client import GeminiClient

class TranslationWorkerProtocol(Protocol):
    """SOTA: Interfaz estructural que desacopla el Dispatcher de los proveedores de LLM."""
    async def translate(self, unit: TranslationUnit) -> TranslatedUnit:
        ...

class FakeGeminiWorker:
    """SOTA: Cliente concurrente simulado para validación de la capa de despacho."""
    
    def __init__(self, prompt_builder: PromptBuilder, estimator: TokenEstimator):
        self.prompt_builder = prompt_builder
        self.estimator = estimator
        self.model_name = "fake-gemini-1.5-flash"

    async def translate(self, unit: TranslationUnit) -> TranslatedUnit:
        start_time = time.perf_counter()
        prompt = self.prompt_builder.build(unit)
        
        await asyncio.sleep(0.01)
        
        simulated_translation = f"FAKE_TRANSLATION::{unit.payload_sha256[:8]}"
        
        input_toks = self.estimator.estimate(prompt)
        output_toks = self.estimator.estimate(simulated_translation)
        latency_ms = (time.perf_counter() - start_time) * 1000

        return TranslatedUnit(
            chunk_index=unit.chunk_index,
            chunk_id=unit.chunk_id,
            chunk_type=unit.chunk_type,
            source_sequence_range=unit.source_sequence_range,
            translated_payload=simulated_translation,
            payload_sha256=unit.payload_sha256,
            model_name=self.model_name,
            prompt_version=self.prompt_builder.PROMPT_VERSION,
            input_tokens=input_toks,
            output_tokens=output_toks,
            latency_ms=latency_ms
        )

class GeminiWorker:
    """SOTA: Adaptador asíncrono real de producción. Envuelve el cliente síncrono
    de Gemini delegando la llamada de red bloqueante al pool de hilos de asyncio.
    """
    
    def __init__(self, client: GeminiClient, prompt_builder: PromptBuilder, estimator: TokenEstimator):
        self.client = client
        self.prompt_builder = prompt_builder
        self.estimator = estimator

    async def translate(self, unit: TranslationUnit) -> TranslatedUnit:
        """Orquesta la traducción delegando de forma segura el transporte bloqueante."""
        start_time = time.perf_counter()
        
        # Corrección 2: Consistencia absoluta usando el método de instancia inyectado
        prompt = self.prompt_builder.build(unit)
        
        # Corrección 1: Respeto estricto a la encapsulación pública de la API
        translated_payload = await asyncio.to_thread(
            self.client.generate,
            prompt
        )
        
        # Corrección 3: Estimación local transitoria (Será sustituida por usage_metadata en 11B.5)
        input_tokens = self.estimator.estimate(prompt)
        output_tokens = self.estimator.estimate(translated_payload)
        latency_ms = (time.perf_counter() - start_time) * 1000

        return TranslatedUnit(
            chunk_index=unit.chunk_index,
            chunk_id=unit.chunk_id,
            chunk_type=unit.chunk_type,
            source_sequence_range=unit.source_sequence_range,
            translated_payload=translated_payload,
            payload_sha256=unit.payload_sha256,
            model_name=self.client.model_v,
            prompt_version=self.prompt_builder.PROMPT_VERSION,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms
        )