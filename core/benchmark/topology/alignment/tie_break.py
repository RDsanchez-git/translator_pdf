from typing import Protocol, Tuple

class LCSTieBreakStrategy(Protocol):
    """Política determinista para la resolución de bifurcaciones óptimas equivalentes."""
    def resolve_tie(self, current_i: int, current_j: int) -> Tuple[int, int]: ...

class PreferCandidateTieBreaker(LCSTieBreakStrategy):
    """Heurística estándar que prioriza el consumo en el árbol candidato."""
    def resolve_tie(self, current_i: int, current_j: int) -> Tuple[int, int]:
        return current_i - 1, current_j