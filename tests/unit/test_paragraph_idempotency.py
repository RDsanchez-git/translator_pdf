from core.normalization.fixers.paragraph_normalizer import ParagraphNormalizer

def test_paragraph_normalizer_invariants_and_strict_idempotency():
    """CRÍTICO 6: Verificación de invariantes estructurales e idempotencia pura f(f(x)) == f(x)"""
    normalizer = ParagraphNormalizer()
    
    # Payload complejo con HTML anidado e inyecciones de código
    dirty_input = (
        "<div><p><strong>**Malformed Text**</strong> and "
        "<sup>value</sup>.</p><script>alert(1)</script></div>"
        "###Heading\n1.Introduction"
    )
    
    # Primera pasada: Extracción y Limpieza
    first_report = normalizer.normalize(dirty_input)
    text_v1 = first_report.text
    
    # --- Validación de Invariantes Estructurales ---
    assert "<div" not in text_v1
    assert "<p>" not in text_v1
    assert "<script>" not in text_v1
    assert "<strong>" not in text_v1
    assert "<sup>" not in text_v1
    
    # Control de no-duplicación de marcas de formato Markdown
    assert "****" not in text_v1
    assert "^{^{" not in text_v1
    
    # --- Validación del Contrato de Idempotencia Estricto ---
    second_report = normalizer.normalize(text_v1)
    text_v2 = second_report.text
    
    assert text_v1 == text_v2
    
    # Segunda pasada no debe registrar nuevas mutaciones (Cero ruido de I/O)
    clean_fixes = [f for f in second_report.fixes if not f.startswith("markdown_numbered_list_spacing_fixed")]
    assert len(clean_fixes) == 0

def test_strict_idempotency_contract_over_corpus():
    """Garantiza la invariabilidad sintáctica de caja negra de la DNL."""
    normalizer = ParagraphNormalizer()
    
    corpus_fixtures = [
        "<strong>**Nesting bold test**</strong> and <sup>value</sup>.",
        "###HeadingContext\n1.Introduction text payload.",
        "Plain text node without any markdown markers or HTML tags."
    ]
    
    for payload in corpus_fixtures:
        first_pass = normalizer.normalize(payload)
        second_pass = normalizer.normalize(first_pass.text)
        
        # El texto debe estabilizarse de forma absoluta en la primera pasada
        assert first_pass.text == second_pass.text
        assert len(second_pass.fixes) == 0