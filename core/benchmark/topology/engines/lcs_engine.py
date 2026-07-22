from typing import Protocol, Tuple
from core.benchmark.topology.ports import AnchorSequenceAlignmentEngine
from core.benchmark.topology.models import MatchingKey
from core.benchmark.topology.alignment.lcs import SequenceAlignmentResult, AnchorMatch

class LCSTieBreakStrategy(Protocol):
    """Política determinista para la resolución de bifurcaciones óptimas equivalentes."""
    def resolve_tie(self, current_i: int, current_j: int) -> Tuple[int, int]: ...

class PreferCandidateTieBreaker(LCSTieBreakStrategy):
    """Heurística estándar que prioriza el consumo en el árbol candidato."""
    def resolve_tie(self, current_i: int, current_j: int) -> Tuple[int, int]:
        return current_i - 1, current_j

class LCSSequenceAlignmentEngine(AnchorSequenceAlignmentEngine):
    """Motor matricial LCS desacoplado de las reglas de negocio."""
    def __init__(self, tie_breaker: LCSTieBreakStrategy | None = None):
        self._tie_breaker = tie_breaker or PreferCandidateTieBreaker()

    def align_sequences(
        self, 
        candidate_keys: tuple[MatchingKey, ...], 
        ground_truth_keys: tuple[MatchingKey, ...]
    ) -> SequenceAlignmentResult:
        m, n = len(candidate_keys), len(ground_truth_keys)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if candidate_keys[i-1] == ground_truth_keys[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        aligned_pairs: list[AnchorMatch] = []
        i, j = m, n
        
        # Backtracking abstraído
        while i > 0 and j > 0:
            if candidate_keys[i-1] == ground_truth_keys[j-1]:
                aligned_pairs.append(AnchorMatch(candidate_index=i-1, ground_truth_index=j-1))
                i -= 1
                j -= 1
            elif dp[i-1][j] == dp[i][j-1]:
                i, j = self._tie_breaker.resolve_tie(i, j)
            elif dp[i-1][j] > dp[i][j-1]:
                i -= 1
            else:
                j -= 1

        aligned_pairs.reverse()
        
        aligned_c = {p.candidate_index for p in aligned_pairs}
        aligned_gt = {p.ground_truth_index for p in aligned_pairs}
        
        unmatched_c = tuple(idx for idx in range(m) if idx not in aligned_c)
        unmatched_gt = tuple(idx for idx in range(n) if idx not in aligned_gt)

        return SequenceAlignmentResult(
            aligned_pairs=tuple(aligned_pairs),
            unmatched_candidate_indices=unmatched_c,
            unmatched_ground_truth_indices=unmatched_gt
        )