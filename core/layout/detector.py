from typing import Type, Any, List, Dict
from core.layout.base import LayoutStage, PipelineContext
from core.layout.models import LayoutBlockCollection, LayoutBlockDraft

class SpatialAnalyzer(LayoutStage[LayoutBlockCollection, LayoutBlockCollection]):
    """Sub-etapa de la Fase 16.1: Analiza la topología bidimensional mediante perfiles de 
    proyección horizontal adaptativos, segmentación estadística y pesos lógicos de exclusión."""

    INPUT_TYPE: Type[Any] = LayoutBlockCollection
    OUTPUT_TYPE: Type[Any] = LayoutBlockCollection

    # SOTA: Matriz de ponderación para mitigar la contaminación por bloques transversales (Spanning Blocks)
    TYPE_WEIGHTS: Dict[str, float] = {
        "PARAGRAPH": 1.0,
        "LIST": 1.0,
        "DISPLAY_EQUATION": 0.7,
        "CODE": 0.8,
        "TITLE": 0.2,    # Títulos largos transversales reducen su impacto
        "TABLE": 0.0,    # Exclusión absoluta: Las tablas spanning no destruyen el histograma
        "IMAGE": 0.0     # Exclusión absoluta: Las figuras spanning no alteran las columnas
    }

    @property
    def stage_name(self) -> str:
        return "spatial_analyzer"

    @property
    def supports_parallel_execution(self) -> bool:
        return True

    def _execute(self, data: LayoutBlockCollection, context: PipelineContext) -> LayoutBlockCollection:
        blocks = data.blocks
        if not blocks:
            return data

        # 1. Resolución adaptativa de Bins (Regla Sturges-Steward acotada)
        bin_resolution = max(100, min(512, int(len(blocks) * 3.5)))
        histogram = [0.0] * bin_resolution

        # 2. Construcción de la Proyección Horizontal Ponderada
        for block in blocks:
            weight = self.TYPE_WEIGHTS.get(block.logical_type or "PARAGRAPH", 1.0)
            if weight == 0.0:
                continue

            start_bin = max(0, min(int(block.bbox.x0 * bin_resolution), bin_resolution - 1))
            end_bin = max(0, min(int(block.bbox.x1 * bin_resolution), bin_resolution - 1))
            
            # Masa proyectada modulada por el peso del tipo lógico
            projected_mass = block.bbox.height * weight
            
            for b in range(start_bin, end_bin + 1):
                histogram[b] += projected_mass

        # 3. Análisis Estadístico del Perfil (Detección Multipolar de Canales)
        mean_density = sum(histogram) / bin_resolution
        max_peak = max(histogram)
        
        # Localizar canales divisorios (valles significativos que caen por debajo de la media local)
        gutters_x = self._detect_gutters(histogram, bin_resolution, mean_density, max_peak)

        # 4. Clasificación y Asignación de Carriles de Columna Heterogéneos (1, 2 o más columnas)
        analyzed_blocks: List[LayoutBlockDraft] = []
        for block in blocks:
            # Determinar el índice de columna contando cuántos canales divisorios cruza su centroide
            assigned_column = 0
            block_center = block.bbox.center_x
            
            for gutter in gutters_x:
                if block_center > gutter:
                    assigned_column += 1

            # El historial de fusión opera de forma condicional para preservar memoria en producción
            history_update = block.merge_history
            if context.config.custom_policies.get("ENABLE_AUDIT_LOGS", True):
                history_update = history_update + [
                    f"SPATIAL: cols={len(gutters_x) + 1} | gutters={str([round(g,3) for g in gutters_x])} | assigned={assigned_column}"
                ]

            analyzed_blocks.append(block.model_copy(update={
                "column_index": assigned_column,
                "merge_history": history_update
            }))

        return LayoutBlockCollection(blocks=analyzed_blocks)

    def _detect_gutters(self, histogram: List[float], resolution: int, mean: float, max_peak: float) -> List[float]:
        """Localiza todos los valles estadísticamente significativos aplicando umbrales de densidad dinámicos."""
        if max_peak <= 0.001:
            return []

        gutters_x: List[float] = []
        
        # Ignorar márgenes perimetrales extremos (15% izquierdo y derecho) para evadir falsos positivos
        start_search = int(0.15 * resolution)
        end_search = int(0.85 * resolution)
        
        # Umbral adaptativo: El valle debe ser menor que la densidad media y representar una caída severa respecto al pico
        density_threshold = min(mean * 0.5, max_peak * 0.12)
        
        in_valley = False
        valley_bins: List[int] = []

        for i in range(start_search, end_search):
            if histogram[i] <= density_threshold:
                if not in_valley:
                    in_valley = True
                valley_bins.append(i)
            else:
                if in_valley:
                    # Fin del canal divisorio: Calcular el centro geográfico del valle local
                    if valley_bins:
                        center_bin = valley_bins[len(valley_bins) // 2]
                        gutters_x.append(center_bin / resolution)
                    valley_bins = []
                    in_valley = False
                    
        # Capturar valle residual si termina en la frontera de búsqueda
        if in_valley and valley_bins:
            center_bin = valley_bins[len(valley_bins) // 2]
            gutters_x.append(center_bin / resolution)

        # Filtrar micro-valles adyacentes espurios (Gutter Width Mínimo del 3% del ancho de página)
        return self._filter_spurious_gutters(gutters_x)

    def _filter_spurious_gutters(self, gutters: List[float]) -> List[float]:
        if len(gutters) < 2:
            return sorted(gutters)
            
        filtered = []
        gutters.sort()
        
        i = 0
        while i < len(gutters):
            current = gutters[i]
            # Combinar valles colindantes si se encuentran a menos de 0.04 de distancia vertical/horizontal
            while i + 1 < len(gutters) and (gutters[i + 1] - current) < 0.04:
                current = (current + gutters[i + 1]) / 2.0
                i += 1
            filtered.append(current)
            i += 1
            
        return filtered