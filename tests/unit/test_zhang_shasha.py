import pytest
from typing import List
from core.ast.models import ASTNode, ParagraphPayload
from core.ast.enums import ContentNodeType, TranslationStrategy
from core.benchmark.topology.models import EvaluationForest
from core.benchmark.topology.ports import TreeEditCostContext
from core.benchmark.topology.engines.zhang_shasha.indexer import PostorderIndexer, IndexConsistencyError
from core.benchmark.topology.engines.zhang_shasha.forest import ForestDistanceCalculator
from core.benchmark.topology.engines.zhang_shasha.tree import ZhangShashaTreeDistanceCalculator
from core.benchmark.topology.engines.zhang_shasha.engine import ZhangShashaEngine


# --- FIXTURE / STUB LOCAL ---

class UnitCostContext(TreeEditCostContext):
    """Contexto estricto de costos unitarios deterministas para pruebas de correctitud."""
    def deletion_cost(self, node: ASTNode) -> float:
        return 1.0

    def insertion_cost(self, node: ASTNode) -> float:
        return 1.0

    def substitution_cost(self, candidate: ASTNode, ground_truth: ASTNode) -> float:
        return 0.0 if candidate.text_content == ground_truth.text_content else 1.0


# --- HELPERS ---

def create_node(node_id: str, parent_id: str | None = None, content: str = "text", seq: int = 1) -> ASTNode:
    return ASTNode(
        node_id=node_id,
        sequence_id=seq,
        node_type=ContentNodeType.PARAGRAPH,
        strategy=TranslationStrategy.TRANSLATE,
        payload=ParagraphPayload(content=content),
        parent_node_id=parent_id
    )

@pytest.fixture
def engine() -> ZhangShashaEngine:
    indexer = PostorderIndexer()
    forest_calc = ForestDistanceCalculator()
    algorithm = ZhangShashaTreeDistanceCalculator(forest_calc)
    return ZhangShashaEngine(indexer=indexer, algorithm=algorithm)

@pytest.fixture
def costs() -> TreeEditCostContext:
    return UnitCostContext()


# =====================================================================
# 1. OPERACIONES ATÓMICAS BÁSICAS
# =====================================================================

def test_empty_forests(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    empty = EvaluationForest(nodes=())
    assert engine.compute(empty, empty, costs) == 0.0

def test_single_node(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    n1 = create_node("a", content="hello")
    f = EvaluationForest(nodes=(n1,))
    assert engine.compute(f, f, costs) == 0.0

def test_identical_trees(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    r1 = create_node("r", content="root")
    c1 = create_node("c", parent_id="r", content="child")
    f1 = EvaluationForest(nodes=(r1, c1))
    f2 = EvaluationForest(nodes=(r1, c1))
    assert engine.compute(f1, f2, costs) == 0.0

def test_atomic_insertion(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    root = create_node("r", content="root")
    child = create_node("c", parent_id="r", content="child")
    f_small = EvaluationForest(nodes=(root,))
    f_large = EvaluationForest(nodes=(root, child))
    assert engine.compute(f_small, f_large, costs) == 1.0

def test_atomic_deletion(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    root = create_node("r", content="root")
    child = create_node("c", parent_id="r", content="child")
    f_small = EvaluationForest(nodes=(root,))
    f_large = EvaluationForest(nodes=(root, child))
    assert engine.compute(f_large, f_small, costs) == 1.0

def test_atomic_substitution(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    n1 = create_node("a", content="original")
    n2 = create_node("b", content="modified")
    f1, f2 = EvaluationForest(nodes=(n1,)), EvaluationForest(nodes=(n2,))
    assert engine.compute(f1, f2, costs) == 1.0


# =====================================================================
# 2. PROPIEDADES MATEMÁTICAS DE TED
# =====================================================================

def test_isomorphism_ignores_ids(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    r_a = create_node("id_a1", content="root")
    c_a = create_node("id_a2", parent_id="id_a1", content="child")
    r_b = create_node("id_x1", content="root")
    c_b = create_node("id_x2", parent_id="id_x1", content="child")
    
    f1, f2 = EvaluationForest(nodes=(r_a, c_a)), EvaluationForest(nodes=(r_b, c_b))
    assert engine.compute(f1, f2, costs) == 0.0

def test_metric_symmetry(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    r1 = create_node("r1", content="root")
    c1 = create_node("c1", parent_id="r1", seq=1, content="child_A")
    f_a = EvaluationForest(nodes=(r1, c1))
    
    r2 = create_node("r2", content="root")
    c2 = create_node("c2", parent_id="r2", seq=1, content="child_B")
    c3 = create_node("c3", parent_id="r2", seq=2, content="child_C")  # SOTA FIX: seq=2
    f_b = EvaluationForest(nodes=(r2, c2, c3))
    
    assert engine.compute(f_a, f_b, costs) == engine.compute(f_b, f_a, costs)


# =====================================================================
# 3. INVARIANTES Y COMPLEJIDAD ESTRUCTURAL
# =====================================================================

def test_ordered_tree_constraint_violation():
    indexer = PostorderIndexer()
    p = create_node("p")
    h1 = create_node("h1", parent_id="p", seq=2)
    h2 = create_node("h2", parent_id="p", seq=1)
    
    with pytest.raises(IndexConsistencyError, match="Invariante de Sibling Order rota"):
        indexer.build((p, h1, h2))

def test_multi_root_forest(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    r1, r2 = create_node("r1", seq=1), create_node("r2", seq=2)
    c1 = create_node("c1", parent_id="r1", seq=1)
    
    f1, f2 = EvaluationForest(nodes=(r1, c1, r2)), EvaluationForest(nodes=(r1, r2))
    assert engine.compute(f1, f2, costs) == 1.0

def test_deep_linear_tree(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    n1 = create_node("1", seq=1)
    n2 = create_node("2", parent_id="1", seq=1)
    n3 = create_node("3", parent_id="2", seq=1)
    
    f1, f2 = EvaluationForest(nodes=(n1, n2, n3)), EvaluationForest(nodes=(n1, n2))
    assert engine.compute(f1, f2, costs) == 1.0

def test_wide_tree_multiple_keyroots(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    parent = create_node("p", seq=1)
    h1 = create_node("h1", parent_id="p", seq=1, content="A")
    h2 = create_node("h2", parent_id="p", seq=2, content="B")
    h3 = create_node("h3", parent_id="p", seq=3, content="C")
    f1 = EvaluationForest(nodes=(parent, h1, h2, h3))

    h2_mod = create_node("h2_mod", parent_id="p", seq=2, content="X")
    f2 = EvaluationForest(nodes=(parent, h1, h2_mod, h3))
    
    assert engine.compute(f1, f2, costs) == 1.0

def test_same_cardinality_different_depth(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    r_a = create_node("r", content="same")
    b_a = create_node("b", parent_id="r", seq=1, content="same")
    c_a = create_node("c", parent_id="r", seq=2, content="same")
    f_flat = EvaluationForest(nodes=(r_a, b_a, c_a))

    r_b = create_node("r", content="same")
    b_b = create_node("b", parent_id="r", seq=1, content="same")
    c_b = create_node("c", parent_id="b", seq=1, content="same")
    f_deep = EvaluationForest(nodes=(r_b, b_b, c_b))

    assert engine.compute(f_flat, f_deep, costs) > 0.0

def test_dissimilar_structures_fd_td_collapse(engine: ZhangShashaEngine, costs: TreeEditCostContext):
    root_a = create_node("r_a", content="shared_root")
    f_a = EvaluationForest(nodes=(root_a,))

    root_b = create_node("r_b", content="shared_root")
    c = create_node("c", parent_id="r_b", seq=1, content="C")
    d = create_node("d", parent_id="r_b", seq=2, content="D")
    e = create_node("e", parent_id="r_b", seq=3, content="E")
    f_b = EvaluationForest(nodes=(root_b, c, d, e))

    assert engine.compute(f_a, f_b, costs) == 3.0


# =====================================================================
# 4. SCALE SMOKE TESTS (ROBUSTEZ)
# =====================================================================

NUM_MUTATIONS = 10

@pytest.mark.parametrize("tree_size", [50, 100, 150])
def test_scale_robustness_large_trees(engine: ZhangShashaEngine, costs: TreeEditCostContext, tree_size: int):
    nodes_a: List[ASTNode] = [create_node("r", seq=1)]
    nodes_b: List[ASTNode] = [create_node("r", seq=1)]
    mutation_start_index = max(1, tree_size - NUM_MUTATIONS)

    for i in range(1, tree_size):
        parent_id = "r" if i < 10 else f"n_{i // 10}"
        nodes_a.append(create_node(f"n_{i}", parent_id=parent_id, seq=i, content=f"val_{i}"))
        val_b = f"val_{i}" if i < mutation_start_index else f"alt_{i}"
        nodes_b.append(create_node(f"n_{i}", parent_id=parent_id, seq=i, content=val_b))
        
    f_a, f_b = EvaluationForest(nodes=tuple(nodes_a)), EvaluationForest(nodes=tuple(nodes_b))
    distance = engine.compute(f_a, f_b, costs)
    
    assert isinstance(distance, float)
    assert distance == float(tree_size - mutation_start_index)