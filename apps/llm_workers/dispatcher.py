# apps/llm_workers/dispatcher.py
import asyncio
import logging
from typing import List, Optional
from core.ast.models import TranslationUnit, TranslatedUnit
from apps.llm_workers.workers import TranslationWorkerProtocol
from apps.llm_workers.cache import SQLiteTranslationCache
from core.execution.exceptions import ChunkExecutionError, ChunkValidationError, DocumentValidationError
from core.validation.models import ValidationContext, Scope, Severity
from core.validation.pipeline import ValidationPipeline
from core.validation.legacy_adapter import LegacyValidatorAdapter
from core.validation.structural_validator import StructuralValidator
from core.validation.preservation import PreservationValidator
from core.validation.perimeter import PerimeterValidator
from core.validation.semantic import SemanticValidator

logger = logging.getLogger(__name__)

class AsyncDispatcher:
    """SOTA: Orquestador concurrente definitivo con control de caché, validación secuencial y resiliencia."""
    
    def __init__(
        self, 
        worker: TranslationWorkerProtocol, 
        cache: SQLiteTranslationCache, 
        model_name: str, 
        prompt_version: str,
        validation_pipeline: Optional[ValidationPipeline] = None
    ):
        self.worker = worker
        self.cache = cache
        self.model_name = model_name
        self.prompt_version = prompt_version
        self.validation_pipeline = validation_pipeline or self._default_pipeline()

    @staticmethod
    def _default_pipeline() -> ValidationPipeline:
        # TODO 11E.5: Mover la composición de este pipeline al bootstrap/container externo
        severity_map = {
            "RESIDUAL_HTML": Severity.HARD_FAIL,
            "UNBALANCED_BRACES_EARLY": Severity.HARD_FAIL,
            "UNBALANCED_BRACES_OPEN": Severity.HARD_FAIL,
            "UNBALANCED_BRACKETS_EARLY": Severity.HARD_FAIL,
            "UNBALANCED_BRACKETS_OPEN": Severity.HARD_FAIL,
            "UNBALANCED_DISPLAY_MATH": Severity.HARD_FAIL,
            "UNBALANCED_INLINE_MATH": Severity.HARD_FAIL,
            "ENV_MISMATCH": Severity.HARD_FAIL,
            "ENV_UNCLOSED": Severity.HARD_FAIL,
        }
        adapter = LegacyValidatorAdapter(StructuralValidator, severity_map)
        pv = PreservationValidator()
        pe = PerimeterValidator()
        sv = SemanticValidator()  # Instancia semántica cuantitativa
        
        pipeline = ValidationPipeline()
        pipeline.add_chunk_validator(adapter)
        pipeline.add_chunk_validator(pv)
        pipeline.add_chunk_validator(pe)
        pipeline.add_chunk_validator(sv)  # Registro bajo alcance CHUNK (WARNING)
        pipeline.add_document_validator(pv)
        return pipeline
   

    async def _bypass_passthrough(self, unit: TranslationUnit) -> TranslatedUnit:
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
        if unit.chunk_type == "passthrough":
            return await self._bypass_passthrough(unit)

        is_new_translation = False
        cached_payload = await self.cache.get(
            payload_sha256=unit.payload_sha256,
            model_name=self.model_name,
            prompt_version=self.prompt_version
        )

        if cached_payload is not None:
            translated = TranslatedUnit(
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
        else:
            translated = await self.worker.translate(unit)
            is_new_translation = True

        if self.validation_pipeline:
            ctx = ValidationContext(
                source_text=unit.target_payload,
                target_text=translated.translated_payload,
                scope=Scope.CHUNK,
                chunk_index=unit.chunk_index,
                chunk_type=unit.chunk_type,
                payload_sha256=unit.payload_sha256
            )
            results = self.validation_pipeline.validate_chunk(ctx)
            for res in results:
                if res.severity == Severity.HARD_FAIL:
                    logger.error(f"Validation HARD_FAIL: [{res.invariant_id}] {res.message}")
                    raise ChunkValidationError(unit.chunk_index, unit.chunk_id, res.invariant_id, res.message)
                elif res.severity == Severity.WARNING:
                    logger.warning(f"Validation WARNING: [{res.invariant_id}] {res.message}")
                else:
                    logger.info(f"Validation INFO: [{res.invariant_id}] {res.message}")

        if is_new_translation:
            await self.cache.set(
                payload_sha256=unit.payload_sha256,
                model_name=self.model_name,
                prompt_version=self.prompt_version,
                translated_payload=translated.translated_payload
            )

        logger.info(
            "chunk_translated",
            extra={
                "extra_data": {
                    "chunk_index": unit.chunk_index,
                    "chunk_id": unit.chunk_id,
                    "chunk_type": unit.chunk_type,
                    "payload_sha256": unit.payload_sha256,
                    "model": translated.model_name,
                    "input_tokens": translated.input_tokens,
                    "output_tokens": translated.output_tokens,
                    "latency_ms": translated.latency_ms,
                    "original_length": len(unit.target_payload),
                    "translated_length": len(translated.translated_payload),
                }
            }
        )

        return translated

    async def dispatch(self, units: List[TranslationUnit]) -> List[TranslatedUnit]:
        chunk_indexes = [u.chunk_index for u in units]
        if len(set(chunk_indexes)) != len(chunk_indexes):
            raise ValueError("Duplicate chunk_index detected")

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
                if isinstance(result, ChunkValidationError):
                    raise result
                raise ChunkExecutionError(units[i].chunk_index, units[i].chunk_id, result) from result
            
            final_units.append(result)

        final_units_sorted = sorted(final_units, key=lambda x: x.chunk_index)

        if self.validation_pipeline:
            # CORRECCIÓN SOTA: Reconstrucción segura utilizando el parámetro de entrada original 'units'
            full_source = "".join([u.target_payload for u in sorted(units, key=lambda x: x.chunk_index)])
            full_document = "".join([u.translated_payload for u in final_units_sorted])
            
            ctx = ValidationContext(
                source_text=full_source,  # Inyección real del documento origen
                target_text=full_document,
                scope=Scope.DOCUMENT
            )
            results_doc = self.validation_pipeline.validate_document(ctx)
            for res in results_doc:
                if res.severity == Severity.HARD_FAIL:
                    logger.error(f"Document validation HARD_FAIL: [{res.invariant_id}] {res.message}")
                    # Corrección de contrato unificado
                    raise DocumentValidationError(res.invariant_id, f"Document validation failed: {res.message}")
                elif res.severity == Severity.WARNING:
                    logger.warning(f"Document validation WARNING: [{res.invariant_id}] {res.message}")
                else:
                    logger.info(f"Document validation INFO: [{res.invariant_id}] {res.message}")

        return final_units_sorted