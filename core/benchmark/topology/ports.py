from typing import Protocol, Sequence, Tuple, runtime_checkable
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType
from core.benchmark.topology.models import (
    MetricScoreDTO, 
    TopologicalEvaluationReport, 
    MatchingKey,
    AlignmentResult,
    EvaluationWindow,
    NormalizationResult,
    EvaluationForest,
    NormalizationInput,
    PostorderIndex,
)
# SOTA FIX: Ruta absoluta prefijada con 'core.'
from core.benchmark.topology.alignment.lcs import SequenceAlignmentResult

@runtime_checkable
class NodeCorrespondencePolicy(Protocol):
    def are_correspondent(self, candidate: ASTNode, ground_truth: ASTNode) -> bool: ...

@runtime_checkable
class ContentSimilarityPolicy(Protocol):
    def calculate_similarity(self, candidate_content: str, ground_truth_content: str, target_type: ContentNodeType) -> float: ...

@runtime_checkable
class EditCostPolicy(Protocol):
    def insertion_cost(self, node_type: ContentNodeType) -> float: ...
    def deletion_cost(self, node_type: ContentNodeType) -> float: ...
    def mismatch_cost(self, type_candidate: ContentNodeType, type_ground_truth: ContentNodeType) -> float: ...
    def substitution_weight(self, node_type: ContentNodeType) -> float: ...

@runtime_checkable
class NodeMatchingPolicy(Protocol):
    def match(self, candidate: ASTNode, ground_truth: ASTNode) -> bool: ...
    def matching_key(self, node: ASTNode) -> MatchingKey: ...
    def unique_identifier(self, node: ASTNode) -> str: ...

@runtime_checkable
class AnchorAlignmentStrategy(Protocol):
    def align(self, candidate_ast: Sequence[ASTNode], ground_truth_ast: Sequence[ASTNode]) -> AlignmentResult: ...

@runtime_checkable
class AnchorPartitionStrategy(Protocol):
    def partition(
        self, 
        candidate_ast: Sequence[ASTNode], 
        ground_truth_ast: Sequence[ASTNode],
        alignment: AlignmentResult
    ) -> Tuple[EvaluationWindow, ...]: ...

@runtime_checkable
class TreeEditCostContext(Protocol):
    """Proveedor unificado de traducción de costos operacionales atómicos para los motores topológicos."""
    def deletion_cost(self, node: ASTNode) -> float: ...
    def insertion_cost(self, node: ASTNode) -> float: ...
    def substitution_cost(self, candidate: ASTNode, ground_truth: ASTNode) -> float: ...

@runtime_checkable
class TreeDistanceAlgorithm(Protocol):
    """Puerto perimetral para motores algebraicos de cálculo de distancias de árboles."""
    def compute_distance(
        self, 
        cand_index: PostorderIndex, 
        gt_index: PostorderIndex, 
        costs: TreeEditCostContext
    ) -> float: ...

@runtime_checkable
class TreeEditEngine(Protocol):
    """Abstracción matemática pura aislada de las políticas de negocio."""
    def compute(
        self,
        candidate_forest: EvaluationForest,
        ground_truth_forest: EvaluationForest,
        cost_context: TreeEditCostContext
    ) -> float: ...

@runtime_checkable
class OverflowStrategy(Protocol):
    def handle_overflow(
        self,
        window: EvaluationWindow,
        cost_context: TreeEditCostContext
    ) -> float: ...

@runtime_checkable
class NormalizationPolicy(Protocol):
    """Escala de demeritación analítica pura acotada a métricas agregadas."""
    def normalize(self, input_data: NormalizationInput) -> NormalizationResult: ...

@runtime_checkable
class TopologicalEvaluatorProtocol(Protocol):
    @property
    def metric_name(self) -> str: ...
    def evaluate(self, candidate_ast: Sequence[ASTNode], ground_truth_ast: Sequence[ASTNode]) -> MetricScoreDTO: ...

@runtime_checkable
class ScoreAggregationPolicy(Protocol):
    def aggregate(self, metrics: Sequence[MetricScoreDTO]) -> float | None: ...

@runtime_checkable
class EvaluationStrategy(Protocol):
    def evaluate_run(self, document_id: str, candidate_ast: Sequence[ASTNode], ground_truth_ast: Sequence[ASTNode]) -> TopologicalEvaluationReport: ...

@runtime_checkable
class AnchorSequenceAlignmentEngine(Protocol):
    """Puerto de OCP para motores matemáticos de alineamiento sobre claves lógicas."""
    def align_sequences(
        self, 
        candidate_keys: tuple[MatchingKey, ...], 
        ground_truth_keys: tuple[MatchingKey, ...]
    ) -> SequenceAlignmentResult: ...