# tests/unit/test_semantic_validator.py
from core.validation.models import ValidationContext, Scope
from core.validation.semantic import SemanticValidator

def test_number_cardinality_mismatch_exact_content():
    validator = SemanticValidator()
    ctx = ValidationContext(
        source_text="Values are 50, 50, 50",
        target_text="Los valores son 50 y 50",
        scope=Scope.CHUNK
    )
    results = validator.validate(ctx)
    assert len(results) == 1
    assert results[0].invariant_id == "SeI-01"
    # Evalúa que exactamente falte un '50'
    assert "Faltan: ['50']" in results[0].message

def test_ip_address_not_parsed_as_number():
    validator = SemanticValidator()
    ctx = ValidationContext(
        source_text="IP 192.168.1.1",
        target_text="IP 192.168.1.1",
        scope=Scope.CHUNK
    )
    # Si capturara 168.1.1 fallaría por mismatch fraccional. Debe pasar limpio.
    results = validator.validate(ctx)
    assert len(results) == 0

def test_complex_scientific_units_exact_content():
    validator = SemanticValidator()
    ctx = ValidationContext(
        source_text="Density: 1.5 kg/m³, Speed: 299 m/s",
        target_text="Densidad: 1.5, Velocidad: 299 m/s",
        scope=Scope.CHUNK
    )
    results = validator.validate(ctx)
    assert len(results) == 1
    assert results[0].invariant_id == "SeI-02"
    # Evalúa que capture exactamente la unidad compuesta perdida
    assert "kg/m³" in results[0].message

def test_unit_case_sensitivity_kelvin_vs_kilo():
    validator = SemanticValidator()
    ctx = ValidationContext(
        source_text="The threshold is 300 K",
        target_text="El umbral es 300 k",
        scope=Scope.CHUNK
    )
    results = validator.validate(ctx)
    assert len(results) == 1
    assert "['K']" in results[0].message