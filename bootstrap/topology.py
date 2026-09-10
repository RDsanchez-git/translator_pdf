
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
from core.benchmark.topology.regression.configuration import (
    CanonicalEngineConfiguration,
)
from core.benchmark.topology.regression.models import RegressionThresholds
from core.benchmark.topology.criticality.costs import CriticalityAwareCostContext
from core.benchmark.topology.criticality.models import NodeCriticality


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


def build_canonical_engine_configuration(
    *,
    matching_policy=None,
    alignment_engine=None,
    cost_context=None,
    thresholds=None,
    warning_threshold=1,
):
    """Construye la configuracion canonica del motor de evaluacion.

    NADR-22 §5.6 R19: Identificador criptografico de configuracion.

    SYNC: Los defaults de partitioner, normalizer, overflow y el algoritmo
    de distancia deben coincidir exactamente con los de create_topology_evaluator().
    Estos componentes son stateless y canonicos; la duplicacion controlada es
    preferible a modificar la API de create_topology_evaluator.

    El engine se construye explicitamente para poder extraer su identidad
    tipada absoluta (module.qualname) y evitar strings libres en el payload
    del fingerprint.
    """
    # Construir el engine explicitamente para extraer identidad tipada
    indexer = PostorderIndexer()
    forest_calc = ForestDistanceCalculator()
    algorithm = ZhangShashaTreeDistanceCalculator(forest_calc)
    engine = ZhangShashaEngine(indexer=indexer, algorithm=algorithm)

    # Componentes inyectados o defaults (SYNC con create_topology_evaluator)
    resolved_matching = matching_policy if matching_policy is not None else DefaultNodeMatchingPolicy()

    if alignment_engine is not None:
        resolved_alignment_engine = alignment_engine
    else:
        try:
            resolved_alignment_engine = LCSSequenceAlignmentEngine(PreferCandidateTieBreaker())
        except TypeError:
            resolved_alignment_engine = LCSSequenceAlignmentEngine()

    aligner = LCSAnchorAlignmentStrategy(
        matching_policy=resolved_matching,
        alignment_engine=resolved_alignment_engine,
    )

    # SYNC: estos 3 defaults deben coincidir con create_topology_evaluator()
    partitioner = HeadingAnchorPartitionStrategy()
    overflow = WorstCaseOverflowStrategy()
    normalizer = MaxBoundNormalizationPolicy()

    # Extraer pesos con isinstance (no hasattr)
    resolved_costs = cost_context if cost_context is not None else UnitCostContext()
    if isinstance(resolved_costs, CriticalityAwareCostContext):
        w = resolved_costs.weights
        cost_weights = (
            w[NodeCriticality.CRITICAL],
            w[NodeCriticality.WARNING],
            w[NodeCriticality.INFO],
        )
    else:
        cost_weights = (1.0, 1.0, 1.0)

    resolved_thresholds = thresholds or RegressionThresholds()

    return CanonicalEngineConfiguration.from_components(
        engine=engine,
        cost_weights=cost_weights,
        partitioner=partitioner,
        aligner=aligner,
        normalizer=normalizer,
        overflow=overflow,
        matching_policy=resolved_matching,
        nss_hard_fail=resolved_thresholds.nss_hard_fail,
        nss_warning=resolved_thresholds.nss_warning,
        warning_threshold=warning_threshold,
    )