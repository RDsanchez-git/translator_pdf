import logging
import importlib.util
from core.ast.models import ContentNodeType
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

    # Corrección Ruff F401: Verificación estática de lxml sin importación huérfana
    if importlib.util.find_spec("lxml") is None:
        raise RuntimeError("CRITICAL: lxml parser is required by DNL.")

    # 1. Política de Texto (Dominio TRANSLATE)
    paragraph_policy = NormalizationPolicy(policy_id="TRANSLATE_TEXT_POLICY")
    paragraph_policy.append(ParagraphNormalizer())
    registry.register_policy(NormalizationDomain.TEXT, paragraph_policy)
    
    # Consolidación completa de mapeos estables (.value) para evitar bypass de nodos
    registry.map_type_to_domain(ContentNodeType.PARAGRAPH.value, NormalizationDomain.TEXT)
    registry.map_type_to_domain(ContentNodeType.LIST.value, NormalizationDomain.TEXT)
    registry.map_type_to_domain(ContentNodeType.LIST_ITEM.value, NormalizationDomain.TEXT)
    registry.map_type_to_domain(ContentNodeType.CAPTION.value, NormalizationDomain.TEXT)
    registry.map_type_to_domain(ContentNodeType.FOOTNOTE.value, NormalizationDomain.TEXT)
    registry.map_type_to_domain(ContentNodeType.MACRO_CHUNK.value, NormalizationDomain.TEXT)

    # 2. Política Matemática (Dominio PRESERVE)
    math_policy = NormalizationPolicy(policy_id="PRESERVE_MATH_POLICY")
    math_policy.append(MathDomainNormalizer())  # El Facade abstrae los micro-módulos
    registry.register_policy(NormalizationDomain.MATH, math_policy)
    
    # Enrutamiento estricto de nodos algebraicos hacia el Facade sin estado
    registry.map_type_to_domain(ContentNodeType.EQUATION.value, NormalizationDomain.MATH)
    registry.map_type_to_domain(ContentNodeType.INLINE_EQUATION.value, NormalizationDomain.MATH)
    registry.map_type_to_domain(ContentNodeType.ALGORITHM.value, NormalizationDomain.MATH)

    registry.freeze()
    logger.info("DNL Hardened Layer bootstrapped successfully via canonical values.")