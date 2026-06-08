# tests/unit/test_legacy_adapter.py
from core.validation.models import Severity, Scope, ValidationContext
from core.validation.legacy_adapter import LegacyValidatorAdapter
from core.execution.models import ValidationError

class DummyLegacy:
    @classmethod
    def validate(cls, text: str):
        return [ValidationError(code="DUMMY_CODE", message="Trace error")]

def test_adapter_converts_error_to_validation_result():
    severity_map = {"DUMMY_CODE": Severity.WARNING}
    adapter = LegacyValidatorAdapter(DummyLegacy, severity_map)
    ctx = ValidationContext(source_text="src", target_text="tgt", scope=Scope.CHUNK)
    
    results = adapter.validate(ctx)
    
    assert len(results) == 1
    assert results[0].invariant_id == "DUMMY_CODE"
    assert results[0].passed is False
    assert results[0].severity == Severity.WARNING
    assert results[0].context is ctx

def test_adapter_default_severity_hard_fail():
    adapter = LegacyValidatorAdapter(DummyLegacy, severity_map={})
    ctx = ValidationContext(source_text="", target_text="", scope=Scope.CHUNK)
    
    results = adapter.validate(ctx)
    assert results[0].severity == Severity.HARD_FAIL

def test_adapter_unknown_code_defaults_hard_fail():
    # Test de Fallback con mapa poblado pero código inexistente
    adapter = LegacyValidatorAdapter(DummyLegacy, severity_map={"OTHER_CODE": Severity.INFO})
    ctx = ValidationContext(source_text="", target_text="", scope=Scope.CHUNK)
    
    results = adapter.validate(ctx)
    assert results[0].severity == Severity.HARD_FAIL