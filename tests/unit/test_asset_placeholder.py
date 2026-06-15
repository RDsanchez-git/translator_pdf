import pytest
from core.normalization.fixers.asset_placeholder import StructuralAssetPlaceholder

@pytest.fixture
def fixer():
    return StructuralAssetPlaceholder()

def test_canonical_placeholder_generation(fixer):
    text = "| Col 1 | Col 2 |\n|---|---| "
    result = fixer.normalize(text, node_id="doc_p12_n04", node_type="table")
    
    # Comprobación del token estructurado sin emojis ni estilos visuales variables
    assert result.text == "[[ASSET:TABLE:doc_p12_n04]]"
    assert "asset_placeholder_inserted_table:1" in result.fixes

def test_empty_content_passthrough(fixer):
    result = fixer.normalize("", node_id="empty_1", node_type="figure")
    assert result.text == ""