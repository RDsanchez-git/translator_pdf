from typing import Final
from core.domain.document import DocumentType
from core.ast.enums import ContentNodeType
from core.document_profile.models import ProfileInput, LayoutDetection, TypeDetection, PageLayout
from core.document_profile.extractors import NodeSemanticAdapter
from core.document_profile.scoring import ClassificationScores

class HeuristicTypeDetector:
    """
    SOTA: Clasificador taxonómico.
    Utiliza el ContentNodeType oficial para agrupar evidencia sin duplicar ontologías.
    """
    __slots__ = ("_semantic_adapter",)

    _LAYOUT_PAPER_WEIGHT_DBL: Final[float] = 0.5
    _LAYOUT_REPORT_WEIGHT_DBL: Final[float] = 0.1
    _LAYOUT_BOOK_WEIGHT_SGL: Final[float] = 0.4
    _LAYOUT_REPORT_WEIGHT_SGL: Final[float] = 0.3

    _MATH_DENSITY_THRESHOLD: Final[float] = 0.05
    _MATH_PAPER_MULTIPLIER: Final[float] = 10.0
    _NARRATIVE_DENSITY_THRESHOLD: Final[float] = 0.60
    _NARRATIVE_BOOK_MULTIPLIER: Final[float] = 1.0

    # CORRECCIÓN SOTA: Alineado con ContentNodeType real
    _NARRATIVE_KINDS: Final[frozenset[ContentNodeType]] = frozenset({
        ContentNodeType.PARAGRAPH, 
        ContentNodeType.HEADING 
    })
    
    _MATH_KINDS: Final[frozenset[ContentNodeType]] = frozenset({
        ContentNodeType.DISPLAY_EQUATION,
        ContentNodeType.INLINE_EQUATION
    })

    def __init__(self, semantic_adapter: NodeSemanticAdapter):
        self._semantic_adapter = semantic_adapter

    def _apply_layout_context(self, scores: ClassificationScores, layout: LayoutDetection) -> None:
        if layout.layout == PageLayout.DOUBLE_COLUMN:
            scores.add(DocumentType.PAPER, self._LAYOUT_PAPER_WEIGHT_DBL * layout.confidence)
            scores.add(DocumentType.REPORT, self._LAYOUT_REPORT_WEIGHT_DBL * layout.confidence)
        elif layout.layout == PageLayout.SINGLE_COLUMN:
            scores.add(DocumentType.BOOK, self._LAYOUT_BOOK_WEIGHT_SGL * layout.confidence)
            scores.add(DocumentType.REPORT, self._LAYOUT_REPORT_WEIGHT_SGL * layout.confidence)

    def _apply_ontology_context(self, scores: ClassificationScores, input_data: ProfileInput) -> None:
        total_nodes = len(input_data.nodes)
        if total_nodes == 0:
            return
            
        math_nodes = 0
        narrative_nodes = 0
        
        for node in input_data.nodes:
            node_kind = self._semantic_adapter.kind(node)
            if node_kind in self._MATH_KINDS:
                math_nodes += 1
            elif node_kind in self._NARRATIVE_KINDS:
                narrative_nodes += 1

        math_ratio = math_nodes / total_nodes
        narrative_ratio = narrative_nodes / total_nodes

        if math_ratio > self._MATH_DENSITY_THRESHOLD:
            scores.add(DocumentType.PAPER, min(math_ratio * self._MATH_PAPER_MULTIPLIER, 0.4))
        
        if narrative_ratio > self._NARRATIVE_DENSITY_THRESHOLD:
            scores.add(DocumentType.BOOK, min(narrative_ratio * self._NARRATIVE_BOOK_MULTIPLIER, 0.4))

    def detect(self, input_data: ProfileInput, layout: LayoutDetection) -> TypeDetection:
        if not input_data.nodes:
            return TypeDetection(document_type=None, confidence=0.0)

        scores = ClassificationScores()
        
        self._apply_layout_context(scores, layout)
        self._apply_ontology_context(scores, input_data)

        best_type, best_score = scores.winner()
        return TypeDetection(document_type=best_type, confidence=best_score)