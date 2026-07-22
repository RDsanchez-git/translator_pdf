from core.benchmark.topology.ports import TreeDistanceAlgorithm, TreeEditCostContext
from core.benchmark.topology.models import PostorderIndex
from core.benchmark.topology.engines.zhang_shasha.matrix import TreeDistanceTable
from core.benchmark.topology.engines.zhang_shasha.forest import ForestDistanceCalculator

class ZhangShashaTreeDistanceCalculator(TreeDistanceAlgorithm):
    """
    Implementación canónica de Zhang-Shasha.
    Resuelve el dominio matemático completo (árboles densos y early exits de vacíos).
    """
    def __init__(self, forest_calc: ForestDistanceCalculator):
        self._forest_calc = forest_calc

    def compute_distance(
        self, 
        cand_index: PostorderIndex, 
        gt_index: PostorderIndex, 
        costs: TreeEditCostContext
    ) -> float:
        # Early exits matemáticos resueltos mediante sumas atómicas locales
        if cand_index.size == 0 and gt_index.size == 0:
            return 0.0
        if cand_index.size == 0:
            return float(sum(costs.insertion_cost(n) for n in gt_index.nodes))
        if gt_index.size == 0:
            return float(sum(costs.deletion_cost(n) for n in cand_index.nodes))

        td_table = TreeDistanceTable(rows=cand_index.size, cols=gt_index.size)

        for c_kr in cand_index.keyroots:
            for gt_kr in gt_index.keyroots:
                
                fd_cells = self._forest_calc.compute_forest_distance(
                    cand_root_idx=c_kr,
                    gt_root_idx=gt_kr,
                    cand_index=cand_index,
                    gt_index=gt_index,
                    td_table=td_table,
                    costs=costs
                )

                c_offset = cand_index.leftmost[c_kr]
                gt_offset = gt_index.leftmost[gt_kr]

                for i in range(c_offset, c_kr + 1):
                    for j in range(gt_offset, gt_kr + 1):
                        if cand_index.leftmost[i] == c_offset and gt_index.leftmost[j] == gt_offset:
                            td_table.cells[i][j] = fd_cells[i - c_offset + 1][j - gt_offset + 1]

        return td_table.cells[cand_index.size - 1][gt_index.size - 1]