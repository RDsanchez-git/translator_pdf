import pytest
from typing import List, Optional
from unittest.mock import MagicMock
from core.ast.models import TranslationUnit, TranslationTaskType
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.execution.exceptions import ChunkValidationError, DocumentValidationError
from core.validation.models import ValidationResult, Severity, ValidationContext, Scope
from core.validation.pipeline import ValidationPipeline

# SOTA: Contratos de la Fase 14
from apps.llm_workers.routing import LLMProvider, ProviderResult
from apps.llm_workers.prompt_builder import PromptEnvelope, PromptBuilder


# ==============================================================================
# Mocks de Infraestructura
# ==============================================================================

class StaticMockProvider(LLMProvider):
    """Mock SOTA que simula la respuesta de la capa física (red o caché)."""
    def __init__(self, output_text: str):
        self.output_text = output_text

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        return ProviderResult(
            chunk_id=envelope.chunk_id,
            translated_text=self.output_text,
            input_tokens=10,
            output_tokens=10,
            latency_ms=50.0,
            finish_reason="stop"
        )

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
    mock_estimator.estimate.return_value = 5
    prompt_builder = PromptBuilder(model_name="mock_llm", prompt_version="v1.0", estimator=mock_estimator)
    
    return AsyncDispatcher(
        context_resolver=mock_resolver,
        prompt_builder=prompt_builder,
        provider_stack=provider,
        validation_pipeline=pipeline
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
    
    with pytest.raises(ChunkValidationError):
        await dispatcher.dispatch([unit])

@pytest.mark.anyio
async def test_dispatcher_revalidates_cache_hits():
    """El Dispatcher evalúa el resultado sin importar si vino de caché o red."""
    # SOTA: Simulamos un hit de caché inyectando un texto corrupto directamente
    provider = StaticMockProvider(output_text="{corrupted open brace")
    dispatcher = build_test_dispatcher(provider)
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id1", chunk_fingerprint="fp1",
        chunk_type=TranslationTaskType.TRANSLATE, 
        source_sequence_range=(1, 2), node_count=1,
        context_id="CTX_TEST", context_depth=1,
        target_payload="test", estimated_tokens=5, payload_sha256="sha_key"
    )
    
    with pytest.raises(ChunkValidationError):
        await dispatcher.dispatch([unit])

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
    
    with pytest.raises(DocumentValidationError):
        await dispatcher.dispatch([unit])