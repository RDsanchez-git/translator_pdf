
from core.ast.models import ASTNode
from core.benchmark.topology.evaluators.ted import TreeEditDistanceEvaluator, TEDEvaluationContext
from core.benchmark.topology.engines.zhang_shasha.indexer import PostorderIndexer
from core.benchmark.topology.engines.zhang_shasha.forest import ForestDistanceCalculator
from core.benchmark.topology.engines.zhang_shasha.tree import ZhangShashaTreeDistanceCalculator
from core.benchmark.topology.engines.zhang_shasha.engine import ZhangShashaEngine
from core.benchmark.topology.costs.unit import UnitCostContext
from core.benchmark.topology.ports import (
    TreeEditCostContext, 
    TopologicalEvaluatorProtocol,
    NodeMatchingPolicy,
    AnchorSequenceAlignmentEngine
)
from core.benchmark.topology.models import MatchingKey

from core.benchmark.topology.alignment.strategy import LCSAnchorAlignmentStrategy
from core.benchmark.topology.engines.lcs_engine import LCSSequenceAlignmentEngine, PreferCandidateTieBreaker
from core.benchmark.topology.partitioning.heading import HeadingAnchorPartitionStrategy
from core.benchmark.topology.policies.overflow import WorstCaseOverflowStrategy
from core.benchmark.topology.policies.normalization import MaxBoundNormalizationPolicy


class DefaultNodeMatchingPolicy(NodeMatchingPolicy):
    """Política de coincidencia de anclajes basada en tipo estructural y contenido textual del nodo."""

    def match(self, candidate: ASTNode, ground_truth: ASTNode) -> bool:
        return (
            candidate.node_type == ground_truth.node_type
            and candidate.text_content == ground_truth.text_content
        )

    def matching_key(self, node: ASTNode) -> MatchingKey:
        return MatchingKey(value=f"{node.node_type}:{node.text_content}")

    def unique_identifier(self, node: ASTNode) -> str:
        return node.node_id


def create_topology_evaluator(
    matching_policy: NodeMatchingPolicy | None = None,
    alignment_engine: AnchorSequenceAlignmentEngine | None = None,
    cost_context: TreeEditCostContext | None = None,
    max_node_threshold: int = 2000
) -> TopologicalEvaluatorProtocol:
    """Ensambla el pipeline de evaluación topológica conectando motor, alineador y políticas."""
    indexer = PostorderIndexer()
    forest_calc = ForestDistanceCalculator()
    algorithm = ZhangShashaTreeDistanceCalculator(forest_calc)
    engine = ZhangShashaEngine(indexer=indexer, algorithm=algorithm)
    
    costs = cost_context if cost_context is not None else UnitCostContext()
    
    # Inyección de dependencias con fallbacks concretos
    resolved_matching_policy = matching_policy if matching_policy is not None else DefaultNodeMatchingPolicy()
    
    if alignment_engine is not None:
        resolved_alignment_engine = alignment_engine
    else:
        try:
            resolved_alignment_engine = LCSSequenceAlignmentEngine(PreferCandidateTieBreaker())
        except TypeError:
            resolved_alignment_engine = LCSSequenceAlignmentEngine()

    aligner = LCSAnchorAlignmentStrategy(
        matching_policy=resolved_matching_policy,
        alignment_engine=resolved_alignment_engine
    )
    
    partitioner = HeadingAnchorPartitionStrategy()
    overflow = WorstCaseOverflowStrategy()
    normalizer = MaxBoundNormalizationPolicy()
    
    context = TEDEvaluationContext(max_node_threshold=max_node_threshold)

    return TreeEditDistanceEvaluator(
        aligner=aligner,
        partitioner=partitioner,
        engine=engine,
        overflow_handler=overflow,
        normalizer=normalizer,
        cost_context=costs,
        evaluation_context=context
    )