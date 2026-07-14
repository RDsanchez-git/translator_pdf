import pytest
from core.ast.models import ASTNode, ParagraphPayload
from core.ast.enums import ContentNodeType
from core.normalization.classifier import SemanticNodeClassifier

@pytest.fixture
def classifier():
    return SemanticNodeClassifier(minimum_score=6)

def test_academic_pdf_greek_mix_reclassification(classifier):
    """Test 1: Valida el comportamiento con prosa académica real mezclada con símbolos griegos."""
    text = "The function \u03B1_i + \u03B2_j = \u03B3_ij is introduced in this section."
    node = ASTNode(node_id="node_1", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content=text), control_plane={})
    processed = classifier.classify_node(node)
    assert processed.node_type == ContentNodeType.INLINE_EQUATION
    assert processed.control_plane["classifier_reason"] == "weighted_heuristic_score"

def test_financial_false_positive_immunity(classifier):
    """Test 2: Valida la exclusión estricta de reportes financieros y numéricos puros."""
    text = "Revenue = 365M\nGrowth +15%\nQ1-Q4"
    node = ASTNode(node_id="node_2", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content=text), control_plane={})
    processed = classifier.classify_node(node)
    assert processed.node_type == ContentNodeType.PARAGRAPH

def test_financial_noise_with_many_operators(classifier):
    """Mejora 2: Desafía el filtro financiero inyectando una alta densidad de operadores aritméticos."""
    text = """
    Revenue = 365M
    Growth +15%
    Margin -3%
    Q1-Q4
    USD/EUR
    """
    node = ASTNode(node_id="node_3", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content=text), control_plane={})
    processed = classifier.classify_node(node)
    assert processed.node_type == ContentNodeType.PARAGRAPH

def test_algebraic_indices_are_equation(classifier):
    """Problema 1: Verifica que la indexación algebraica pura sin comandos LaTeX ni dólares active la clasificación."""
    text = "x_i + y_j = z_k"
    node = ASTNode(node_id="node_4", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content=text), control_plane={})
    processed = classifier.classify_node(node)
    assert processed.node_type == ContentNodeType.INLINE_EQUATION

def test_large_formula_diluted_in_prosa_reclassification(classifier):
    """Test 3: Verifica que fórmulas algebraicas largas basadas en subíndices no se diluyan en prosa."""
    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Se evalúa la ecuación x_i + y_j = z_k dentro del árbol de derivación. "
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    )
    node = ASTNode(node_id="node_5", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content=text), control_plane={})
    processed = classifier.classify_node(node)
    assert processed.node_type == ContentNodeType.INLINE_EQUATION

def test_complete_batch_idempotency(classifier):
    """Test 4: Garantiza que el procesamiento por lotes sea idempotente y libre de efectos secundarios."""
    batch = [
        ASTNode(node_id="batch_1", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content=r"\begin{align*} x=1 \end{align*}"), control_plane={}),
        ASTNode(node_id="batch_2", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content="Prosa financiera pura USD 500M"), control_plane={}),
        ASTNode(node_id="batch_3", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content="x_i + y_j = z_k"), control_plane={})
    ]
    
    first_pass = classifier.classify_batch(batch)
    second_pass = classifier.classify_batch(first_pass)
    
    for n1, n2 in zip(first_pass, second_pass):
        assert n1.node_type == n2.node_type
        assert n1.control_plane == n2.control_plane

def test_unbalanced_tokens_immunity(classifier):
    """Problemas 1, 2 y 3: Valida que tokens de nivel A sin cerrar o desbalanceados no fuercen la clasificación."""
    node_dollar = ASTNode(node_id="fail_1", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content="Precio = $$500 y subiendo."), control_plane={})
    assert classifier.classify_node(node_dollar).node_type == ContentNodeType.PARAGRAPH
    
    node_bracket = ASTNode(node_id="fail_2", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content="Texto roto \\[[0-9] sin cierre"), control_plane={})
    assert classifier.classify_node(node_bracket).node_type == ContentNodeType.PARAGRAPH

    node_env = ASTNode(node_id="fail_3", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content="Texto \begin{align*} x=1 "), control_plane={})
    assert classifier.classify_node(node_env).node_type == ContentNodeType.PARAGRAPH

def test_pure_operators_noise_immunity(classifier):
    """Problema 3: Una secuencia de guiones u operadores puros sin semántica fuerte no debe convertirse en ecuación."""
    node = ASTNode(node_id="node_noise", node_type=ContentNodeType.PARAGRAPH, payload=ParagraphPayload(content="a-b-c-d-e-f-g-h-i-j"), control_plane={})
    processed = classifier.classify_node(node)
    assert processed.node_type == ContentNodeType.PARAGRAPH