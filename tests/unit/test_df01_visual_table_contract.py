import pytest

from core.ast.builder import FlatASTBuilder
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.hashing import compute_ast_hash
from core.ast.models import ASTNode, TablePayload, VisualTablePayload, TranslationTaskType
from core.ast.registry import ASTRegistry
from core.chunking.manifest_contract import ChunkPlan, validate_chunk_coverage
from core.chunking.contextual_plan import prepare_contextual_plan
from core.layout.models import LayoutBlockCollection, LayoutBlockDraft

ASSET = "data/assets/" + "a" * 64 + ".pdf"


class Estimator:
    def estimate_tokens(self, text: str) -> int:
        return len(text)


def _node() -> ASTNode:
    return FlatASTBuilder.build(LayoutBlockCollection(blocks=[
        LayoutBlockDraft(logical_type="TABLE_COMPLEX", content=ASSET,
                         asset_path=ASSET, page_index=1),
    ]))[0]


def test_df01_visual_table_roundtrip_registry_and_plan(tmp_path):
    node = _node()
    assert isinstance(node.payload, VisualTablePayload)
    assert node.strategy == TranslationStrategy.PASSTHROUGH
    assert ASTNode.model_validate_json(node.model_dump_json()) == node
    literal = node.model_copy(update={"payload": TablePayload(content=ASSET)})
    assert compute_ast_hash([node]) != compute_ast_hash([literal])
    prepared = prepare_contextual_plan(document_id="df01", raw_ast=[node], estimator=Estimator())
    assert len(prepared.plan.units) == 1
    unit = prepared.plan.units[0]
    assert unit.chunk_type == TranslationTaskType.PRESERVE
    assert unit.target_payload == ASSET
    registry = ASTRegistry(str(tmp_path))
    ast = list(prepared.ast)
    digest = compute_ast_hash(ast)
    registry.register_ast("df01", digest, ast)
    restored = ASTRegistry(str(tmp_path)).get_verified_document_ast("df01", digest)
    assert restored == ast
    assert ChunkPlan.from_json(prepared.plan.to_json(), restored,
                               document_id="df01", ast_hash=digest) == prepared.plan
    for strategy in (TranslationStrategy.TRANSLATE, TranslationStrategy.OMIT):
        with pytest.raises(ValueError, match="DF01_TABLE_MUST_PRESERVE"):
            validate_chunk_coverage([node.with_strategy(strategy)], [unit])


@pytest.mark.parametrize("node_type", [ContentNodeType.TABLE_SIMPLE, ContentNodeType.PARAGRAPH])
def test_df01_visual_table_wrong_type_rejected(node_type):
    with pytest.raises(ValueError, match="DF01_ASSET_PAYLOAD_WRONG_NODE_TYPE"):
        ASTNode(node_id="bad", node_type=node_type, payload=VisualTablePayload(asset_path=ASSET))
    with pytest.raises(ValueError, match="DF01_ASSET_PAYLOAD_WRONG_NODE_TYPE"):
        ASTNode.model_validate({"node_id": "bad", "node_type": node_type,
                                "payload": {"asset_path": ASSET}})


def test_df01_literal_path_not_implicitly_visual():
    node = FlatASTBuilder.build(LayoutBlockCollection(blocks=[
        LayoutBlockDraft(logical_type="TABLE_COMPLEX", content=ASSET, page_index=1),
        LayoutBlockDraft(logical_type="TABLE_SIMPLE", content="a | b", page_index=1),
    ]))
    assert all(isinstance(n.payload, TablePayload) for n in node)
    with pytest.raises(ValueError, match="DF01_NONCANONICAL_TABLE_ASSET"):
        VisualTablePayload(asset_path="../outside.pdf")
    with pytest.raises(ValueError, match="DF01_LAYOUT_ASSET_TYPE_OR_CONTENT_DRIFT"):
        FlatASTBuilder.build(LayoutBlockCollection(blocks=[
            LayoutBlockDraft(logical_type="TABLE_COMPLEX", content="different",
                             asset_path=ASSET, page_index=1),
        ]))
