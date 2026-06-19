import pytest
from unittest.mock import MagicMock
from core.ast.models import TranslationUnit, TranslationTaskType
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.execution.exceptions import ChunkValidationError, DocumentValidationError

# SOTA: Importaciones de los contratos del Provider Stack (Fase 14)
from apps.llm_workers.routing import LLMProvider, ProviderResult
from apps.llm_workers.prompt_builder import PromptEnvelope, PromptBuilder

# ==============================================================================
# Mocks de Infraestructura (E/S y Red Aisladas)
# ==============================================================================

class StaticMockProvider(LLMProvider):
    """SOTA: Simula respuestas estáticas del LLM respetando el contrato de la Fase 14."""
    def __init__(self, output_text: str):
        self.output_text = output_text

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        return ProviderResult(
            chunk_id=envelope.chunk_id,
            translated_text=self.output_text,
            input_tokens=10,
            output_tokens=10,
            latency_ms=10.0,
            finish_reason="stop"
        )

class SequenceMockProvider(LLMProvider):
    """SOTA: Simula respuestas secuenciales del LLM."""
    def __init__(self, outputs: list[str]):
        self.outputs = outputs
        self.calls = 0

    async def translate(self, envelope: PromptEnvelope) -> ProviderResult:
        out = self.outputs[self.calls]
        self.calls += 1
        return ProviderResult(
            chunk_id=envelope.chunk_id,
            translated_text=out,
            input_tokens=10,
            output_tokens=10,
            latency_ms=10.0,
            finish_reason="stop"
        )

def build_test_dispatcher(provider: LLMProvider) -> AsyncDispatcher:
    """Fábrica de inyección de dependencias para el Dispatcher aislado."""
    mock_resolver = MagicMock()
    mock_resolver.resolve.return_value = MagicMock(breadcrumbs=(), depth=0)
    
    mock_estimator = MagicMock()
    mock_estimator.estimate.return_value = 5
    prompt_builder = PromptBuilder(model_name="mock_llm", prompt_version="v1.0", estimator=mock_estimator)
    
    return AsyncDispatcher(
        context_resolver=mock_resolver,
        prompt_builder=prompt_builder,
        provider_stack=provider
    )

# ==============================================================================
# Suite de Pruebas de Integración (End-to-End)
# ==============================================================================

@pytest.mark.anyio
async def test_integration_hard_fail_on_unbalanced_braces():
    provider = StaticMockProvider(output_text="{unbalanced brace")
    dispatcher = build_test_dispatcher(provider)
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id1", chunk_fingerprint="fp1",
        chunk_type=TranslationTaskType.TRANSLATE,
        source_sequence_range=(1,2), node_count=1, 
        context_id="CTX_TEST", context_depth=1,
        target_payload="some source", estimated_tokens=5, payload_sha256="sha_brace"
    )
    
    with pytest.raises(ChunkValidationError) as exc:
        await dispatcher.dispatch([unit])

    assert exc.value.invariant_id == "UNBALANCED_BRACES_OPEN"

@pytest.mark.anyio
async def test_integration_preservation_fail_on_missing_doi():
    provider = StaticMockProvider(output_text="Some text without DOI")
    dispatcher = build_test_dispatcher(provider)
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id2", chunk_fingerprint="fp2",
        chunk_type=TranslationTaskType.TRANSLATE,
        source_sequence_range=(1,2), node_count=1, 
        context_id="CTX_TEST", context_depth=1,
        target_payload="Source with DOI 10.1000/xyz123",
        estimated_tokens=5, payload_sha256="sha_doi"
    )
    
    with pytest.raises(ChunkValidationError) as exc:
        await dispatcher.dispatch([unit])
        
    assert exc.value.invariant_id == "PI-01"

@pytest.mark.anyio
async def test_integration_warning_does_not_block():
    provider = StaticMockProvider(output_text="El valor es")
    dispatcher = build_test_dispatcher(provider)
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id3", chunk_fingerprint="fp3",
        chunk_type=TranslationTaskType.TRANSLATE,
        source_sequence_range=(1,2), node_count=1, 
        context_id="CTX_TEST", context_depth=1,
        target_payload="Error: 404",
        estimated_tokens=5, payload_sha256="sha_warn"
    )
    
    result = await dispatcher.dispatch([unit])
    assert len(result) == 1

@pytest.mark.anyio
async def test_integration_perimeter_fail_on_markdown():
    provider = StaticMockProvider(output_text="```latex\nE=mc^2\n```")
    dispatcher = build_test_dispatcher(provider)
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id4", chunk_fingerprint="fp4",
        chunk_type=TranslationTaskType.TRANSLATE,
        source_sequence_range=(1,2), node_count=1, 
        context_id="CTX_TEST", context_depth=1,
        target_payload="source text", estimated_tokens=5, payload_sha256="sha_mark"
    )
    
    with pytest.raises(ChunkValidationError) as exc:
        await dispatcher.dispatch([unit])
        
    assert exc.value.invariant_id == "PeI-01"

@pytest.mark.anyio
async def test_integration_document_level_pi04_fail():
    provider = SequenceMockProvider([
        r"\label{sec1}",
        r"\ref{sec2}"
    ])
    dispatcher = build_test_dispatcher(provider)
    
    units = [
        TranslationUnit(
            chunk_index=1, chunk_id="id_lbl", chunk_fingerprint="fp_lbl",
            chunk_type=TranslationTaskType.TRANSLATE, source_sequence_range=(1,1),
            node_count=1, context_id="CTX_TEST", context_depth=1, 
            target_payload=r"\label{sec1}", 
            estimated_tokens=5, payload_sha256="sha_L1"
        ),
        TranslationUnit(
            chunk_index=2, chunk_id="id_ref", chunk_fingerprint="fp_ref",
            chunk_type=TranslationTaskType.TRANSLATE, source_sequence_range=(2,2),
            node_count=1, context_id="CTX_TEST", context_depth=1, 
            target_payload=r"\ref{sec1}", 
            estimated_tokens=5, payload_sha256="sha_R1"
        )
    ]
    
    with pytest.raises(DocumentValidationError) as exc:
        await dispatcher.dispatch(units)
        
    assert exc.value.invariant_id == "PI-04"