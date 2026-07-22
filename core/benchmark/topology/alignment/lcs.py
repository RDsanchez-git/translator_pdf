from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class AnchorMatch:
    """Value Object que representa un emparejamiento de índices discretos."""
    candidate_index: int
    ground_truth_index: int

@dataclass(frozen=True)
class SequenceAlignmentResult:
    """Contenedor inmutable de las coordenadas discretas resultantes del alineamiento."""
    aligned_pairs: Tuple[AnchorMatch, ...]
    unmatched_candidate_indices: Tuple[int, ...]
    unmatched_ground_truth_indices: Tuple[int, ...]