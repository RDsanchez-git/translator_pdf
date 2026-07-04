from typing import List, Dict, Any, Tuple
from core.domain.document import DocumentLayout, LayoutPage, PageDimensions, PageOrientation, DocumentProfile, DocumentType
from core.layout.base import LayoutStage, PipelineContext, ProviderDescriptor, PipelineConfig
from core.execution.exceptions import PipelineIntegrityError

class DocumentLayoutBuilder:
    def __init__(
        self, 
        source_path: str, 
        pipeline: Tuple[LayoutStage[Any, Any], ...],
        config: PipelineConfig,
        document_type: DocumentType = DocumentType.PAPER
    ):
        self._source_path = source_path
        self._pipeline = pipeline
        self._config = config
        self._document_type = document_type
        self._validate_pipeline_composition()

    def _validate_pipeline_composition(self) -> None:
        if not self._pipeline:
            raise PipelineIntegrityError("La tubería del LayoutBuilder no contiene etapas secuenciales.")
            
        for i in range(len(self._pipeline) - 1):
            current_stage = self._pipeline[i]
            next_stage = self._pipeline[i + 1]
            
            # SOTA: Validación basada en polimorfismo estructural (subclases)
            if not issubclass(current_stage.OUTPUT_TYPE, next_stage.INPUT_TYPE):
                raise PipelineIntegrityError(
                    f"Ruptura de Contrato de Tipos: La etapa '{current_stage.stage_name}' "
                    f"produce '{current_stage.OUTPUT_TYPE.__name__}', pero la etapa "
                    f"'{next_stage.stage_name}' exige un subtipo compatible con '{next_stage.INPUT_TYPE.__name__}'."
                )

    def build(self, raw_pages_data: List[Dict[str, Any]], provider_desc: ProviderDescriptor, execution_id: str) -> DocumentLayout:
        processed_pages: List[LayoutPage] = []

        for page_data in raw_pages_data:
            p_width = page_data["width"]
            p_height = page_data["height"]
            page_num = page_data["page_number"]
            
            orientation = PageOrientation.PORTRAIT if p_height >= p_width else PageOrientation.LANDSCAPE
            dimensions = PageDimensions(width=p_width, height=p_height, orientation=orientation)
            
            current_payload = page_data.get("raw_blocks", [])
            
            # Recorrido indexado para traza inequívoca
            for idx, stage in enumerate(self._pipeline):
                context = PipelineContext(
                    execution_id=execution_id,
                    provider=provider_desc,
                    config=self._config,
                    page_number=page_num,
                    page_width=p_width,
                    page_height=p_height
                )
                current_payload = stage.process(current_payload, context, stage_index=idx)
                
            processed_pages.append(LayoutPage(
                page_number=page_num,
                dimensions=dimensions,
                blocks=current_payload
            ))

        return DocumentLayout(
            source_path=self._source_path,
            total_pages=len(processed_pages),
            profile=DocumentProfile(document_type=self._document_type, primary_language="en"),
            pages=processed_pages
        )