"""W2.2 real ASTRegistry consumer: replay never trusts a stale cached AST."""

import json

import pytest

from core.ast.enums import ContentNodeType, HeadingLevel
from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode, HeadingPayload, ParagraphPayload
from core.ast.registry import ASTRegistry


def _ast(level: HeadingLevel = HeadingLevel.H1):
    return [
        ASTNode(
            node_id="heading", sequence_id=1,
            node_type=ContentNodeType.HEADING,
            payload=HeadingPayload(content="1 Methods", heading_level=level),
            depth=1,
        ),
        ASTNode(
            node_id="paragraph", sequence_id=2,
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="H₂O in experiment"), depth=1,
        ),
    ]


@pytest.mark.integration
def test_verified_ast_registry_survives_restart_with_exact_semantic_generation(tmp_path):
    nodes = _ast()
    digest = compute_ast_hash(nodes)
    ASTRegistry(str(tmp_path)).register_ast("document", digest, nodes)
    restarted = ASTRegistry(str(tmp_path))
    assert restarted.get_verified_document_ast("document", digest) == nodes
    assert restarted.get_document_ast("document", digest) == nodes


@pytest.mark.integration
def test_verified_registry_rejects_mutated_heading_even_with_hot_cache(tmp_path):
    nodes = _ast()
    digest = compute_ast_hash(nodes)
    registry = ASTRegistry(str(tmp_path))
    registry.register_ast("document", digest, nodes)
    assert registry.get_verified_document_ast("document", digest) == nodes
    path = tmp_path / "data" / "ast_cache" / f"document.{digest}.ast.json"
    stored = json.loads(path.read_text(encoding="utf-8"))
    stored["nodes"][0]["payload"]["heading_level"] = HeadingLevel.H2.value
    path.write_text(json.dumps(stored), encoding="utf-8")
    with pytest.raises(ValueError, match="PPPR_G2_AST_SEMANTIC_GENERATION_DRIFT"):
        registry.get_verified_document_ast("document", digest)


@pytest.mark.integration
def test_verified_registry_rejects_unbound_legacy_hash_and_envelope_mismatch(tmp_path):
    nodes = _ast()
    registry = ASTRegistry(str(tmp_path))
    registry.register_ast("document", "0" * 64, nodes)
    with pytest.raises(ValueError, match="PPPR_G2_AST_SEMANTIC_GENERATION_DRIFT"):
        registry.get_verified_document_ast("document", "0" * 64)
    correct = compute_ast_hash(nodes)
    registry.register_ast("document", correct, nodes)
    path = tmp_path / "data" / "ast_cache" / f"document.{correct}.ast.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["document_id"] = "another-document"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="PPPR_G2_AST_PERSISTED_ENVELOPE_MISMATCH"):
        registry.get_verified_document_ast("document", correct)
