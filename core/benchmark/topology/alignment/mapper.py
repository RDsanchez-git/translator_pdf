from typing import Sequence, Set, List
from core.benchmark.topology.ports import NodeMatchingPolicy
from core.benchmark.topology.models import AlignmentResult, AnchorCorrespondence
from core.benchmark.topology.alignment.lcs import SequenceAlignmentResult
from core.benchmark.topology.alignment.keys import IndexedAnchor

class AlignmentProjector:
    def __init__(self, matching_policy: NodeMatchingPolicy):
        self._policy = matching_policy

    def build(
        self, 
        candidate_anchors: Sequence[IndexedAnchor], 
        ground_truth_anchors: Sequence[IndexedAnchor],
        lcs_result: SequenceAlignmentResult,
        coverage: float
    ) -> AlignmentResult:
        matches: List[AnchorCorrespondence] = []
        c_unmatched: Set[str] = set()
        gt_unmatched: Set[str] = set()

        for match in lcs_result.aligned_pairs:
            c_anchor = candidate_anchors[match.candidate_index]
            gt_anchor = ground_truth_anchors[match.ground_truth_index]
            
            matches.append(
                AnchorCorrespondence(
                    candidate_uid=self._policy.unique_identifier(c_anchor.node),
                    ground_truth_uid=self._policy.unique_identifier(gt_anchor.node),
                    candidate_ast_index=c_anchor.ast_index,
                    ground_truth_ast_index=gt_anchor.ast_index
                )
            )

        for idx_c in lcs_result.unmatched_candidate_indices:
            c_unmatched.add(self._policy.unique_identifier(candidate_anchors[idx_c].node))

        for idx_gt in lcs_result.unmatched_ground_truth_indices:
            gt_unmatched.add(self._policy.unique_identifier(ground_truth_anchors[idx_gt].node))

        return AlignmentResult(
            matches=tuple(matches),
            unmatched_candidate_uids=c_unmatched,
            unmatched_ground_truth_uids=gt_unmatched,
            alignment_coverage=coverage
        )