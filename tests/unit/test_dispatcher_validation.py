# tests/unit/test_dispatcher_validation.py
import pytest
from typing import Dict, List, Optional
from core.ast.models import TranslationUnit, TranslatedUnit
from apps.llm_workers.dispatcher import AsyncDispatcher
from apps.llm_workers.cache import SQLiteTranslationCache
from core.execution.exceptions import ChunkValidationError, DocumentValidationError
from core.validation.models import ValidationResult, Severity, ValidationContext, Scope
from core.validation.pipeline import ValidationPipeline

class MockWorker:
    def __init__(self, output_text: str):
        self.output_text = output_text

    async def translate(self, unit: TranslationUnit) -> TranslatedUnit:
        return TranslatedUnit(
            chunk_index=unit.chunk_index, 
            chunk_id=unit.chunk_id, 
            chunk_type=unit.chunk_type,
            source_sequence_range=unit.source_sequence_range, 
            translated_payload=self.output_text,
            payload_sha256=unit.payload_sha256, 
            model_name="mock", 
            prompt_version="1.0",
            input_tokens=10, 
            output_tokens=10, 
            latency_ms=50.0
        )

class MockCache(SQLiteTranslationCache):
    """SOTA: Hereda nominalmente para Pylance, anulando la conexión real a disco."""
    def __init__(self, initial_data: Optional[str] = None) -> None:
        self.store: Dict[str, str] = {}
        if initial_data:
            self.store["sha_key"] = initial_data

    async def get(self, payload_sha256: str, model_name: str, prompt_version: str) -> Optional[str]:
        return self.store.get(payload_sha256)

    async def set(self, payload_sha256: str, model_name: str, prompt_version: str, translated_payload: str) -> None:
        self.store[payload_sha256] = translated_payload

class MockDocumentFailValidator:
    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        if context.scope == Scope.DOCUMENT:
            return [ValidationResult("SI-03", False, Severity.HARD_FAIL, "Global crash", context)]
        return []

@pytest.mark.anyio
async def test_dispatcher_hard_fail_prevents_cache_storage():
    worker = MockWorker(output_text="{broken brace")
    cache = MockCache()
    dispatcher = AsyncDispatcher(worker, cache, "model", "v1")
    
    unit = TranslationUnit(
        chunk_index=1, 
        chunk_id="id1", 
        chunk_type="translate", 
        source_sequence_range=(1, 2),
        node_count=1,  # Corrección: Parámetro contractual obligatorio
        reference_context="", 
        target_payload="{normal brace", 
        estimated_tokens=5, 
        payload_sha256="sha_miss"
    )
    
    with pytest.raises(ChunkValidationError):
        await dispatcher.dispatch([unit])
        
    assert "sha_miss" not in cache.store

@pytest.mark.anyio
async def test_dispatcher_revalidates_cache_hits():
    worker = MockWorker(output_text="clean")
    cache = MockCache(initial_data="{corrupted open brace")
    dispatcher = AsyncDispatcher(worker, cache, "model", "v1")
    
    unit = TranslationUnit(
        chunk_index=1, 
        chunk_id="id1", 
        chunk_type="translate", 
        source_sequence_range=(1, 2),
        node_count=1,  # Corrección: Parámetro contractual obligatorio
        reference_context="", 
        target_payload="test", 
        estimated_tokens=5, 
        payload_sha256="sha_key"
    )
    
    with pytest.raises(ChunkValidationError):
        await dispatcher.dispatch([unit])

@pytest.mark.anyio
async def test_dispatcher_document_level_hard_fail():
    worker = MockWorker(output_text="clean")
    cache = MockCache()
    
    pipeline = ValidationPipeline()
    pipeline.add_document_validator(MockDocumentFailValidator())
    
    dispatcher = AsyncDispatcher(worker, cache, "model", "v1", validation_pipeline=pipeline)
    unit = TranslationUnit(
        chunk_index=1, 
        chunk_id="id1", 
        chunk_type="translate", 
        source_sequence_range=(1, 2),
        node_count=1,  # Corrección: Parámetro contractual obligatorio
        reference_context="", 
        target_payload="test", 
        estimated_tokens=5, 
        payload_sha256="sha_doc"
    )
    
    with pytest.raises(DocumentValidationError):
        await dispatcher.dispatch([unit])