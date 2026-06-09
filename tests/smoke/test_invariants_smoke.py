# tests/smoke/test_invariants_smoke.py
from core.validation.models import ValidationContext, Scope, Severity

def run_chunk_validation(pipeline, source: str, target: str):
    ctx = ValidationContext(source_text=source, target_text=target, scope=Scope.CHUNK)
    return pipeline.validate_chunk(ctx)

def run_doc_validation(pipeline, source: str, target: str):
    ctx = ValidationContext(source_text=source, target_text=target, scope=Scope.DOCUMENT)
    return pipeline.validate_document(ctx)

# ==============================================================================
# STRUCTURAL INVARIANTS (HARD_FAIL) - Evaluación por Familia
# ==============================================================================
def test_smoke_si01_unclosed_brace(reliability_pipeline):
    res = run_chunk_validation(reliability_pipeline, r"\textbf{text}", r"\textbf{text")
    # Aserción SOTA: Evalúa la familia formal y el descarte de la severidad
    assert any(r.invariant_family == "SI-01" and r.severity == Severity.HARD_FAIL for r in res)

def test_smoke_si02_unbalanced_math(reliability_pipeline):
    res = run_chunk_validation(reliability_pipeline, r"$$E=mc^2$$", r"$$E=mc^2$")
    assert any(r.invariant_family == "SI-02" and r.severity == Severity.HARD_FAIL for r in res)

def test_smoke_si03_unclosed_environment(reliability_pipeline):
    res = run_doc_validation(reliability_pipeline, r"\begin{matrix} 1 \end{matrix}", r"\begin{matrix} 1")
    assert any(r.invariant_family == "SI-03" and r.severity == Severity.HARD_FAIL for r in res)

# ==============================================================================
# PRESERVATION INVARIANTS (HARD_FAIL)
# ==============================================================================
def test_smoke_pi01_doi_alteration(reliability_pipeline):
    res = run_chunk_validation(reliability_pipeline, "Referencia DOI 10.1000/xyz123", "Referencia DOI 10.1000/abc999")
    assert any(r.invariant_id == "PI-01" and r.severity == Severity.HARD_FAIL for r in res)

def test_smoke_pi02_url_domain_alteration(reliability_pipeline):
    # Alteración inequívoca de dominio/path para evitar colisiones de DNS locales
    res = run_chunk_validation(reliability_pipeline, "Sitio web: https://ieee.org/Test", "Sitio web: https://springer.com/Test")
    assert any(r.invariant_id == "PI-02" and r.severity == Severity.HARD_FAIL for r in res)

def test_smoke_pi03_orcid_lost(reliability_pipeline):
    res = run_chunk_validation(reliability_pipeline, "Autor (ORCID 0000-0002-1825-0097)", "Autor (ORCID eliminado)")
    assert any(r.invariant_id == "PI-03" and r.severity == Severity.HARD_FAIL for r in res)

def test_smoke_pi04_cross_reference_lost(reliability_pipeline):
    res = run_doc_validation(reliability_pipeline, r"\cite{smith, jones}", r"\cite{smith}")
    assert any(r.invariant_id == "PI-04" and r.severity == Severity.HARD_FAIL for r in res)

# ==============================================================================
# PERIMETER INVARIANTS (HARD_FAIL)
# ==============================================================================
def test_smoke_pei01_markdown_block(reliability_pipeline):
    res = run_chunk_validation(reliability_pipeline, "Texto de origen limpio.", "```latex\nTexto de origen limpio.\n```")
    assert any(r.invariant_id == "PeI-01" and r.severity == Severity.HARD_FAIL for r in res)

def test_smoke_pei02_conversational_leak(reliability_pipeline):
    res = run_chunk_validation(reliability_pipeline, "El sistema de ecuaciones diverge.", "Sure, here's the translation:\nEl sistema de ecuaciones diverge.")
    assert any(r.invariant_id == "PeI-02" and r.severity == Severity.HARD_FAIL for r in res)

# ==============================================================================
# SEMANTIC INVARIANTS (WARNING)
# ==============================================================================
def test_smoke_sei01_missing_number(reliability_pipeline):
    res = run_chunk_validation(reliability_pipeline, "Lanzó el Error code 404 de inmediato.", "Lanzó el Error de inmediato.")
    assert any(r.invariant_id == "SeI-01" and r.severity == Severity.WARNING for r in res)

def test_smoke_sei02_unit_mutation(reliability_pipeline):
    res = run_chunk_validation(reliability_pipeline, "Un consumo total de 100 kW.", "Un consumo total de 100 MW.")
    assert any(r.invariant_id == "SeI-02" and r.severity == Severity.WARNING for r in res)

# ==============================================================================
# VOLUMETRIC INVARIANTS (WARNING)
# ==============================================================================
def test_smoke_vi01_ratio_contraction(reliability_pipeline):
    # Base > 20 caracteres para activar validación volumétrica
    base = "Este es un texto de origen que supera los veinte caracteres requeridos."
    res = run_chunk_validation(reliability_pipeline, base, "Corto.") 
    assert any(r.invariant_id == "VI-01" and r.severity == Severity.WARNING for r in res)

def test_smoke_vi01_ratio_expansion(reliability_pipeline):
    base = "Texto base suficiente."
    expanded = "Este es un texto traducido que artificialmente expande la prosa repitiendo ideas y rompiendo el umbral máximo de forma agresiva."
    res = run_chunk_validation(reliability_pipeline, base, expanded)
    assert any(r.invariant_id == "VI-01" and r.severity == Severity.WARNING for r in res)