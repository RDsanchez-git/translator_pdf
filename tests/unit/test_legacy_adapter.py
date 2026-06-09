# tests/unit/test_legacy_adapter.py
import pytest
from core.validation.models import Severity, Scope, ValidationContext
from core.validation.legacy_adapter import LegacyValidatorAdapter, UnknownLegacyValidationCodeError
from core.execution.models import ValidationError

class DummyLegacyValid:
    @classmethod
    def validate(cls, text: str):
        return [ValidationError(code="RESIDUAL_HTML", message="Trace error")]

class DummyLegacyInvalid:
    @classmethod
    def validate(cls, text: str):
        return [ValidationError(code="UNKNOWN_CODE", message="Fatal unmapped token")]

def test_adapter_converts_error_to_validation_result():
    severity_map = {"RESIDUAL_HTML": Severity.WARNING}
    adapter = LegacyValidatorAdapter(DummyLegacyValid, severity_map)
    ctx = ValidationContext(source_text="src", target_text="tgt", scope=Scope.CHUNK)
    
    results = adapter.validate(ctx)
    
    assert len(results) == 1
    assert results[0].invariant_id == "RESIDUAL_HTML"
    assert results[0].invariant_family == "SI-04"
    assert results[0].passed is False
    assert results[0].severity == Severity.WARNING
    assert results[0].context is ctx

def test_adapter_default_severity_hard_fail():
    adapter = LegacyValidatorAdapter(DummyLegacyValid, severity_map={})
    ctx = ValidationContext(source_text="", target_text="", scope=Scope.CHUNK)
    
    results = adapter.validate(ctx)
    assert results[0].severity == Severity.HARD_FAIL

def test_adapter_unknown_code_raises_domain_exception():
    adapter = LegacyValidatorAdapter(DummyLegacyInvalid, severity_map={})
    ctx = ValidationContext(source_text="", target_text="", scope=Scope.CHUNK)
    
    # Certifica la estrategia Fail-Fast ante códigos corruptos o no registrados
    with pytest.raises(UnknownLegacyValidationCodeError):
        adapter.validate(ctx)