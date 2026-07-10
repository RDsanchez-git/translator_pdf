from core.domain.document import DocumentType

class ClassificationScores:
    __slots__ = ("_scores",)

    def __init__(self) -> None:
        # Inicializa dinámicamente sin buscar UNKNOWN
        self._scores: dict[DocumentType, float] = {dt: 0.0 for dt in DocumentType}

    def add(self, doc_type: DocumentType, score: float) -> None:
        if doc_type in self._scores:
            self._scores[doc_type] += score

    def winner(self) -> tuple[DocumentType | None, float]:
        if not self._scores:
            return None, 0.0
        
        # Corrección tipado estricto
        best_type, best_score = max(self._scores.items(), key=lambda item: item[1])
        
        if best_score == 0.0:
            return None, 0.0
            
        return best_type, min(best_score, 1.0)