import asyncio
import logging
from typing import List, Optional, Dict
from dataclasses import replace
from core.ast.models import TranslationUnit, TranslatedUnit, ChunkOutcome, ExecutionStatus, FailureReason, DispatchResult
from apps.llm_workers.prompt_builder import PromptEnvelope, PromptBuilder, PromptBuildResult, BuildFailureReason
from apps.llm_workers.routing import ProviderResult, LLMProvider
from core.execution.exceptions import CircuitOpenError
from core.context.context_resolver import ContextResolverProtocol, ResolvedContext
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

logger = logging.getLogger(__name__)

class AsyncDispatcher:
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
                translated = replace(
                    translated, 
                    translated_payload=healing_result.final_text,
                    model_name=f"healed:{translated.model_name}"
                )
                results = self.validation_pipeline.validate_chunk(replace(ctx, target_text=translated.translated_payload))
                hard_fails = [] 

        if hard_fails:
            res = hard_fails[0]
            raise ValueError(f"[{res.invariant_id}] {res.message}")

        return translated

    async def _worker(self, queue: asyncio.Queue, results: Dict[int, ChunkOutcome]) -> None:
        while True:
            try:
                unit, envelope = await queue.get()
            except asyncio.CancelledError:
                break

            try:
                provider_result = await self._provider.translate(envelope)
                translated = await self._process_validation_and_healing(unit, provider_result, envelope)
                
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.SUCCESS,
                    original_payload_sha256=unit.payload_sha256, # SOTA: O(1) memory footprint
                    translated_unit=translated,
                    failure_reason=None,
                    error_message=None
                )
            except CircuitOpenError as e:
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=FailureReason.RETRY_EXHAUSTED,
                    error_message=str(e)
                )
            except ValueError as e: # Captura el hard fail del validador
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=FailureReason.VALIDATION_FAILURE,
                    error_message=str(e)
                )
            except Exception as e:
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=FailureReason.PROVIDER_FAILURE,
                    error_message=str(e)
                )
            finally:
                queue.task_done()

    async def dispatch(self, units: List[TranslationUnit]) -> DispatchResult:
        if not units:
            return DispatchResult(outcomes=[])

        chunk_indexes = [u.chunk_index for u in units]
        if len(set(chunk_indexes)) != len(chunk_indexes):
            raise ValueError("Duplicate chunk_index detected")

        context_ids = {u.context_id for u in units if u.context_id}
        resolved_contexts = self.context_resolver.resolve_many(context_ids)

        queue: asyncio.Queue = asyncio.Queue()
        outcomes_map: Dict[int, ChunkOutcome] = {} 

        for unit in units:
            context = resolved_contexts.get(unit.context_id) or ResolvedContext(
                context_id=unit.context_id,
                breadcrumbs=()
            )
            
            # SOTA: Consumo del Discriminated Union
            build_result: PromptBuildResult = self.prompt_builder.build(unit, context)
            
            if build_result.status == "success":
                queue.put_nowait((unit, build_result.envelope))
            else:
                outcomes_map[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=FailureReason.CONTEXT_OVERFLOW if build_result.error_reason == BuildFailureReason.CONTEXT_OVERFLOW else FailureReason.PROVIDER_FAILURE,
                    error_message=build_result.message
                )

        workers = [asyncio.create_task(self._worker(queue, outcomes_map)) for _ in range(self._concurrency)]

        try:
            await queue.join()
        finally:
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)

        # SOTA FIX: Red de seguridad para outcomes_map incompleto (Worker Hard-Crash)
        missing_indexes = set(chunk_indexes) - set(outcomes_map.keys())
        if missing_indexes:
            logger.error(f"FATAL: {len(missing_indexes)} chunks perdidos por crash no controlado en Workers.")
            for idx in missing_indexes:
                unit = next(u for u in units if u.chunk_index == idx)
                outcomes_map[idx] = ChunkOutcome(
                    chunk_index=idx,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=FailureReason.UNHANDLED_WORKER_CRASH,
                    error_message="El Worker colapsó o fue cancelado antes de registrar el outcome."
                )

        final_outcomes_sorted = [outcomes_map[idx] for idx in sorted(outcomes_map.keys())]

        return DispatchResult(outcomes=final_outcomes_sorted)