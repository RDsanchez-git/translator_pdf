import pytest
from core.ast.models import ASTNode, ContentNodeType
from core.normalization.enrichers.context_enricher import HierarchicalContextEnricher

@pytest.fixture
def enricher():
    return HierarchicalContextEnricher()

def test_homonym_section_isolation(enricher):
    """SOTA TEST: Comprueba que dos secciones con textos idénticos generen contextos únicos."""
    nodes = [
        # Capítulo 1
        ASTNode(node_id="heading_ch1_method", type=ContentNodeType.HEADING, content="# Methodology", metadata={"heading_level": 1}),
        ASTNode(node_id="p1", type=ContentNodeType.PARAGRAPH, content="Text under chapter 1 methodology."),
        
        # Capítulo 2
        ASTNode(node_id="heading_ch2_method", type=ContentNodeType.HEADING, content="# Methodology", metadata={"heading_level": 1}),
        ASTNode(node_id="p2", type=ContentNodeType.PARAGRAPH, content="Text under chapter 2 methodology.")
    ]
    
    enriched, registry, _, _ = enricher.enrich_document(nodes)
    
    ctx_id_p1 = enriched[1].control_plane["context_id"]
    ctx_id_p2 = enriched[3].control_plane["context_id"]
    
    # Prueba de fuego: Deben ser estrictamente distintos debido al aislamiento relacional
    assert ctx_id_p1 != ctx_id_p2
    
    # El registro estructurado debe mapear ambos preservando la resolución semántica
    assert registry["mappings"][ctx_id_p1] == [{"level": 1, "title": "Methodology"}]
    assert registry["mappings"][ctx_id_p2] == [{"level": 1, "title": "Methodology"}]
    assert registry["schema_version"] == "1.0.1"

def test_no_context_document_warning(enricher):
    """Verifica la emisión de alertas globales de telemetría INFO cuando el documento carece de títulos."""
    nodes = [
        ASTNode(node_id="p1", type=ContentNodeType.PARAGRAPH, content="Flat text document without layout hierarchy.")
    ]
    _, _, warnings, _ = enricher.enrich_document(nodes)
    assert any(w.severity == "INFO" and "NO_CONTEXT_DOCUMENT" in w.message for w in warnings)