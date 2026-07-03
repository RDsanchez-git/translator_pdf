from typing import Type, Any, Tuple
from core.layout.base import LayoutStage, PipelineContext
from core.layout.models import LayoutBlockCollection
from core.domain.document import BoundingBox
from core.execution.exceptions import LayoutRecoveryError

class CoordinateNormalizer(LayoutStage[LayoutBlockCollection, LayoutBlockCollection]):
    INPUT_TYPE: Type[Any] = LayoutBlockCollection
    OUTPUT_TYPE: Type[Any] = LayoutBlockCollection

    @property
    def stage_name(self) -> str:
        return "coordinate_normalizer"

    @property
    def supports_parallel_execution(self) -> bool:
        return True

    def _execute(self, data: LayoutBlockCollection, context: PipelineContext) -> LayoutBlockCollection:
        page_w = context.page_width
        page_h = context.page_height
        
        if page_w <= 0 or page_h <= 0:
            raise LayoutRecoveryError(
                message=f"Frontera Ingesta Interceptada: Dimensiones inválidas {page_w}x{page_h}",
                provider_name=context.provider.name,
                pdf_path="ContextStream"
            )
            
        normalized_list = []
        for block in data.blocks:
            nx0, ny0, nx1, ny1 = self._scale_and_clamp(block.bbox, page_w, page_h)
            normalized_bbox = BoundingBox(x0=nx0, y0=ny0, x1=nx1, y1=ny1, is_normalized=True)
            
            normalized_list.append(block.model_copy(update={"bbox": normalized_bbox}))
            
        return LayoutBlockCollection(blocks=normalized_list)

    def _scale_and_clamp(self, bbox: BoundingBox, width: float, height: float) -> Tuple[float, float, float, float]:
        """Función pura aislada para pruebas unitarias de proyección geométrica."""
        nx0 = max(0.0, min(float(bbox.x0) / width, 1.0))
        ny0 = max(0.0, min(float(bbox.y0) / height, 1.0))
        nx1 = max(0.0, min(float(bbox.x1) / width, 1.0))
        ny1 = max(0.0, min(float(bbox.y1) / height, 1.0))
        return nx0, ny0, nx1, ny1