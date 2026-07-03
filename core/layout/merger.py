from typing import Type, Any, List, Tuple, Dict
from core.layout.base import LayoutStage, PipelineContext, MergePolicy
from core.layout.models import LayoutBlockCollection, LayoutBlockDraft
from core.domain.document import BoundingBox

class SpatialMerger(LayoutStage[LayoutBlockCollection, LayoutBlockCollection]):
    INPUT_TYPE: Type[Any] = LayoutBlockCollection
    OUTPUT_TYPE: Type[Any] = LayoutBlockCollection

    # Matriz estática de transición para resolver la degradación de tipos lógicos mixtos
    TYPE_TRANSITION_MATRIX: Dict[Tuple[str, str], str] = {
        ("TITLE", "PARAGRAPH"): "PARAGRAPH",
        ("PARAGRAPH", "TITLE"): "PARAGRAPH",
        ("DISPLAY_EQUATION", "PARAGRAPH"): "PARAGRAPH",
        ("PARAGRAPH", "DISPLAY_EQUATION"): "PARAGRAPH",
        ("CODE", "PARAGRAPH"): "PARAGRAPH",
        ("PARAGRAPH", "CODE"): "PARAGRAPH"
    }

    @property
    def stage_name(self) -> str:
        return "spatial_merger"

    @property
    def supports_parallel_execution(self) -> bool:
        return False

    def _execute(self, data: LayoutBlockCollection, context: PipelineContext) -> LayoutBlockCollection:
        blocks = data.blocks
        if len(blocks) < 2:
            return data

        policy = context.config.merge_policy
        pivots = context.config.spatial_pivots
        primary_pivot = pivots[0] if pivots else 0.45
        
        # SOTA: Estabilización del flujo de entrada mediante pre-sort por carriles de columna (X) y altura (Y)
        working_blocks = sorted(
            blocks, 
            key=lambda b: (1 if b.bbox.x0 > primary_pivot else 0, b.bbox.y0)
        )
        
        merged_blocks: List[LayoutBlockDraft] = []
        i = 0
        while i < len(working_blocks):
            current = working_blocks[i]
            
            while i + 1 < len(working_blocks):
                candidate = working_blocks[i + 1]
                
                is_compatible, score, reason = self._evaluate_merge_affinity(current, candidate, policy)
                
                if is_compatible and score >= self._get_strategy_threshold(policy.strategy):
                    current = self._fuse_blocks(current, candidate, score, reason)
                    i += 1
                else:
                    # Registrar el motivo del rechazo en el historial para auditoría/explainability
                    current = current.model_copy(update={
                        "merge_history": current.merge_history + [f"REJECTED [{candidate.block_id.value if candidate.block_id else 'None'}]: {reason}"]
                    })
                    break
            
            merged_blocks.append(current)
            i += 1

        return LayoutBlockCollection(blocks=merged_blocks)

    def _evaluate_merge_affinity(self, b1: LayoutBlockDraft, b2: LayoutBlockDraft, policy: MergePolicy) -> Tuple[bool, float, str]:
        v_gap = b2.bbox.y0 - b1.bbox.y1
        
        # Obtener el límite vertical específico según el tipo lógico del bloque base
        max_v_threshold = policy.type_thresholds.get(b1.logical_type, policy.vertical_threshold) if b1.logical_type else policy.vertical_threshold
        
        if v_gap < -0.01:
            return False, 0.0, f"Overlapping inverso detectado o bloque fuera de secuencia vertical (v_gap: {v_gap:.4f})"
        if v_gap > (max_v_threshold * 1.5):
            return False, 0.0, f"Distancia vertical excede el umbral de tipo '{b1.logical_type}' (v_gap: {v_gap:.4f} > {max_v_threshold * 1.5})"

        # Cálculo de Solapamiento Horizontal (Intersection over Minimum Width en eje X)
        x0_max = max(b1.bbox.x0, b2.bbox.x0)
        x1_min = min(b1.bbox.x1, b2.bbox.x1)
        overlap_width = max(0.0, x1_min - x0_max)
        
        b1_w = b1.bbox.x1 - b1.bbox.x0
        b2_w = b2.bbox.x1 - b2.bbox.x0
        min_w = min(b1_w, b2_w)
        
        horiz_overlap_ratio = (overlap_width / min_w) if min_w > 0 else 0.0
        align_delta = abs(b1.bbox.x0 - b2.bbox.x0)

        # Evaluación de la Función de Costo Inversa Parametrizada
        v_score = max(0.0, 1.0 - (max(0.0, v_gap) / max_v_threshold))
        h_score = horiz_overlap_ratio
        a_score = max(0.0, 1.0 - (align_delta / 0.05))

        total_score = (v_score * policy.v_weight) + (h_score * policy.h_weight) + (a_score * policy.a_weight)
        
        # Validación estricta de invariantes horizontales de columna
        is_valid = horiz_overlap_ratio >= policy.horizontal_overlap or align_delta <= 0.02
        
        if not is_valid:
            return False, total_score, f"Alineación horizontal rota. Overlap: {horiz_overlap_ratio:.2f}, Delta Izquierdo: {align_delta:.4f}"
            
        return True, total_score, f"Afinidad válida detectada bajo peso paramétrico. Score: {total_score:.3f}"

    def _get_strategy_threshold(self, strategy: str) -> float:
        mapping = {"STRICT": 0.85, "BALANCED": 0.65, "AGGRESSIVE": 0.45}
        return mapping.get(strategy.upper(), 0.65)

    def _fuse_blocks(self, b1: LayoutBlockDraft, b2: LayoutBlockDraft, score: float, reason: str) -> LayoutBlockDraft:
        fused_bbox = BoundingBox(
            x0=min(b1.bbox.x0, b2.bbox.x0),
            y0=min(b1.bbox.y0, b2.bbox.y0),
            x1=max(b1.bbox.x1, b2.bbox.x1),
            y1=max(b1.bbox.y1, b2.bbox.y1),
            is_normalized=True
        )

        join_char = "\n" if b1.logical_type in ("CODE", "DISPLAY_EQUATION") else " "
        fused_content = f"{b1.content}{join_char}{b2.content}"
        
        # Resolución determinística del tipo lógico resultante vía Matriz de Transición
        t1, t2 = b1.logical_type or "PARAGRAPH", b2.logical_type or "PARAGRAPH"
        resolved_type = t1 if t1 == t2 else self.TYPE_TRANSITION_MATRIX.get((t1, t2), t1)

        # Concatenación del registro de auditoría interno
        c2_id = b2.block_id.value if b2.block_id else "None"
        new_history = b1.merge_history + [f"FUSED CON [{c2_id}] | Score: {score:.3f} | Motivo: {reason}"]

        return b1.model_copy(update={
            "bbox": fused_bbox,
            "content": fused_content,
            "logical_type": resolved_type,
            "confidence": min(b1.confidence, b2.confidence),
            "merge_history": new_history
        })