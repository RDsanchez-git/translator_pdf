import hashlib
from typing import Type, Any
from core.layout.base import LayoutStage, PipelineContext
from core.layout.models import LayoutBlockCollection
from core.domain.document import BlockId, BoundingBox


class BlockIdentityGenerator(LayoutStage[LayoutBlockCollection, LayoutBlockCollection]):
    INPUT_TYPE: Type[Any] = LayoutBlockCollection
    OUTPUT_TYPE: Type[Any] = LayoutBlockCollection

    @property
    def stage_name(self) -> str:
        return "block_identity_generator"

    @property
    def supports_parallel_execution(self) -> bool:
        return True

    def _execute(self, data: LayoutBlockCollection, context: PipelineContext) -> LayoutBlockCollection:
        page_num = context.page_number
        provider_name = context.provider.name
        precision = context.config.coordinate_precision
        
        identified_list = []
        for idx, block in enumerate(data.blocks):
            block_seed_id = block.provider_native_id if block.provider_native_id else f"idx{idx}"
            
            # El contenido ya viene sanitizado desde el origen; no se altera aquí
            seed_string = self._build_seed(
                provider_name, page_num, block_seed_id, block.bbox, block.content, precision
            )
            
            sha256_hash = hashlib.sha256(seed_string.encode("utf-8")).hexdigest()
            
            identified_list.append(block.model_copy(
                update={"block_id": BlockId(value=sha256_hash)}
            ))
            
        return LayoutBlockCollection(blocks=identified_list)

    def _build_seed(self, provider: str, page: int, block_id: str, bbox: BoundingBox, content: str, precision: int) -> str:
        """Garantiza la estabilidad del hash aplicando la precisión declarada en la configuración."""
        dx0 = round(bbox.x0, precision)
        dy0 = round(bbox.y0, precision)
        dx1 = round(bbox.x1, precision)
        dy1 = round(bbox.y1, precision)
        
        return f"{provider}_p{page}_{block_id}_[{dx0:.{precision}f},{dy0:.{precision}f},{dx1:.{precision}f},{dy1:.{precision}f}]_{content}"