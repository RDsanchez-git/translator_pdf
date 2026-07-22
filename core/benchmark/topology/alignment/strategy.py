from typing import Sequence
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.benchmark.topology.ports import AnchorAlignmentStrategy, NodeMatchingPolicy, AnchorSequenceAlignmentEngine
from core.benchmark.topology.models import AlignmentResult
from core.benchmark.topology.alignment.keys import AnchorExtractor, MatchingKeyMapper
from core.benchmark.topology.alignment.mapper import AlignmentProjector
from core.benchmark.topology.alignment.metrics import AlignmentQualityPolicy

class LCSAnchorAlignmentStrategy(AnchorAlignmentStrategy):
    """Estrategia perimetral desacoplada mediante inversión de control sobre el motor."""
    def __init__(
        self, 
        matching_policy: NodeMatchingPolicy,
        alignment_engine: AnchorSequenceAlignmentEngine,
        anchor_type: ContentNodeType = ContentNodeType.HEADING
    ):
        self._extractor = AnchorExtractor(anchor_type)
        self._mapper = MatchingKeyMapper(matching_policy)
        self._engine = alignment_engine
        self._projector = AlignmentProjector(matching_policy)

    def align(self, candidate_ast: Sequence[ASTNode], ground_truth_ast: Sequence[ASTNode]) -> AlignmentResult:
        c_anchors = self._extractor.extract(candidate_ast)
        gt_anchors = self._extractor.extract(ground_truth_ast)

        c_keys = self._mapper.map_to_keys(c_anchors)
        gt_keys = self._mapper.map_to_keys(gt_anchors)

        # Inversión de control pura: el algoritmo matemático está completamente aislado
        lcs_result = self._engine.align_sequences(c_keys, gt_keys)

        coverage = AlignmentQualityPolicy.calculate_coverage(
            aligned_count=len(lcs_result.aligned_pairs),
            unmatched_candidate_count=len(lcs_result.unmatched_candidate_indices),
            unmatched_ground_truth_count=len(lcs_result.unmatched_ground_truth_indices)
        )

        return self._projector.build(
            candidate_anchors=c_anchors,
            ground_truth_anchors=gt_anchors,
            lcs_result=lcs_result,
            coverage=coverage
        )