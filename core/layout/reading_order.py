import heapq
import logging
from typing import Type, Any, List, Dict, Set, Tuple
from collections import defaultdict
from core.layout.base import LayoutStage, PipelineContext, ReadingOrderPolicy
from core.layout.models import LayoutBlockCollection, LayoutBlockDraft
from core.domain.document import BlockId
from core.telemetry.ports import StageExecutionRecord

logger = logging.getLogger(__name__)

class ReadingOrderResolver(LayoutStage[LayoutBlockCollection, LayoutBlockCollection]):
    INPUT_TYPE: Type[Any] = LayoutBlockCollection
    OUTPUT_TYPE: Type[Any] = LayoutBlockCollection

    # Jerarquía estática de quiebre de ciclos para mitigar degradaciones del OCR
    TYPE_PRIORITY: Dict[str, int] = {
        "TITLE": 0,
        "DISPLAY_EQUATION": 1,
        "CODE": 2,
        "PARAGRAPH": 3
    }

    @property
    def stage_name(self) -> str:
        return "reading_order_resolver"

    @property
    def supports_parallel_execution(self) -> bool:
        return False

    def _execute(self, data: LayoutBlockCollection, context: PipelineContext) -> LayoutBlockCollection:
        blocks = data.blocks
        if len(blocks) < 2:
            return data

        policy = context.config.reading_policy
        
        # 1. Preparar estructuras gobernadas exclusivamente por BlockId (Value Object)
        id_to_block: Dict[BlockId, LayoutBlockDraft] = {}
        adjacency_graph: Dict[BlockId, Set[BlockId]] = defaultdict(set)
        in_degree: Dict[BlockId, int] = {}

        # Ordenamiento de barrido inicial por cota superior Y0
        sorted_working_list = sorted(blocks, key=lambda b: b.bbox.y0)

        for block in sorted_working_list:
            if not block.block_id:
                continue
            b_id = block.block_id
            id_to_block[b_id] = block
            in_degree[b_id] = 0

        # 2. SOTA: Sweep-Line Estricto con Mantenimiento de Active Set
        active_set: List[LayoutBlockDraft] = []
        
        for b_curr in sorted_working_list:
            b_curr_id = b_curr.block_id
            if not b_curr_id:
                continue

            # Desalojar del Active Set bloques que han quedado completamente rezagados detrás de la línea de barrido
            active_set = [
                b for b in active_set 
                if b.bbox.y1 + policy.inter_column_y_slack >= b_curr.bbox.y0
            ]

            # Evaluar restricciones cruzadas exclusivamente contra el set activo optimizado
            for b_active in active_set:
                b_active_id = b_active.block_id
                if not b_active_id or b_active_id == b_curr_id:
                    continue

                if self._eval_precedence(b_active, b_curr, policy):
                    if b_curr_id not in adjacency_graph[b_active_id]:
                        adjacency_graph[b_active_id].add(b_curr_id)

                if self._eval_precedence(b_curr, b_active, policy):
                    if b_active_id not in adjacency_graph[b_curr_id]:
                        adjacency_graph[b_curr_id].add(b_active_id)

            active_set.append(b_curr)

        # Validar y consolidar los grados de entrada del DAG resultante
        for targets in adjacency_graph.values():
            for target in targets:
                in_degree[target] += 1

        # 3. Validación de integridad perimetral preventiva del DAG
        self._validate_dag_integrity(adjacency_graph, in_degree)

        # 4. Algoritmo de Kahn Puro mediante Heap Compuesto O(n log n) sin Sorts Internos
        priority_queue: List[Tuple[int, float, float, str, BlockId]] = []
        for nid, degree in in_degree.items():
            if degree == 0:
                b = id_to_block[nid]
                # Estructura de tupla autocomparable inmutable para indexación interna del Heap
                heapq.heappush(priority_queue, (b.column_index or 0, b.bbox.y0, b.bbox.x0, b.content[:10], nid))

        sorted_ids: List[BlockId] = []
        while priority_queue:
            # SOTA: Garantiza coste logarítmico puro delegando el ordenamiento al motor binario nativo
            _, _, _, _, current_id = heapq.heappop(priority_queue)
            sorted_ids.append(current_id)

            for neighbor in adjacency_graph[current_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    nb = id_to_block[neighbor]
                    heapq.heappush(priority_queue, (nb.column_index or 0, nb.bbox.y0, nb.bbox.x0, nb.content[:10], neighbor))

        # 5. Gestión Avanzada de Ciclos con Quiebre por Tipado Semántico y Emisión de Telemetría
        cyclic_ids: Set[BlockId] = set(in_degree.keys()) - set(sorted_ids)
        if cyclic_ids:
            self._emit_cycle_telemetry(context, len(cyclic_ids))
            
            # Quiebre de ciclos jerárquico: prioridad lógica del tipo -> columna -> coordenadas físicas
            fallback_sorted = sorted(
                [id_to_block[rid] for rid in cyclic_ids],
                key=lambda b: (self.TYPE_PRIORITY.get(b.logical_type or "PARAGRAPH", 4), b.column_index or 0, b.bbox.y0, b.bbox.x0)
            )
            ordered_blocks = [id_to_block[sid] for sid in sorted_ids] + fallback_sorted
        else:
            ordered_blocks = [id_to_block[sid] for sid in sorted_ids]

        # 6. Serialización final libre de efectos secundarios
        final_blocks = []
        for seq_idx, block in enumerate(ordered_blocks):
            history_update = block.merge_history
            if context.config.custom_policies.get("ENABLE_AUDIT_LOGS", True):
                status_flag = "DEGRADED_CYCLIC" if block.block_id in cyclic_ids else "STABLE"
                history_update = history_update + [f"READING_ORDER: index={seq_idx} | status={status_flag}"]

            final_blocks.append(block.model_copy(update={
                "merge_history": history_update
            }))

        return LayoutBlockCollection(blocks=final_blocks)

    def _validate_dag_integrity(self, graph: Dict[BlockId, Set[BlockId]], in_degree: Dict[BlockId, int]) -> None:
        """Garantiza defensivamente la ausencia de auto-bucles y la paridad de nodos en el grafo."""
        for node, edges in graph.items():
            if node in edges:
                edges.remove(node)
                if node in in_degree:
                    in_degree[node] = max(0, in_degree[node] - 1)

    def _emit_cycle_telemetry(self, context: PipelineContext, cyclic_count: int) -> None:
        """Notifica de forma atómica la anomalía estructural hacia el perímetro de observabilidad remoto."""
        logger.warning(f"[RUPTURA_DAG] Ciclo espacial detectado en página {context.page_number}. Nodos: {cyclic_count}.")
        try:
            record = StageExecutionRecord(
                execution_id=context.execution_id,
                stage_name=self.stage_name,
                stage_index=99,
                latency_sec=0.0,
                input_type="LayoutBlockCollection",
                output_type="LayoutBlockCollection",
                status="DEGRADED",
                error_message=f"Ciclo Topológico interceptado. Nodos comprometidos: {cyclic_count}",
                metadata={"page_number": context.page_number, "cyclic_nodes": cyclic_count}
            )
            self._telemetry.record_execution(record)
        except Exception as e:
            logger.error(f"Fallo crítico al inyectar registro en el puerto de telemetría: {str(e)}")

    def _eval_precedence(self, b1: LayoutBlockDraft, b2: LayoutBlockDraft, policy: ReadingOrderPolicy) -> bool:
        if b1.column_index == b2.column_index:
            return b1.bbox.y1 <= b2.bbox.y0 + policy.vertical_overlap_tolerance
            
        if b1.bbox.width >= policy.spanning_width_threshold and b1.column_index == 0:
            return b1.bbox.y1 <= b2.bbox.y0 + policy.vertical_overlap_tolerance
            
        if b2.bbox.width >= policy.spanning_width_threshold and b2.bbox.y0 >= policy.spanning_footer_y_anchor:
            return b1.bbox.y1 <= b2.bbox.y0 + policy.vertical_overlap_tolerance
            
        if b1.column_index is not None and b2.column_index is not None:
            if b1.column_index < b2.column_index:
                return b1.bbox.y0 < b2.bbox.y1 + policy.inter_column_y_slack
                
        return False