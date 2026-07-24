import pytest
from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, HeadingPayload, ParagraphPayload
from tools.evaluation.topology.metrics.structural import StructuralTopologyMetric


@pytest.fixture
def metric() -> StructuralTopologyMetric:
    return StructuralTopologyMetric()


def test_determinism_invariant(metric: StructuralTopologyMetric):
    gt = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.HEADING,
            payload=HeadingPayload(content="Title"),
        ),
        ASTNode(
            node_id="2",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Text A"),
            parent_node_id="1",
        ),
    ]
    cand = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.HEADING,
            payload=HeadingPayload(content="Title"),
        ),
        ASTNode(
            node_id="2",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Text B"),
            parent_node_id="1",
        ),
    ]

    first_run = metric.evaluate(cand, gt)
    for _ in range(5):
        subsequent_run = metric.evaluate(cand, gt)
        assert subsequent_run.value == first_run.value
        assert subsequent_run.details == first_run.details


def test_identical_trees(metric: StructuralTopologyMetric):
    nodes = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.HEADING,
            payload=HeadingPayload(content="Title"),
        ),
        ASTNode(
            node_id="2",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Hello"),
            parent_node_id="1",
        ),
    ]
    result = metric.evaluate(nodes, nodes)
    assert result.value == 1.0


def test_empty_trees(metric: StructuralTopologyMetric):
    result = metric.evaluate([], [])
    assert result.value == 1.0


def test_node_id_agnosticism(metric: StructuralTopologyMetric):
    gt = [
        ASTNode(
            node_id="uuid-1",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Text"),
        )
    ]
    cand = [
        ASTNode(
            node_id="uuid-999",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Text"),
        )
    ]

    result = metric.evaluate(cand, gt)
    assert result.value == 1.0


def test_hierarchy_flattening_detection(metric: StructuralTopologyMetric):
    # Árbol Anidado: HEADING es padre de PARAGRAPH
    nested_gt = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.HEADING,
            payload=HeadingPayload(content="Title"),
        ),
        ASTNode(
            node_id="2",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Text"),
            parent_node_id="1",
        ),
    ]
    # Árbol Plano: HEADING y PARAGRAPH son hermanos (parent_node_id es None en ambos)
    flat_cand = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.HEADING,
            payload=HeadingPayload(content="Title"),
        ),
        ASTNode(
            node_id="2",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Text"),
        ),
    ]

    result = metric.evaluate(flat_cand, nested_gt)
    assert result.value < 1.0


def test_child_reordering_sensitivity(metric: StructuralTopologyMetric):
    gt = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.HEADING,
            payload=HeadingPayload(content="Title"),
        ),
        ASTNode(
            node_id="2",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="A"),
            parent_node_id="1",
        ),
        ASTNode(
            node_id="3",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="B"),
            parent_node_id="1",
        ),
    ]
    cand = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.HEADING,
            payload=HeadingPayload(content="Title"),
        ),
        ASTNode(
            node_id="3",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="B"),
            parent_node_id="1",
        ),
        ASTNode(
            node_id="2",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="A"),
            parent_node_id="1",
        ),
    ]

    result = metric.evaluate(cand, gt)
    assert result.value < 1.0


def test_rename_same_type_vs_diff_type(metric: StructuralTopologyMetric):
    gt = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Original Text"),
        )
    ]
    cand_same_type = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.PARAGRAPH,
            payload=ParagraphPayload(content="Modified Text"),
        )
    ]
    cand_diff_type = [
        ASTNode(
            node_id="1",
            node_type=ContentNodeType.HEADING,
            payload=HeadingPayload(content="Original Text"),
        )
    ]

    res_same = metric.evaluate(cand_same_type, gt)
    res_diff = metric.evaluate(cand_diff_type, gt)

    assert res_same.value > res_diff.value