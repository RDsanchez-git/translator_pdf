# tests/unit/test_preservation_validator.py
from core.validation.models import ValidationContext, Scope
from core.validation.preservation import PreservationValidator

def test_doi_case_insensitivity_is_preserved():
    validator = PreservationValidator()
    ctx = ValidationContext(
        source_text="Read 10.1000/ABC",
        target_text="Read 10.1000/abc",  # El LLM alteró el case legítimamente
        scope=Scope.CHUNK
    )
    results = validator.validate(ctx)
    assert not any(r.invariant_id == "PI-01" for r in results)  # Debe pasar limpio

def test_addbibresource_with_optional_arguments():
    validator = PreservationValidator()
    ctx = ValidationContext(
        source_text=r"\addbibresource{refs.bib}",
        target_text=r"\addbibresource[location=remote]{refs.bib}",  # Tolerancia estructural
        scope=Scope.DOCUMENT
    )
    results = validator.validate(ctx)
    assert not any(r.invariant_id == "PI-05" for r in results)

def test_modern_reference_commands():
    validator = PreservationValidator()
    ctx = ValidationContext(
        source_text=r"\nameref{sec:intro} and \vref{fig:data}",
        target_text=r"\nameref{sec:intro} and \vref{fig:data}",
        scope=Scope.DOCUMENT
    )
    results = validator.validate(ctx)
    assert not any(r.invariant_id == "PI-04" for r in results)