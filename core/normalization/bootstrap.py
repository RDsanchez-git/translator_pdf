import logging
import importlib.util
from core.ast.enums import ContentNodeType  # SOTA FIX: Importación desde enums de la Fase 16
from core.normalization.registry import NormalizationPolicyRegistry, NormalizationPolicy, NormalizationDomain
from core.normalization.fixers.paragraph_normalizer import ParagraphNormalizer
from core.normalization.fixers.math_pipeline import MathDomainNormalizer

logger = logging.getLogger(__name__)

def bootstrap_normalization_layer() -> None:
    """Inicializa, vincula tipos a dominios lógicos y congela la DNL."""
    registry = NormalizationPolicyRegistry.get_instance()
    
    if registry.is_bootstrapped:
        logger.debug("DNL Registry is already bootstrapped. Bypassing.")
        return

    if importlib.util.find_spec("lxml") is None:
        raise RuntimeError("CRITICAL: lxml parser is required by DNL.")

    # 1. Política de Texto (Dominio TRANSLATE)
    paragraph_policy = NormalizationPolicy(policy_id="TRANSLATE_TEXT_POLICY")
    paragraph_policy.append(ParagraphNormalizer())
    registry.register_policy(NormalizationDomain.TEXT, paragraph_policy)
    
    # SOTA FIX: Alineación estricta con tipos semánticos reales vigentes en AST V2
    registry.map_type_to_domain(ContentNodeType.PARAGRAPH.value, NormalizationDomain.TEXT)
    registry.map_type_to_domain(ContentNodeType.LIST.value, NormalizationDomain.TEXT)
    registry.map_type_to_domain(ContentNodeType.HEADING.value, NormalizationDomain.TEXT)
    registry.map_type_to_domain(ContentNodeType.CAPTION.value, NormalizationDomain.TEXT)

    # 2. Política Matemática (Dominio PRESERVE)
    math_policy = NormalizationPolicy(policy_id="PRESERVE_MATH_POLICY")
    math_policy.append(MathDomainNormalizer())
    registry.register_policy(NormalizationDomain.MATH, math_policy)
    
    # SOTA FIX: Enrutamiento explícito hacia las especializaciones algebraicas
    registry.map_type_to_domain(ContentNodeType.DISPLAY_EQUATION.value, NormalizationDomain.MATH)
    registry.map_type_to_domain(ContentNodeType.INLINE_EQUATION.value, NormalizationDomain.MATH)
    registry.map_type_to_domain(ContentNodeType.CODE.value, NormalizationDomain.MATH)

    registry.freeze()
    logger.info("DNL Hardened Layer bootstrapped successfully via canonical values.")