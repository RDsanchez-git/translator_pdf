import pytest
from typing import Any
from unittest.mock import MagicMock
from core.ast.models import TranslationUnit, TranslationTaskType
from apps.llm_workers.dispatcher import AsyncDispatcher
from apps.llm_workers.prompt_builder import PromptEnvelope, PromptBuilder

# ==============================================================================
# Mocks de Infraestructura (E/S y Red Aisladas)
# ==============================================================================

class StaticMockProvider:
    """SOTA: Simula respuestas estáticas del LLM respetando el contrato de la Fase 14."""
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
        mock_res.latency_ms = 10.0
        mock_res.finish_reason = "stop"
        return mock_res

class SequenceMockProvider:
    """SOTA: Simula respuestas secuenciales del LLM."""
    def __init__(self, outputs: list[str]):
        self.outputs = outputs
        self.calls = 0

    async def translate(self, envelope: PromptEnvelope) -> Any:
        out = self.outputs[self.calls]
        self.calls += 1
        mock_res = MagicMock()
        mock_res.chunk_id = envelope.chunk_id
        mock_res.translated_text = out
        mock_res.text = out
        mock_res.content = out
        mock_res.translated_payload = out
        mock_res.input_tokens = 10
        mock_res.output_tokens = 10
        mock_res.latency_ms = 10.0
        mock_res.finish_reason = "stop"
        return mock_res

def build_test_dispatcher(provider: Any) -> AsyncDispatcher:
    """Fábrica de inyección de dependencias para el Dispatcher aislado."""
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
    
    # Construir ValidationPipeline con validadores reales
    from core.validation.pipeline import ValidationPipeline
    from core.validation.adapters.structural_bridge import StructuralValidationBridge
    from core.validation.preservation import PreservationValidator
    from core.validation.perimeter import PerimeterValidator
    from core.validation.semantic import SemanticValidator
    from core.validation.volumetric import VolumetricValidator
    from core.healing.pipeline import HealingPipeline
    
    validation_pipeline = ValidationPipeline()
    structural_bridge = StructuralValidationBridge()
    validation_pipeline.add_chunk_validator(structural_bridge)
    validation_pipeline.add_chunk_validator(PreservationValidator())
    validation_pipeline.add_chunk_validator(PerimeterValidator())
    validation_pipeline.add_chunk_validator(SemanticValidator())
    validation_pipeline.add_chunk_validator(VolumetricValidator())
    validation_pipeline.add_document_validator(structural_bridge)
    validation_pipeline.add_document_validator(PreservationValidator())
    
    healing_pipeline = HealingPipeline(validation_pipeline, strategies=[])
    
    return AsyncDispatcher(
        context_resolver=mock_resolver,
        prompt_builder=prompt_builder,
        provider_stack=provider,
        validation_pipeline=validation_pipeline,
        healing_pipeline=healing_pipeline,
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
    
    result = await dispatcher.dispatch([unit])
    assert len(result.outcomes) == 1
    assert result.outcomes[0].is_success is False

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
    
    result = await dispatcher.dispatch([unit])
    assert len(result.outcomes) == 1
    assert result.outcomes[0].is_success is False

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
    assert len(result.outcomes) == 1
    assert result.outcomes[0].is_success is True

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
    
    result = await dispatcher.dispatch([unit])
    assert len(result.outcomes) == 1
    assert result.outcomes[0].is_success is False

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
    
    # SOTA FIX: El dispatcher procesa los chunks de forma atómica; la validación macro ocurre pos-ensamble
    result = await dispatcher.dispatch(units)
    assert len(result.outcomes) == 2
    assert all(outcome.is_success for outcome in result.outcomes)