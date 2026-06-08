# tests/unit/test_validation_pipeline.py
from typing import List
from core.validation.models import ValidationContext, Scope, Severity, ValidationResult
from core.validation.pipeline import ValidationPipeline

class MockPassValidator:
    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        return [ValidationResult(
            invariant_id="MOCK_PASS", 
            passed=True, 
            severity=Severity.INFO,
            message="ok", 
            context=context
        )]

class MockFailValidator:
    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        return [ValidationResult(
            invariant_id="MOCK_FAIL", 
            passed=False, 
            severity=Severity.HARD_FAIL,
            message="error", 
            context=context
        )]
def test_pipeline_runs_chunk_validators_only():
    pipeline = ValidationPipeline()
    pipeline.add_chunk_validator(MockPassValidator())
    pipeline.add_chunk_validator(MockFailValidator())
    pipeline.add_document_validator(MockFailValidator()) 
    
    ctx = ValidationContext(source_text="", target_text="", scope=Scope.CHUNK)
    results = pipeline.validate_chunk(ctx)
    
    assert len(results) == 2
    assert results[0].invariant_id == "MOCK_PASS"
    assert results[1].invariant_id == "MOCK_FAIL"

def test_pipeline_runs_document_validators_only():
    pipeline = ValidationPipeline()
    pipeline.add_chunk_validator(MockPassValidator())
    pipeline.add_document_validator(MockFailValidator())
    
    ctx = ValidationContext(source_text="", target_text="", scope=Scope.DOCUMENT)
    results = pipeline.validate_document(ctx)
    
    assert len(results) == 1
    assert results[0].invariant_id == "MOCK_FAIL"

def test_pipeline_preserves_registration_order():
    # Test de determinismo contractual del ADR-003
    pipeline = ValidationPipeline()
    pipeline.add_chunk_validator(MockPassValidator())
    pipeline.add_chunk_validator(MockFailValidator())
    
    ctx = ValidationContext(source_text="", target_text="", scope=Scope.CHUNK)
    results = pipeline.validate_chunk(ctx)
    
    assert [r.invariant_id for r in results] == ["MOCK_PASS", "MOCK_FAIL"]