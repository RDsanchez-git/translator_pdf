from core.benchmark.topology.ports import TreeEditEngine, TreeEditCostContext, TreeDistanceAlgorithm
from core.benchmark.topology.models import EvaluationForest
from core.benchmark.topology.engines.zhang_shasha.indexer import PostorderIndexer

class ZhangShashaEngine(TreeEditEngine):
    """
    Adaptador de orquestación puro acoplado a contratos perimetrales (Ports).
    Se limita a indexar las colecciones y delegar la DP al algoritmo inyectado.
    """
    def __init__(self, indexer: PostorderIndexer, algorithm: TreeDistanceAlgorithm):
        self._indexer = indexer
        self._algorithm = algorithm

    def compute(
        self,
        candidate_forest: EvaluationForest,
        ground_truth_forest: EvaluationForest,
        cost_context: TreeEditCostContext
    ) -> float:
        cand_index = self._indexer.build(candidate_forest.nodes)
        gt_index = self._indexer.build(ground_truth_forest.nodes)
        
        return self._algorithm.compute_distance(cand_index, gt_index, cost_context)