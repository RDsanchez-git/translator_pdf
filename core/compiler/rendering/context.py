import logging
from dataclasses import dataclass
from typing import Mapping
from core.ast.models import ContentNodeType
from core.document_profile.models import InferredDocumentProfile, PageLayout
from core.compiler.rendering.models import RenderUnit, RenderingConfiguration
from core.compiler.rendering.policies import DocumentStructurePolicy, RenderStrategy
from core.compiler.rendering.implementations import (
    DynamicDocumentStructure, TextRenderStrategy, 
    PassthroughRenderStrategy, AdaptiveFloatStrategy
)

logger = logging.getLogger(__name__)

@dataclass(frozen=True, slots=True)
class RenderContext:
    structure: DocumentStructurePolicy
    strategies: Mapping[ContentNodeType, RenderStrategy]
    fallback_strategy: RenderStrategy

    def render_unit(self, unit: RenderUnit) -> str:
        strategy = self.strategies.get(unit.node_type, self.fallback_strategy)
        return strategy.render(unit)

class RenderContextFactory:
    @classmethod
    def create(cls, profile: InferredDocumentProfile) -> RenderContext:
        logger.info(f"Instanciando RenderContext. Layout inferido: {profile.layout}")
        
        config = RenderingConfiguration(
            is_multi_column=(profile.layout == PageLayout.DOUBLE_COLUMN)
        )
        
        structure = DynamicDocumentStructure(config)
        text_strategy = TextRenderStrategy()
        passthrough_strategy = PassthroughRenderStrategy()
        float_strategy = AdaptiveFloatStrategy(config)

        strategies_map = {
            ContentNodeType.PARAGRAPH: text_strategy,
            ContentNodeType.HEADING: text_strategy,
            ContentNodeType.LIST: text_strategy,
            ContentNodeType.CAPTION: text_strategy,
            
            ContentNodeType.DISPLAY_EQUATION: passthrough_strategy,
            ContentNodeType.INLINE_EQUATION: passthrough_strategy,
            ContentNodeType.TABLE_SIMPLE: passthrough_strategy,
            ContentNodeType.TABLE_COMPLEX: passthrough_strategy,
            ContentNodeType.CODE: passthrough_strategy,
            ContentNodeType.COMPOSITE_BLOCK: passthrough_strategy,
            
            ContentNodeType.IMAGE: float_strategy
        }

        return RenderContext(
            structure=structure,
            strategies=strategies_map,
            fallback_strategy=text_strategy
        )