from typing import Tuple, Set
from dataclasses import dataclass, field
from core.ast.models import ASTNode


@dataclass(frozen=True)
class MatchingKey:
    """Value Object inmutable que encapsula un token de correspondencia lógica."""
    value: str

@dataclass(frozen=True)
class RecallDiagnostics:
    """Diagnóstico detallado de la ejecución del evaluador de recuperación."""
    precision: float
    recall: float
    true_positives: int
    false_positives: int
    false_negatives: int

@dataclass(frozen=True)
class NormalizationDiagnostics:
    """Trazas métricas e invariantes de control empleadas durante la escala de demeritación."""
    total_gt_destructive_cost: float
    total_candidate_constructive_cost: float
    worst_case_bound: float

@dataclass(frozen=True)
class NormalizationInput:
    """Encapsula las métricas agregadas requeridas para computar la demeritación estructural."""
    accumulated_distance: float
    total_gt_destructive_cost: float
    total_candidate_constructive_cost: float

@dataclass(frozen=True)
class NormalizationResult:
    """Resultado aglutinador de la escala de demeritación y sus trazas métricas."""
    score: float
    diagnostics: NormalizationDiagnostics | None = None

@dataclass(frozen=True)
class TedDiagnostics:
    """Métricas operacionales puras del pipeline de infraestructura topológica."""
    global_ted: float
    total_windows_evaluated: int
    overflow_triggered: bool
    normalization: NormalizationDiagnostics | None = None

# Unión explícita de tipos de diagnóstico para mitigar el Type Erasure
MetricDiagnostics = RecallDiagnostics | TedDiagnostics | NormalizationDiagnostics

@dataclass(frozen=True)
class MetricScoreDTO:
    """Contenedor universal inmutable para los resultados de un micro-juez."""
    metric_name: str
    primary_score: float
    diagnostics: MetricDiagnostics | None = field(default=None)

@dataclass(frozen=True)
class TopologicalEvaluationReport:
    """Agregado con inmutabilidad profunda garantizada para análisis estructural por documento."""
    document_id: str
    metrics: Tuple[MetricScoreDTO, ...] = field(default_factory=tuple)
    overall_score: float | None = None

@dataclass(frozen=True)
class ConfusionMatrix:
    """Encapsulamiento métrico de la matriz de confusión analítica."""
    true_positives: int
    false_positives: int
    false_negatives: int

    @property
    def precision(self) -> float:
        total = self.true_positives + self.false_positives
        return self.true_positives / total if total > 0 else 0.0

    @property
    def recall(self) -> float:
        total = self.true_positives + self.false_negatives
        return self.true_positives / total if total > 0 else 0.0

    @property
    def f1_score(self) -> float:
        p, r = self.precision, self.recall
        return (2.0 * p * r) / (p + r) if (p + r) > 0 else 0.0

    def to_diagnostics(self) -> RecallDiagnostics:
        return RecallDiagnostics(
            precision=self.precision,
            recall=self.recall,
            true_positives=self.true_positives,
            false_positives=self.false_positives,
            false_negatives=self.false_negatives
        )


@dataclass(frozen=True)
class AnchorCorrespondence:
    """Biyección topológica que incluye las coordenadas absolutas de corte."""
    candidate_uid: str
    ground_truth_uid: str
    candidate_ast_index: int
    ground_truth_ast_index: int


@dataclass(frozen=True)
class AlignmentResult:
    """
    Value Object enriquecido con relaciones explícitas y métricas de cobertura.
    
    INVARIANTE DE DOMINIO:
    - La colección 'matches' DEBE estar estrictamente ordenada de forma ascendente
      por 'candidate_ast_index' y 'ground_truth_ast_index' simultáneamente.
    """
    matches: Tuple[AnchorCorrespondence, ...]
    unmatched_candidate_uids: Set[str] = field(default_factory=set)
    unmatched_ground_truth_uids: Set[str] = field(default_factory=set)
    alignment_coverage: float = 1.0

@dataclass(frozen=True)
class EvaluationForest:
    """Value Object que garantiza la inmutabilidad y orden jerárquico del sub-bosque."""
    nodes: Tuple[ASTNode, ...]

    @property
    def size(self) -> int:
        return len(self.nodes)

    @property
    def is_empty(self) -> bool:
        return len(self.nodes) == 0

    @property
    def node_types(self) -> Tuple[str, ...]:
        return tuple(n.node_type.value for n in self.nodes)

@dataclass(frozen=True)
class TEDEvaluationContext:
    """Contenedor de estado operativo y configuraciones transversales del pipeline de ejecución."""
    max_node_threshold: int = 150
    enable_profiling: bool = False

@dataclass(frozen=True)
class EvaluationWindow:
    """Unidad atómica estructural que aísla un sub-bosque candidato y del oráculo."""
    window_index: int
    candidate: EvaluationForest
    ground_truth: EvaluationForest
    leading_anchor: AnchorCorrespondence | None = None

@dataclass(frozen=True)
class PostorderIndex:
    """
    Representación columnar pura (Data-Oriented) del bosque para optimización de caché.
    Ubicada en el modelo global para servir de contrato en las firmas de los puertos.
    """
    nodes: Tuple[ASTNode, ...]
    leftmost: Tuple[int, ...]
    keyroots: Tuple[int, ...]
    postorder: Tuple[int, ...]
    
    @property
    def size(self) -> int:
        return len(self.nodes)



