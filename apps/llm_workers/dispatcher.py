import asyncio
import logging
import itertools
from typing import List, Dict, Any, Tuple
from dataclasses import replace

from core.ast.models import TranslationUnit, TranslatedUnit, ChunkOutcome, ExecutionStatus, FailureReason, DispatchResult
from apps.llm_workers.prompt_builder import PromptEnvelope, PromptBuilder
from apps.llm_workers.routing import LLMProvider
from core.prompting.inference_result import InferenceResult  # SOTA FIX: Nuevo contrato

from core.execution.exceptions import CircuitOpenError, PermanentQuotaRejection, QuotaTimeoutError
from core.context.context_resolver import ContextResolverProtocol, ResolvedContext
from core.validation.models import ValidationContext, Scope, Severity
from core.validation.pipeline import ValidationPipeline
from core.healing.models import HealingOutcome
from core.healing.pipeline import HealingPipeline
from core.validation.budget import BudgetViolationReason
from core.healing.models import HealingFailedException

logger = logging.getLogger(__name__)

# =====================================================================
# SOTA: RESOLUCIÓN DE ENRUTAMIENTO Y PRESUPUESTO
# =====================================================================
MAX_GLOBAL_SUPPORTED_WINDOW = 2097152 # Límite físico absoluto del Stack (ej. Gemini 1.5 Pro)

BUDGET_TO_EXECUTION_FAILURE_MAP = {
    BudgetViolationReason.PAYLOAD_TOO_LARGE: FailureReason.CONTEXT_OVERFLOW,
    BudgetViolationReason.SYSTEM_PROMPT_TOO_LARGE: FailureReason.CONTEXT_OVERFLOW,
    BudgetViolationReason.CONTEXT_TOO_LARGE: FailureReason.CONTEXT_OVERFLOW,
    BudgetViolationReason.OUTPUT_RESERVE_TOO_LARGE: FailureReason.CONTEXT_OVERFLOW,
    BudgetViolationReason.NONE: FailureReason.UNKNOWN_ERROR
}

class AsyncDispatcher:
    """
    NADR-11 §5.1: Todas las dependencias se inyectan por constructor.
    NADR-04 §5.1: ValidationPipeline y HealingPipeline son obligatorios.
    No existe _default_pipeline(). No existe fallback.
    """
    def __init__(
        self, 
        context_resolver: ContextResolverProtocol,
        prompt_builder: PromptBuilder,
        provider_stack: LLMProvider, 
        validation_pipeline: ValidationPipeline,
        healing_pipeline: HealingPipeline,
        concurrency: int = 20,
    ):
        self.context_resolver = context_resolver
        self.prompt_builder = prompt_builder
        self._provider = provider_stack
        self._concurrency = concurrency
        self.validation_pipeline = validation_pipeline
        self.healing_pipeline = healing_pipeline

    async def _process_validation_and_healing(
        self, unit: TranslationUnit, provider_result: InferenceResult, envelope: PromptEnvelope
    ) -> TranslatedUnit:
        chunk_type_str = getattr(unit.chunk_type, 'value', unit.chunk_type)
        target_payload_text = str(provider_result.content)

        translated = TranslatedUnit(
            chunk_index=unit.chunk_index,
            chunk_id=unit.chunk_id,
            chunk_type=chunk_type_str,
            source_sequence_range=unit.source_sequence_range,
            translated_payload=target_payload_text,
            payload_sha256=unit.payload_sha256,
            model_name=envelope.model_name if provider_result.finish_reason != "cache_hit" else f"cache_hit:{envelope.model_name}",
            prompt_version=envelope.prompt_version,
            input_tokens=int(provider_result.input_tokens),
            output_tokens=int(provider_result.output_tokens),
            latency_ms=float(provider_result.latency_ms),
        )
        if not self.validation_pipeline:
            return translated

        ctx = ValidationContext(
            source_text=unit.target_payload,
            target_text=translated.translated_payload,
            scope=Scope.CHUNK,
            chunk_index=unit.chunk_index,
            chunk_type=unit.chunk_type,
            payload_sha256=unit.payload_sha256,
        )

        results = self.validation_pipeline.validate_chunk(ctx)
        hard_fails = [r for r in results if r.severity == Severity.HARD_FAIL]

        if not hard_fails:
            return translated

        if not self.healing_pipeline:
            raise HealingFailedException(
                failures=hard_fails,
                attempted_strategies=[],
                rollback_reason="No healing pipeline configured",
                original_text=target_payload_text,
                mutated_text=target_payload_text,
                chunk_id=unit.chunk_id,
                context_id=unit.context_id or "",
            )

        # NADR-07 §5.1 R1-R3: Colección completa de fallos.
        # NADR-07 §5.3 R7-R9: Revalidación única dentro del healing pipeline.
        healing_result = self.healing_pipeline.heal_all_and_revalidate(ctx, hard_fails)

        if healing_result.outcome == HealingOutcome.SUCCESS:
            # AJUSTE OBLIGATORIO: Usar healed_text directamente.
            # healed_text no es None cuando outcome == SUCCESS.
            translated = replace(
                translated,
                translated_payload=healing_result.healed_text,
                model_name=f"healed:{translated.model_name}",
            )
            return translated
        else:
            raise HealingFailedException(
                failures=hard_fails,
                attempted_strategies=healing_result.strategy_id.split("+") if healing_result.strategy_id != "NONE" else [],
                rollback_reason=healing_result.message,
                original_text=target_payload_text,
                mutated_text=target_payload_text,
                chunk_id=unit.chunk_id,
                context_id=unit.context_id or "",
            )

    # SOTA FIX: Tipado estructural de la Cola para eliminar los Unknowns de priority, seq_id, unit, y envelope.
    async def _worker(self, queue: 'asyncio.PriorityQueue[Tuple[int, int, TranslationUnit, PromptEnvelope]]', results: Dict[int, ChunkOutcome]) -> None:
        while True:
            try:
               _priority, _seq_id, unit, envelope = await queue.get()
            except asyncio.CancelledError:
                break
            try:
                provider_result = await self._provider.translate(envelope)
                translated = await self._process_validation_and_healing(unit, provider_result, envelope)
                
                # SOTA FIX: Aislamiento dict nativo para evitar Unknown Propagation
                base_telemetry = envelope.telemetry or {}
                execution_telemetry: Dict[str, Any] = dict(base_telemetry)
                execution_telemetry["input_tokens"] = int(provider_result.input_tokens)
                execution_telemetry["output_tokens"] = int(provider_result.output_tokens)
                execution_telemetry["latency_ms"] = float(provider_result.latency_ms)
                
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.SUCCESS,
                    original_payload_sha256=unit.payload_sha256, 
                    translated_unit=translated,
                    failure_reason=None,
                    error_message=None,
                    telemetry=execution_telemetry
                )
            except CircuitOpenError as e:
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index, chunk_id=unit.chunk_id, status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256, translated_unit=None,
                    failure_reason=FailureReason.CIRCUIT_OPEN, error_message=str(e), telemetry=envelope.telemetry
                )
            except QuotaTimeoutError as e:
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index, chunk_id=unit.chunk_id, status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256, translated_unit=None,
                    failure_reason=FailureReason.QUOTA_TIMEOUT, error_message=str(e), telemetry=envelope.telemetry
                )
            except PermanentQuotaRejection as e:
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index, chunk_id=unit.chunk_id, status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256, translated_unit=None,
                    failure_reason=FailureReason.QUOTA_REJECTION, error_message=str(e), telemetry=envelope.telemetry
                )

            except HealingFailedException as e:
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=FailureReason.VALIDATION_FAILURE,
                    error_message=str(e),
                    telemetry={
                        **(envelope.telemetry or {}),
                        "healing_attempted_strategies": e.attempted_strategies,
                        "healing_rollback_reason": e.rollback_reason,
                        "healing_unresolved_invariants": [
                            getattr(f, 'invariant_id', 'UNKNOWN') for f in e.failures
                        ],
                    },
                )

            except ValueError as e:
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=FailureReason.VALIDATION_FAILURE,
                    error_message=str(e),
                    telemetry=envelope.telemetry
                )
            except Exception as e:
                results[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=FailureReason.PROVIDER_FAILURE,
                    error_message=str(e),
                    telemetry=envelope.telemetry
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
        
        # SOTA FIX: Instanciación genérica correcta.
        queue: 'asyncio.PriorityQueue[Tuple[int, int, TranslationUnit, PromptEnvelope]]' = asyncio.PriorityQueue()
        sequence_counter = itertools.count()
        outcomes_map: Dict[int, ChunkOutcome] = {} 
        
        for unit in units:
            # NADR-05 §5.1 R3: Unidades sin context_id reciben contexto vacío explícito.
            # Unidades con context_id acceden al resolver (fail-fast si no existe).
            if unit.context_id is None or unit.context_id == "":
                context = ResolvedContext(context_id="", breadcrumbs=())
            else:
                context = resolved_contexts[unit.context_id]

            build_result = self.prompt_builder.build(unit, resolved_context=context)
            
            # SOTA FIX: Discriminación Literal.
            if build_result.status == "failed":
                mapped_reason = BUDGET_TO_EXECUTION_FAILURE_MAP.get(
                    build_result.error_reason, 
                    FailureReason.UNKNOWN_ERROR
                )
                outcomes_map[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=mapped_reason,
                    error_message=build_result.message,
                    telemetry={"violation_reason": build_result.error_reason.value}
                )
                continue
                
            envelope = build_result.envelope
            req_window = envelope.telemetry.get("required_window", 0)
            
            if req_window > MAX_GLOBAL_SUPPORTED_WINDOW:
                outcomes_map[unit.chunk_index] = ChunkOutcome(
                    chunk_index=unit.chunk_index,
                    chunk_id=unit.chunk_id,
                    status=ExecutionStatus.FAILED,
                    original_payload_sha256=unit.payload_sha256,
                    translated_unit=None,
                    failure_reason=FailureReason.UNPROCESSABLE_ENTITY,
                    error_message=f"Rechazo Absoluto: required_window ({req_window}) excede la capacidad total ({MAX_GLOBAL_SUPPORTED_WINDOW}).",
                    telemetry={"target_provider": "rejected", "required_window": req_window}
                )
                continue
                
            cost_priority = -envelope.estimated_tokens
            seq_id = next(sequence_counter)
            queue.put_nowait((cost_priority, seq_id, unit, envelope))
            
        workers = [asyncio.create_task(self._worker(queue, outcomes_map)) for _ in range(self._concurrency)]
        
        try:
            await queue.join()
        finally:
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            
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
                    error_message="El Worker colapsó o fue cancelado antes de registrar el outcome.",
                    telemetry={"violation_reason": "worker_crash"}
                )
                
        final_outcomes_sorted = [outcomes_map[idx] for idx in sorted(outcomes_map.keys())]
        return DispatchResult(outcomes=final_outcomes_sorted)