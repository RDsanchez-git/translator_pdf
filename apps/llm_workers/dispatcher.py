import asyncio
import logging
from typing import List, Optional, Dict
from dataclasses import replace
from core.ast.models import TranslationUnit, TranslatedUnit
from apps.llm_workers.prompt_builder import PromptEnvelope, PromptBuilder
from apps.llm_workers.routing import ProviderResult, LLMProvider
from core.execution.exceptions import CircuitOpenError
from core.context.context_resolver import ContextResolverProtocol
from core.execution.exceptions import ChunkExecutionError, ChunkValidationError, DocumentValidationError
from core.validation.models import ValidationContext, Scope, Severity
from core.validation.pipeline import ValidationPipeline
from core.validation.legacy_adapter import LegacyValidatorAdapter
from core.validation.structural_validator import StructuralValidator
from core.validation.preservation import PreservationValidator
from core.validation.perimeter import PerimeterValidator
from core.validation.semantic import SemanticValidator
from core.validation.volumetric import VolumetricValidator
from core.healing.models import HealingContext, HealingOutcome
from core.healing.pipeline import HealingPipeline
from core.context.context_resolver import ResolvedContext

logger = logging.getLogger(__name__)

class AsyncDispatcher:
    """SOTA: Orquestador concurrente con Worker Pool, Stack Decorado (ADR 007), Validación y Healing."""
    
    def __init__(
        self, 
        context_resolver: ContextResolverProtocol,
        prompt_builder: PromptBuilder,
        provider_stack: LLMProvider, 
        concurrency: int = 20,
        validation_pipeline: Optional[ValidationPipeline] = None,
        healing_pipeline: Optional[HealingPipeline] = None
    ):
        self.context_resolver = context_resolver
        self.prompt_builder = prompt_builder
        self._provider = provider_stack
        self._concurrency = concurrency
        self.validation_pipeline = validation_pipeline or self._default_pipeline()
        self.healing_pipeline = healing_pipeline

    @staticmethod
    def _default_pipeline() -> ValidationPipeline:
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
        pipeline = ValidationPipeline()
        pipeline.add_chunk_validator(adapter)
        pipeline.add_document_validator(adapter)
        pipeline.add_chunk_validator(PreservationValidator())
        pipeline.add_chunk_validator(PerimeterValidator())
        pipeline.add_chunk_validator(SemanticValidator())
        pipeline.add_chunk_validator(VolumetricValidator())
        pipeline.add_document_validator(PreservationValidator())
        return pipeline

    async def _process_validation_and_healing(self, unit: TranslationUnit, provider_result: ProviderResult, envelope: PromptEnvelope) -> TranslatedUnit:
        # SOTA: Extracción pragmática segura independiente de la resolución de importaciones.
        chunk_type_str = getattr(unit.chunk_type, 'value', unit.chunk_type)

        translated = TranslatedUnit(
            chunk_index=unit.chunk_index,
            chunk_id=unit.chunk_id,
            chunk_type=chunk_type_str,
            source_sequence_range=unit.source_sequence_range,
            translated_payload=provider_result.translated_text,
            payload_sha256=unit.payload_sha256,
            model_name=envelope.model_name if provider_result.finish_reason != "cache_hit" else f"cache_hit:{envelope.model_name}",
            prompt_version=envelope.prompt_version,
            input_tokens=provider_result.input_tokens,
            output_tokens=provider_result.output_tokens,
            latency_ms=provider_result.latency_ms
        )

        if not self.validation_pipeline:
            return translated

        ctx = ValidationContext(
            source_text=unit.target_payload,
            target_text=translated.translated_payload,
            scope=Scope.CHUNK,
            chunk_index=unit.chunk_index,
            chunk_type=unit.chunk_type,
            payload_sha256=unit.payload_sha256
        )
        results = self.validation_pipeline.validate_chunk(ctx)
        hard_fails = [r for r in results if r.severity == Severity.HARD_FAIL]
        
        if hard_fails and self.healing_pipeline:
            healing_ctx = HealingContext(validation_context=ctx, validation_result=hard_fails[0])
            healing_result = self.healing_pipeline.heal_and_revalidate(healing_ctx)
            
            if healing_result.outcome == HealingOutcome.SUCCESS:
                logger.info(f"HEALING_SUCCESS: Chunk {unit.chunk_id} reparado mediante {hard_fails[0].invariant_family}.")
                translated = replace(
                    translated, 
                    translated_payload=healing_result.final_text,
                    model_name=f"healed:{translated.model_name}"
                )
                results = self.validation_pipeline.validate_chunk(replace(ctx, target_text=translated.translated_payload))
                hard_fails = [] 

        if hard_fails:
            res = hard_fails[0]
            logger.error(f"Validation HARD_FAIL: [{res.invariant_id}] {res.message}")
            raise ChunkValidationError(unit.chunk_index, unit.chunk_id, res.invariant_id, res.message)

        for res in results:
            if res.severity == Severity.WARNING:
                logger.warning(f"Validation WARNING: [{res.invariant_id}] {res.message}")

        logger.info("chunk_translated", extra={"extra_data": {
            "chunk_index": translated.chunk_index, "chunk_id": translated.chunk_id,
            "chunk_type": translated.chunk_type, "model": translated.model_name,
            "input_tokens": translated.input_tokens, "output_tokens": translated.output_tokens,
            "latency_ms": translated.latency_ms, "original_length": len(unit.target_payload),
            "translated_length": len(translated.translated_payload)
        }})
        return translated

    async def _worker(self, queue: asyncio.Queue, results: Dict[int, TranslatedUnit], errors: Dict[int, Exception]) -> None:
        while True:
            try:
                unit, envelope = await queue.get()
            except asyncio.CancelledError:
                break

            try:
                provider_result = await self._provider.translate(envelope)
                translated = await self._process_validation_and_healing(unit, provider_result, envelope)
                # SOTA: Indexación segura posicional
                results[unit.chunk_index] = translated
            except CircuitOpenError:
                logger.warning(f"Circuito abierto. Suspendiendo 5s y reencolando índice {unit.chunk_index}.")
                await asyncio.sleep(5.0)
                await queue.put((unit, envelope))
            except Exception as e:
                errors[unit.chunk_index] = e
            finally:
                queue.task_done()

    async def dispatch(self, units: List[TranslationUnit]) -> List[TranslatedUnit]:
        if not units:
            return []

        chunk_indexes = [u.chunk_index for u in units]
        if len(set(chunk_indexes)) != len(chunk_indexes):
            raise ValueError("Duplicate chunk_index detected")

        context_ids = {u.context_id for u in units if u.context_id}
        resolved_contexts = self.context_resolver.resolve_many(context_ids)

        queue: asyncio.Queue = asyncio.Queue()
        results: Dict[int, TranslatedUnit] = {}
        errors: Dict[int, Exception] = {}

        for unit in units:
            # SOTA: Inyección de la identidad técnica del context_id y tupla vacía para cumplir el DTO con slots
            context = resolved_contexts.get(unit.context_id) or ResolvedContext(
                context_id=unit.context_id,
                breadcrumbs=()
            )
            envelope = self.prompt_builder.build(unit, context)
            queue.put_nowait((unit, envelope))

        workers = [asyncio.create_task(self._worker(queue, results, errors)) for _ in range(self._concurrency)]

        try:
            await queue.join()
        finally:
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)

        if errors:
            first_error_index = min(errors.keys())
            first_error = errors[first_error_index]
            first_error_unit = next(u for u in units if u.chunk_index == first_error_index)
            
            if isinstance(first_error, ChunkValidationError):
                raise first_error
            raise ChunkExecutionError(first_error_unit.chunk_index, first_error_unit.chunk_id, first_error) from first_error

        # SOTA: Extracción 100% determinista basada en el índice topológico
        final_units_sorted = [results[idx] for idx in sorted(results.keys())]

        if self.validation_pipeline:
            full_source = "".join([u.target_payload for u in sorted(units, key=lambda x: x.chunk_index)])
            full_document = "".join([u.translated_payload for u in final_units_sorted])
            ctx = ValidationContext(source_text=full_source, target_text=full_document, scope=Scope.DOCUMENT)
            results_doc = self.validation_pipeline.validate_document(ctx)
            for res in results_doc:
                if res.severity == Severity.HARD_FAIL:
                    raise DocumentValidationError(res.invariant_id, f"Document validation failed: {res.message}")

        return final_units_sorted