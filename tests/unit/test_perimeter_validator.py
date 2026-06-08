# tests/unit/test_perimeter_validator.py
from core.validation.models import ValidationContext, Scope
from core.validation.perimeter import PerimeterValidator

def test_markdown_block_detected():
    validator = PerimeterValidator()
    ctx = ValidationContext(source_text="", target_text="```latex\n\\begin{equation}\n```", scope=Scope.CHUNK)
    results = validator.validate(ctx)
    assert any(r.invariant_id == "PeI-01" and not r.passed for r in results)

def test_conversational_leak_with_leading_whitespace_detected():
    validator = PerimeterValidator()
    ctx = ValidationContext(source_text="", target_text="\n\n  Claro, aquí tienes la traducción:", scope=Scope.CHUNK)
    results = validator.validate(ctx)
    assert any(r.invariant_id == "PeI-02" and not r.passed for r in results)

def test_extended_conversational_leak_detected():
    validator = PerimeterValidator()
    leaks = [
        "Traducción:\nEl modelo de lenguaje...",
        "Below is the translation:\n\n\\section{Intro}",
        "  Certainly! Here is the text:",
        "Resultado: El ensayo demuestra..."
    ]
    for leak in leaks:
        ctx = ValidationContext(source_text="", target_text=leak, scope=Scope.CHUNK)
        results = validator.validate(ctx)
        assert any(r.invariant_id == "PeI-02" for r in results), f"Falló en detectar fuga: {leak}"

def test_technical_prose_prefixes_pass_successfully():
    validator = PerimeterValidator()
    texts = [
        "Nota: El espacio de Hilbert es separable.",
        "Importante: Se asume consistencia de rangos.",
        "Como se demostró en la sección anterior, el operador es acotado."
    ]
    for text in texts:
        ctx = ValidationContext(source_text="", target_text=text, scope=Scope.CHUNK)
        results = validator.validate(ctx)
        assert len(results) == 0

def test_clean_translation_payload_passes():
    validator = PerimeterValidator()
    ctx = ValidationContext(source_text="", target_text="El vector de estado inicializa en cero.", scope=Scope.CHUNK)
    results = validator.validate(ctx)
    assert len(results) == 0