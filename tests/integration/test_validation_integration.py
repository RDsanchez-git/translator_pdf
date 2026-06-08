# tests/integration/test_validation_integration.py
import pytest
from typing import Dict, Optional
from core.ast.models import TranslationUnit, TranslatedUnit
from apps.llm_workers.dispatcher import AsyncDispatcher
from apps.llm_workers.cache import SQLiteTranslationCache
from core.execution.exceptions import ChunkValidationError, DocumentValidationError

# ==============================================================================
# Mocks Locales de Infraestructura (E/S y Red Aisladas)
# ==============================================================================

class IntegrationMockCache(SQLiteTranslationCache):
    def __init__(self) -> None:
        self.store: Dict[str, str] = {}
        
    async def get(self, payload_sha256: str, model_name: str, prompt_version: str) -> Optional[str]:
        return self.store.get(payload_sha256)

    async def set(self, payload_sha256: str, model_name: str, prompt_version: str, translated_payload: str) -> None:
        self.store[payload_sha256] = translated_payload

class BaseMockWorker:
    """Clase base genérica para la integración"""
    async def translate(self, unit: TranslationUnit) -> TranslatedUnit:
        raise NotImplementedError

class IntegrationMockWorker(BaseMockWorker):
    def __init__(self, output_text: str):
        self.output_text = output_text

    async def translate(self, unit: TranslationUnit) -> TranslatedUnit:
        return TranslatedUnit(
            chunk_index=unit.chunk_index, chunk_id=unit.chunk_id, chunk_type=unit.chunk_type,
            source_sequence_range=unit.source_sequence_range, translated_payload=self.output_text,
            payload_sha256=unit.payload_sha256, model_name="mock_llm", prompt_version="1.0",
            input_tokens=10, output_tokens=10, latency_ms=10.0
        )

class SequenceMockWorker(BaseMockWorker):
    def __init__(self, outputs: list[str]):
        self.outputs = outputs
        self.calls = 0

    async def translate(self, unit: TranslationUnit) -> TranslatedUnit:
        out = self.outputs[self.calls]
        self.calls += 1
        return TranslatedUnit(
            chunk_index=unit.chunk_index, chunk_id=unit.chunk_id, chunk_type=unit.chunk_type,
            source_sequence_range=unit.source_sequence_range, translated_payload=out,
            payload_sha256=unit.payload_sha256, model_name="mock_llm", prompt_version="1.0",
            input_tokens=10, output_tokens=10, latency_ms=10.0
        )

# ==============================================================================
# Suite de Pruebas de Integración (End-to-End)
# ==============================================================================

@pytest.mark.anyio
async def test_integration_hard_fail_on_unbalanced_braces():
    worker = IntegrationMockWorker(output_text="{unbalanced brace")
    cache = IntegrationMockCache()
    dispatcher = AsyncDispatcher(worker, cache, "model", "v1")
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id1", chunk_type="translate",
        source_sequence_range=(1,2), node_count=1, reference_context="",
        target_payload="some source", estimated_tokens=5, payload_sha256="sha_brace"
    )
    
    with pytest.raises(ChunkValidationError) as exc:
        await dispatcher.dispatch([unit])

    # Corrección: Evaluación directa sobre el atributo del objeto
    assert exc.value.invariant_id == "UNBALANCED_BRACES_OPEN"
    assert "sha_brace" not in cache.store

@pytest.mark.anyio
async def test_integration_preservation_fail_on_missing_doi():
    worker = IntegrationMockWorker(output_text="Some text without DOI")
    cache = IntegrationMockCache()
    dispatcher = AsyncDispatcher(worker, cache, "model", "v1")
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id2", chunk_type="translate",
        source_sequence_range=(1,2), node_count=1, reference_context="",
        target_payload="Source with DOI 10.1000/xyz123",
        estimated_tokens=5, payload_sha256="sha_doi"
    )
    
    with pytest.raises(ChunkValidationError) as exc:
        await dispatcher.dispatch([unit])
        
    # Corrección: Evaluación directa sobre el atributo del objeto
    assert exc.value.invariant_id == "PI-01"
    assert "sha_doi" not in cache.store

@pytest.mark.anyio
async def test_integration_warning_does_not_block():
    worker = IntegrationMockWorker(output_text="El valor es")
    cache = IntegrationMockCache()
    dispatcher = AsyncDispatcher(worker, cache, "model", "v1")
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id3", chunk_type="translate",
        source_sequence_range=(1,2), node_count=1, reference_context="",
        target_payload="Error: 404",
        estimated_tokens=5, payload_sha256="sha_warn"
    )
    
    result = await dispatcher.dispatch([unit])
    assert len(result) == 1
    assert "sha_warn" in cache.store

@pytest.mark.anyio
async def test_integration_perimeter_fail_on_markdown():
    worker = IntegrationMockWorker(output_text="```latex\nE=mc^2\n```")
    cache = IntegrationMockCache()
    dispatcher = AsyncDispatcher(worker, cache, "model", "v1")
    
    unit = TranslationUnit(
        chunk_index=1, chunk_id="id4", chunk_type="translate",
        source_sequence_range=(1,2), node_count=1, reference_context="",
        target_payload="source text", estimated_tokens=5, payload_sha256="sha_mark"
    )
    
    with pytest.raises(ChunkValidationError) as exc:
        await dispatcher.dispatch([unit])
        
    # Corrección: Evaluación directa sobre el atributo del objeto
    assert exc.value.invariant_id == "PeI-01"
    assert "sha_mark" not in cache.store

@pytest.mark.anyio
async def test_integration_document_level_pi04_fail():
    worker = SequenceMockWorker([
        r"\label{sec1}",
        r"\ref{sec2}"
    ])
    cache = IntegrationMockCache()
    dispatcher = AsyncDispatcher(worker, cache, "model", "v1")
    
    units = [
        TranslationUnit(
            chunk_index=1, chunk_id="id_lbl", chunk_type="translate", source_sequence_range=(1,1),
            node_count=1, reference_context="", target_payload=r"\label{sec1}", 
            estimated_tokens=5, payload_sha256="sha_L1"
        ),
        TranslationUnit(
            chunk_index=2, chunk_id="id_ref", chunk_type="translate", source_sequence_range=(2,2),
            node_count=1, reference_context="", target_payload=r"\ref{sec1}", 
            estimated_tokens=5, payload_sha256="sha_R1"
        )
    ]
    
    with pytest.raises(DocumentValidationError) as exc:
        await dispatcher.dispatch(units)
        
    # Corrección: Aserción desacoplada del stringificador por contrato unificado
    assert exc.value.invariant_id == "PI-04"