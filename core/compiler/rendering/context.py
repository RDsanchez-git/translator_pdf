import logging
from dataclasses import dataclass
from typing import Mapping
from core.ast.models import ContentNodeType
from core.document_profile.models import InferredDocumentProfile, PageLayout, SamplingCoverage
from core.compiler.rendering.models import RenderUnit, RenderingConfiguration
from core.compiler.rendering.policies import DocumentStructurePolicy, RenderStrategy
from core.compiler.rendering.implementations import (
    DynamicDocumentStructure, TextRenderStrategy, 
    PassthroughRenderStrategy, LiteralProtectedRenderStrategy,
    UnclassifiedMixedRenderStrategy, AdaptiveFloatStrategy
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
        
        evidence = profile.physical_diagnostics
        layout_accredited = (
            evidence is not None
            and evidence.sampling_coverage == SamplingCoverage.STRICT_SCOPE
            and not evidence.geometry_reasons
        )
        if not layout_accredited:
            logger.warning(
                "PPPR_G2_LAYOUT_UNVERIFIED coverage=%s; renderizado conservador de una columna",
                evidence.sampling_coverage.value if evidence is not None else "LEGACY_UNKNOWN",
            )
        config = RenderingConfiguration(
            is_multi_column=(profile.layout == PageLayout.DOUBLE_COLUMN and layout_accredited)
        )
        
        structure = DynamicDocumentStructure(config)
        text_strategy = TextRenderStrategy()
        passthrough_strategy = PassthroughRenderStrategy()
        literal_strategy = LiteralProtectedRenderStrategy()
        unclassified_mixed_strategy = UnclassifiedMixedRenderStrategy()
        float_strategy = AdaptiveFloatStrategy(config)

        strategies_map = {
            ContentNodeType.PARAGRAPH: text_strategy,
            ContentNodeType.HEADING: text_strategy,
            ContentNodeType.LIST: text_strategy,
            ContentNodeType.CAPTION: text_strategy,
            
            ContentNodeType.DISPLAY_EQUATION: passthrough_strategy,
            ContentNodeType.INLINE_EQUATION: passthrough_strategy,
            ContentNodeType.TABLE_SIMPLE: literal_strategy,
            ContentNodeType.TABLE_COMPLEX: literal_strategy,
            ContentNodeType.CODE: literal_strategy,
            ContentNodeType.COMPOSITE_BLOCK: unclassified_mixed_strategy,
            
            ContentNodeType.IMAGE: float_strategy
        }

        return RenderContext(
            structure=structure,
            strategies=strategies_map,
            fallback_strategy=text_strategy
        )