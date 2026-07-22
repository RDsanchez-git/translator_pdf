from typing import Sequence, Tuple, Optional
from dataclasses import dataclass
from core.ast.models import ASTNode
from core.benchmark.topology.ports import AnchorPartitionStrategy
from core.benchmark.topology.models import AlignmentResult, EvaluationWindow, EvaluationForest, AnchorCorrespondence

@dataclass(frozen=True)
class PartitionBoundary:
    """Encapsula los límites numéricos absolutos de corte para un segmento del AST."""
    c_start: int
    c_end: int
    gt_start: int
    gt_end: int
    leading_anchor: Optional[AnchorCorrespondence]


class HeadingAnchorPartitionStrategy(AnchorPartitionStrategy):
    """
    Segmentador topológico puro basado en intervalos secuenciales semiabiertos.
    Garantiza la partición exhaustiva del AST en una única pasada lineal O(n).
    """
    def partition(
        self, 
        candidate_ast: Sequence[ASTNode], 
        ground_truth_ast: Sequence[ASTNode],
        alignment: AlignmentResult
    ) -> Tuple[EvaluationWindow, ...]:
        
        # 1. Extraer los límites lógicos de corte en tupla inmutable nativa
        boundaries = self._compute_boundaries(alignment, len(candidate_ast), len(ground_truth_ast))
        
        # 2. Proyectar los límites directamente sobre Value Objects de dominio mediante slicing O(1)
        return tuple(
            EvaluationWindow(
                window_index=idx,
                candidate=EvaluationForest(nodes=tuple(candidate_ast[b.c_start:b.c_end])),
                ground_truth=EvaluationForest(nodes=tuple(ground_truth_ast[b.gt_start:b.gt_end])),
                leading_anchor=b.leading_anchor
            )
            for idx, b in enumerate(boundaries)
        )

    def _compute_boundaries(
        self, 
        alignment: AlignmentResult, 
        c_len: int, 
        gt_len: int
    ) -> Tuple[PartitionBoundary, ...]:
        if not alignment.matches:
            return (PartitionBoundary(0, c_len, 0, gt_len, None),)

        boundaries: list[PartitionBoundary] = []
        c_start, gt_start = 0, 0
        current_leading_anchor: Optional[AnchorCorrespondence] = None

        for match in alignment.matches:
            c_end = match.candidate_ast_index
            gt_end = match.ground_truth_ast_index

            # El intervalo [start, end) incluye el anclaje inicial (leading anchor) 
            # y se extiende capturando el contenido jerárquico hasta antes del siguiente anclaje.
            boundaries.append(
                PartitionBoundary(
                    c_start=c_start,
                    c_end=c_end,
                    gt_start=gt_start,
                    gt_end=gt_end,
                    leading_anchor=current_leading_anchor
                )
            )
            
            c_start = c_end
            gt_start = gt_end
            current_leading_anchor = match

        # Captura determinista de la ventana residual de cola del documento
        boundaries.append(
            PartitionBoundary(
                c_start=c_start,
                c_end=c_len,
                gt_start=gt_start,
                gt_end=gt_len,
                leading_anchor=current_leading_anchor
            )
        )
        return tuple(boundaries)