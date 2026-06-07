import asyncio
import logging
from typing import List
from core.ast.models import TranslationUnit, TranslatedUnit
from apps.llm_workers.workers import TranslationWorkerProtocol
from apps.llm_workers.cache import SQLiteTranslationCache
from core.execution.exceptions import ChunkExecutionError

logger = logging.getLogger(__name__)

class AsyncDispatcher:
    """SOTA: Orquestador concurrente definitivo con bypass perimetral, control de caché y resiliencia."""
    
    def __init__(
        self, 
        worker: TranslationWorkerProtocol, 
        cache: SQLiteTranslationCache, 
        model_name: str, 
        prompt_version: str
    ):
        self.worker = worker
        self.cache = cache
        self.model_name = model_name
        self.prompt_version = prompt_version

    async def _bypass_passthrough(self, unit: TranslationUnit) -> TranslatedUnit:
        """Aislamiento topológico instantáneo con latencia cero y costo de API cero."""
        return TranslatedUnit(
            chunk_index=unit.chunk_index,
            chunk_id=unit.chunk_id,
            chunk_type=unit.chunk_type,
            source_sequence_range=unit.source_sequence_range,
            translated_payload=unit.target_payload,
            payload_sha256=unit.payload_sha256,
            model_name="bypass_passthrough",
            prompt_version="none",
            input_tokens=0,
            output_tokens=0,
            latency_ms=0.0
        )

    async def _process_unit(self, unit: TranslationUnit) -> TranslatedUnit:
        """Grafo de decisión atómico por unidad de traducción."""
        if unit.chunk_type == "passthrough":
            return await self._bypass_passthrough(unit)

        # 10C.6: Interceptación preventiva mediante firma criptográfica compuesta
        cached_payload = await self.cache.get(
            payload_sha256=unit.payload_sha256,
            model_name=self.model_name,
            prompt_version=self.prompt_version
        )

        if cached_payload is not None:
            return TranslatedUnit(
                chunk_index=unit.chunk_index,
                chunk_id=unit.chunk_id,
                chunk_type=unit.chunk_type,
                source_sequence_range=unit.source_sequence_range,
                translated_payload=cached_payload,
                payload_sha256=unit.payload_sha256,
                model_name=f"cache_hit:{self.model_name}",
                prompt_version=self.prompt_version,
                input_tokens=0,
                output_tokens=0,
                latency_ms=0.0
            )

        # Cache Miss: Despacho regulado a la capa de transporte de red
        translated_unit = await self.worker.translate(unit)

        # Persistencia asíncrona inmediata pos-traducción exitosa
        await self.cache.set(
            payload_sha256=unit.payload_sha256,
            model_name=self.model_name,
            prompt_version=self.prompt_version,
            translated_payload=translated_unit.translated_payload
        )

        logger.info(
            "chunk_translated",
            extra={
                "extra_data": {
                    "chunk_index": unit.chunk_index,
                    "chunk_id": unit.chunk_id,
                    "chunk_type": unit.chunk_type,
                    "payload_sha256": unit.payload_sha256,
                    "model": translated_unit.model_name,
                    "input_tokens": translated_unit.input_tokens,
                    "output_tokens": translated_unit.output_tokens,
                    "latency_ms": translated_unit.latency_ms,
                    "original_length": len(unit.target_payload),
                    "translated_length": len(translated_unit.translated_payload),
                }
            }
        )

        return translated_unit

    async def dispatch(self, units: List[TranslationUnit]) -> List[TranslatedUnit]:
        # Verificación defensiva contra corrupción de índices aguas arriba
        chunk_indexes = [u.chunk_index for u in units]
        if len(set(chunk_indexes)) != len(chunk_indexes):
            raise ValueError("Duplicate chunk_index detected")

        # Mapeo concurrente de corrutinas en el bucle de eventos
        tasks = [self._process_unit(u) for u in units]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_units = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "chunk_failed",
                    extra={
                        "extra_data": {
                            "chunk_index": units[i].chunk_index,
                            "chunk_id": units[i].chunk_id,
                            "error_class": result.__class__.__name__,
                            "error_message": str(result),
                            "original_length": len(units[i].target_payload),
                        }
                    }
                )
                raise ChunkExecutionError(units[i].chunk_index, units[i].chunk_id, result) from result
            
            final_units.append(result)

        # Garantizar orden lineal indexado para el ensamble determinista (Fase 10D)
        return sorted(final_units, key=lambda x: x.chunk_index)