from typing import List
from core.ast.models import ASTNode
from core.benchmark.topology.ports import TreeEditCostContext
from core.benchmark.topology.models import PostorderIndex
from core.benchmark.topology.engines.zhang_shasha.matrix import TreeDistanceTable
from core.benchmark.topology.engines.zhang_shasha.indexer import VIRTUAL_ROOT_ID

class ForestDistanceCalculator:
    """Ejecuta las ecuaciones canónicas de recurrencia de forma Stateless."""

    def _del_cost(self, node: ASTNode, costs: TreeEditCostContext) -> float:
        return 0.0 if node.node_id == VIRTUAL_ROOT_ID else costs.deletion_cost(node)

    def _ins_cost(self, node: ASTNode, costs: TreeEditCostContext) -> float:
        return 0.0 if node.node_id == VIRTUAL_ROOT_ID else costs.insertion_cost(node)

    def _sub_cost(self, cand: ASTNode, gt: ASTNode, costs: TreeEditCostContext) -> float:
        if cand.node_id == VIRTUAL_ROOT_ID and gt.node_id == VIRTUAL_ROOT_ID:
            return 0.0
        if cand.node_id == VIRTUAL_ROOT_ID:
            return self._ins_cost(gt, costs)
        if gt.node_id == VIRTUAL_ROOT_ID:
            return self._del_cost(cand, costs)
        return costs.substitution_cost(cand, gt)

    def compute_forest_distance(
        self,
        cand_root_idx: int,
        gt_root_idx: int,
        cand_index: PostorderIndex,
        gt_index: PostorderIndex,
        td_table: TreeDistanceTable,
        costs: TreeEditCostContext
    ) -> List[List[float]]:
        
        cand_offset = cand_index.leftmost[cand_root_idx]
        gt_offset = gt_index.leftmost[gt_root_idx]

        m = cand_root_idx - cand_offset + 2
        n = gt_root_idx - gt_offset + 2

        fd_cells = [[0.0] * n for _ in range(m)]

        for i in range(1, m):
            c_node = cand_index.nodes[cand_offset + i - 1]
            fd_cells[i][0] = fd_cells[i - 1][0] + self._del_cost(c_node, costs)

        for j in range(1, n):
            gt_node = gt_index.nodes[gt_offset + j - 1]
            fd_cells[0][j] = fd_cells[0][j - 1] + self._ins_cost(gt_node, costs)

        for i in range(1, m):
            cand_pos = cand_offset + i - 1
            c_node = cand_index.nodes[cand_pos]
            c_lld = cand_index.leftmost[cand_pos]

            for j in range(1, n):
                gt_pos = gt_offset + j - 1
                gt_node = gt_index.nodes[gt_pos]
                gt_lld = gt_index.leftmost[gt_pos]

                cost_del = fd_cells[i - 1][j] + self._del_cost(c_node, costs)
                cost_ins = fd_cells[i][j - 1] + self._ins_cost(gt_node, costs)

                if c_lld == cand_offset and gt_lld == gt_offset:
                    cost_match = fd_cells[i - 1][j - 1] + self._sub_cost(c_node, gt_node, costs)
                    chosen_cost = min(cost_del, cost_ins, cost_match)
                else:
                    i_mapped = c_lld - cand_offset
                    j_mapped = gt_lld - gt_offset
                    cost_tree_sub = fd_cells[i_mapped][j_mapped] + td_table.cells[cand_pos][gt_pos]
                    chosen_cost = min(cost_del, cost_ins, cost_tree_sub)

                fd_cells[i][j] = chosen_cost

        return fd_cells