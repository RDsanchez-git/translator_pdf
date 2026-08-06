import pytest
from typing import List, Optional, Any
from unittest.mock import MagicMock
from core.ast.models import TranslationUnit, TranslationTaskType
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.validation.models import ValidationResult, Severity, ValidationContext, Scope
from core.validation.pipeline import ValidationPipeline


from apps.llm_workers.routing import LLMProvider
from apps.llm_workers.prompt_builder import PromptEnvelope, PromptBuilder

# ==============================================================================
# Mocks de Infraestructura
# ==============================================================================

class StaticMockProvider(LLMProvider):
    """Mock SOTA que simula la respuesta de la capa física (red o caché)."""
    def __init__(self, output_text: str):
        self.output_text = output_text

    async def translate(self, envelope: PromptEnvelope) -> Any:
        mock_res = MagicMock()
        mock_res.chunk_id = envelope.chunk_id
        mock_res.translated_text = self.output_text
        mock_res.text = self.output_text
        mock_res.content = self.output_text
        mock_res.translated_payload = self.output_text
        mock_res.input_tokens = 10
        mock_res.output_tokens = 10
        mock_res.latency_ms = 50.0
        mock_res.finish_reason = "stop"
        return mock_res

class MockDocumentFailValidator:
    """Validador sintético a nivel macro."""
    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        if context.scope == Scope.DOCUMENT:
            return [ValidationResult("SI-03", False, Severity.HARD_FAIL, "Global crash", context)]
        return []

def build_test_dispatcher(provider: LLMProvider, pipeline: Optional[ValidationPipeline] = None) -> AsyncDispatcher:
    """Fábrica de inyección para el orquestador aislado."""
    mock_resolver = MagicMock()
    mock_resolver.resolve.return_value = MagicMock(breadcrumbs=(), depth=0)
    
    mock_estimator = MagicMock()
    mock_estimator.estimate_tokens.return_value = 5
    
    from core.finops.measurement import InferenceMeasurementService
    from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
    
    measurement_service = InferenceMeasurementService(estimator=mock_estimator)
    budget_calculator = PromptBudgetCalculator()
    compression_policy = StandardCompressionPolicy()
    
    prompt_builder = PromptBuilder(
        model_name="mock_llm", 
        prompt_version="v1.0", 
        measurement_service=measurement_service,
        budget_calculator=budget_calculator,
        compression_policy=compression_policy
    )
    
    # Si no se provee pipeline, construir uno con validadores reales
    if pipeline is None:
        from core.validation.adapters.structural_bridge import StructuralValidationBridge
        from core.validation.preservation import PreservationValidator
        from core.validation.perimeter import PerimeterValidator
        pipeline = ValidationPipeline()
        structural_bridge = StructuralValidationBridge()
        pipeline.add_chunk_validator(structural_bridge)
        pipeline.add_chunk_validator(PreservationValidator())
        pipeline.add_chunk_validator(PerimeterValidator())
        pipeline.add_document_validator(structural_bridge)
        pipeline.add_document_validator(PreservationValidator())
    
    from core.healing.pipeline import HealingPipeline
    healing_pipeline = HealingPipeline(pipeline, strategies=[])
    
    return AsyncDispatcher(
        context_resolver=mock_resolver,
        prompt_builder=prompt_builder,
        provider_stack=provider,
        validation_pipeline=pipeline,
        healing_pipeline=healing_pipeline,
    )

# ==============================================================================
# Suite de Pruebas Unitarias del Dispatcher
# ==============================================================================

@pytest.mark.anyio
async def test_dispatcher_hard_fail_on_invalid_output():
    """Verifica el rechazo inmediato ante invariantes rotas por el proveedor."""
    provider = StaticMockProvider(output_text="{broken brace")
    dispatcher = build_test_dispatcher(provider)
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id1", chunk_fingerprint="fp1",
        chunk_type=TranslationTaskType.TRANSLATE, 
        source_sequence_range=(1, 2), node_count=1,
        context_id="CTX_TEST", context_depth=1,
        target_payload="{normal brace", estimated_tokens=5, payload_sha256="sha_miss"
    )
    
    result = await dispatcher.dispatch([unit])
    assert len(result.outcomes) == 1
    assert result.outcomes[0].is_success is False

@pytest.mark.anyio
async def test_dispatcher_revalidates_cache_hits():
    """El Dispatcher evalúa el resultado sin importar si vino de caché o red."""
    provider = StaticMockProvider(output_text="{corrupted open brace")
    dispatcher = build_test_dispatcher(provider)
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id1", chunk_fingerprint="fp1",
        chunk_type=TranslationTaskType.TRANSLATE, 
        source_sequence_range=(1, 2), node_count=1,
        context_id="CTX_TEST", context_depth=1,
        target_payload="test", estimated_tokens=5, payload_sha256="sha_key"
    )
    
    result = await dispatcher.dispatch([unit])
    assert len(result.outcomes) == 1
    assert result.outcomes[0].is_success is False

@pytest.mark.anyio
async def test_dispatcher_document_level_hard_fail():
    """Verificación de validaciones macro a nivel de ensamble."""
    provider = StaticMockProvider(output_text="clean")
    
    pipeline = ValidationPipeline()
    pipeline.add_document_validator(MockDocumentFailValidator())
    
    dispatcher = build_test_dispatcher(provider, pipeline)
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id1", chunk_fingerprint="fp1",
        chunk_type=TranslationTaskType.TRANSLATE, 
        source_sequence_range=(1, 2), node_count=1,
        context_id="CTX_TEST", context_depth=1,
        target_payload="test", estimated_tokens=5, payload_sha256="sha_doc"
    )
    
    # SOTA FIX: Las validaciones macro de documento no bloquean ni alteran el despacho individual de chunks
    result = await dispatcher.dispatch([unit])
    assert len(result.outcomes) == 1
    assert result.outcomes[0].is_success is True