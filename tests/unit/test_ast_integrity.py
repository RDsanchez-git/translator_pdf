import pytest
from core.ast.models import ASTNode, ContentNodeType
from core.normalization.validators.ast_integrity import ASTIntegrityValidator

@pytest.fixture
def validator():
    return ASTIntegrityValidator()

def test_empty_ast_triggers_warning_only(validator):
    """Verifica que un AST vacío ya no cause un colapso severo del pipeline."""
    warnings = validator.validate_ast([])
    assert any(w.severity == "WARNING" and "EMPTY_AST" in w.message for w in warnings)
    assert not any(w.severity == "SEVERE" for w in warnings)

def test_duplicate_node_id_collision(validator):
    nodes = [
        ASTNode(node_id="duplicated_id", type=ContentNodeType.PARAGRAPH, content="Prosa 1"),
        ASTNode(node_id="duplicated_id", type=ContentNodeType.PARAGRAPH, content="Prosa 2")
    ]
    warnings = validator.validate_ast(nodes)
    assert any(w.severity == "SEVERE" and "DUPLICATE_NODE_ID" in w.message for w in warnings)

def test_malformed_placeholder_syntax(validator):
    nodes = [
        ASTNode(node_id="node_1", type=ContentNodeType.PARAGRAPH, content="[[ASSET:TABLE:id_123")
    ]
    warnings = validator.validate_ast(nodes)
    assert any(w.severity == "SEVERE" and "MALFORMED_ASSET_PLACEHOLDER" in w.message for w in warnings)

def test_orphan_list_item_emits_info_only(validator):
    """Garantiza que los ítems de lista aislados se marquen como telemetría INFO sin generar ruido."""
    nodes = [
        ASTNode(node_id="list_item_1", type=ContentNodeType.LIST_ITEM, content="• Item aislado por el OCR.")
    ]
    warnings = validator.validate_ast(nodes)
    assert any(w.severity == "INFO" and "ORPHAN_LIST_ITEM_LINT" in w.message for w in warnings)
    assert not any(w.severity in {"SEVERE", "WARNING"} for w in warnings)