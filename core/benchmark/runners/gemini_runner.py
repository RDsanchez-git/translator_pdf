import os
import time
import logging
import psutil
from typing import List

from core.benchmark.ports import BenchmarkRunnerProtocol, RunnerExecutionResult
from core.benchmark.models import (
    PreparedBenchmarkDataset, ChunkBenchmarkRecord, DocumentComplexity, 
    ProviderDescriptor, BenchmarkMode, QuotaSnapshot, HardwareTelemetry,
    TranslatedArtifact
)
from core.ast.models import ExecutionStatus, FailureReason

from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.dispatcher import AsyncDispatcher
from apps.bootstrap.provider_stack_factory import build_provider_stack
from apps.bootstrap.pipeline_factory import build_healing_pipeline
from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
from core.finops.measurement import InferenceMeasurementService
from core.metrics.pricing import PricingEngine
from core.benchmark.quality import FormalLatexSyntaxParser, FormalMarkdownTableParser
from core.context.context_registry import ContextRegistry
from core.context.dynamic_resolver import DynamicContextResolver

from core.validation.factory import build_validation_pipeline
from core.validation.estimators import ExactBPEEstimator


logger = logging.getLogger(__name__)


class GeminiBenchmarkRunner(BenchmarkRunnerProtocol):
    """SOTA: Ejecutor de carga pura para ecosistema Gemini."""
    
    def __init__(
        self, 
        descriptor: ProviderDescriptor, 
        mode: BenchmarkMode = BenchmarkMode.CAPABILITY,
        concurrency: int = 15
    ):
        self.descriptor = descriptor
        self.mode = mode
        self.concurrency = concurrency
        self._dispatcher = None
        self.warmup_time_seconds = 0.0
        self.quota_snapshot = None

    async def warmup(self) -> None:
        start_time = time.monotonic()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY no detectada.")

        # Gemini tiene ventana masiva nativa
        limit_to_use = 2097152

        estimator = ExactBPEEstimator()
        measurement_service = InferenceMeasurementService(estimator=estimator)
        
        budget_calculator = PromptBudgetCalculator(
            primary_window_limit=limit_to_use,
            fallback_window_limit=limit_to_use,
            min_output_reserve=256,
            max_output_reserve=8192
        )
        
        compression_policy = StandardCompressionPolicy()
        
        prompt_builder = PromptBuilder(
            model_name=self.descriptor.model, 
            prompt_version="v1.0", 
            measurement_service=measurement_service,
            budget_calculator=budget_calculator,
            compression_policy=compression_policy
        )

        rpm_limit = int(os.getenv("GEMINI_RPM_LIMIT", "360"))
        tpm_limit = int(os.getenv("GEMINI_TPM_LIMIT", "4000000"))
        
        self.quota_snapshot = QuotaSnapshot(rpm_limit=rpm_limit, tpm_limit=tpm_limit, concurrency=self.concurrency)
        
        # DF-28: Usar factory canónica con cache deshabilitado y Gemini como provider base.
        # El benchmark mide capacidad del modelo, no eficiencia del sistema.
        # CircuitBreaker es MANDATORY (NADR-08 §5.2 R7).
        provider_stack = await build_provider_stack(
            api_key=api_key,
            provider_type="gemini",  # ← Gemini como provider base
            rpm_limit=rpm_limit,
            tpm_limit=tpm_limit,
            cache_db_path=None,  # ← Sin cache (decisión metodológica)
        )
        
        # DF-28: Contexto real (NADR-05 §5.1 R1).
        context_registry = ContextRegistry()
        context_resolver = DynamicContextResolver(registry=context_registry)
        
        # DF-28: Reutilizar construcción canónica de validation + healing.
        validation_pipeline = build_validation_pipeline()
        healing_pipeline = build_healing_pipeline(validation_pipeline)

        self._dispatcher = AsyncDispatcher(
            context_resolver=context_resolver,
            prompt_builder=prompt_builder,
            provider_stack=provider_stack,
            validation_pipeline=validation_pipeline,
            healing_pipeline=healing_pipeline,
            concurrency=self.concurrency,
        )
        
        self.warmup_time_seconds = time.monotonic() - start_time
        logger.info(f"Gemini Stack inicializado en {self.warmup_time_seconds:.3f}s. Modo: {self.mode.value}.")

    async def execute_dataset(
        self, 
        dataset: PreparedBenchmarkDataset, 
        force_cache_bypass: bool = True
    ) -> RunnerExecutionResult:
        
        if not self._dispatcher:
            raise RuntimeError("El Runner debe inicializarse vía warmup().")

        start_time = time.monotonic()
        dispatch_result = await self._dispatcher.dispatch(dataset.prepared_units)
        makespan = time.monotonic() - start_time

        raw_records: List[ChunkBenchmarkRecord] = []

        for outcome in dispatch_result.outcomes:
            telemetry = outcome.telemetry or {}
            success = outcome.status == ExecutionStatus.SUCCESS
            
            complexity = dataset.unit_complexity_map.get(outcome.chunk_id, DocumentComplexity.MIXED_HYBRID)
            
            in_tokens = telemetry.get("input_tokens", 0)
            out_tokens = telemetry.get("output_tokens", 0)
            
            latency = telemetry.get("latency_ms", 0.0)
            tps_inst = round((in_tokens + out_tokens) / (latency / 1000.0), 2) if latency > 0 else 0.0
            
            is_local_rejection = (not success) and (latency == 0.0)
            execution_stage = "pre_network" if is_local_rejection else "post_network"
            
            model_used = outcome.translated_unit.model_name if outcome.translated_unit else self.descriptor.model
            cost = 0.0 if is_local_rejection else PricingEngine.calculate_cost(model_used, in_tokens, out_tokens)

            text_payload = ""
            if outcome.translated_unit and getattr(outcome.translated_unit, 'translated_payload', None):
                text_payload = outcome.translated_unit.translated_payload

            artifact_dto = None
            if success and text_payload:
                from core.shared.crypto import compute_sha256
                sha256_hash = compute_sha256(text_payload.encode('utf-8'))
                artifact_dto = TranslatedArtifact(
                    chunk_id=outcome.chunk_id,
                    translated_text=text_payload,
                    text_sha256=sha256_hash,
                    is_latex_valid=FormalLatexSyntaxParser.validate_syntax(text_payload),
                    is_markdown_valid=FormalMarkdownTableParser.validate_syntax(text_payload)
                )

            raw_records.append(
                ChunkBenchmarkRecord(
                    chunk_id=outcome.chunk_id,
                    chunk_index=outcome.chunk_index,
                    complexity=complexity,
                    tps_instantaneous=tps_inst,
                    latency_ms=latency,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    cost_usd=cost,
                    success=success,
                    failure_reason=outcome.failure_reason,
                    is_local_rejection=is_local_rejection,
                    execution_stage=execution_stage,
                    billing_model_used=model_used,
                    quota_wait_seconds=telemetry.get("quota_wait_seconds", 0.0),
                    quota_attempts=telemetry.get("quota_reservation_attempts", 1),
                    did_overflow=outcome.failure_reason == FailureReason.CONTEXT_OVERFLOW,
                    did_fallback=telemetry.get("target_provider") == "fallback_large_window",
                    compression_ratio_used=round(out_tokens / in_tokens, 4) if in_tokens > 0 else 1.0,
                    artifact_metadata=artifact_dto
                )
            )

        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        hw_telemetry = HardwareTelemetry(
            cpu_peak_percent=psutil.cpu_percent(interval=0.1),
            rss_peak_mb=round(mem_info.rss / (1024 * 1024), 2),
            rss_avg_mb=round(mem_info.rss / (1024 * 1024), 2),
            sampling_interval_ms=100
        )

        return RunnerExecutionResult(
            provider_id=self.descriptor.provider,
            raw_records=raw_records,
            document_completion_seconds=makespan,
            hardware_telemetry=hw_telemetry
        )

    async def teardown(self) -> None:
        self._dispatcher = None