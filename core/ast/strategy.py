import logging
from typing import Dict, Final
from core.ast.enums import ContentNodeType, TranslationStrategy

logger = logging.getLogger(__name__)

# Matriz inmutable de enrutamiento base (Nivel de módulo - Funcional Puro)
_STRATEGY_MAP: Final[Dict[ContentNodeType, TranslationStrategy]] = {
    ContentNodeType.HEADING: TranslationStrategy.TRANSLATE,
    ContentNodeType.PARAGRAPH: TranslationStrategy.TRANSLATE,
    ContentNodeType.LIST: TranslationStrategy.TRANSLATE,
    ContentNodeType.TABLE_SIMPLE: TranslationStrategy.TRANSLATE,
    ContentNodeType.CAPTION: TranslationStrategy.TRANSLATE,
    
    ContentNodeType.DISPLAY_EQUATION: TranslationStrategy.PASSTHROUGH,
    ContentNodeType.INLINE_EQUATION: TranslationStrategy.PASSTHROUGH,
    ContentNodeType.TABLE_COMPLEX: TranslationStrategy.PASSTHROUGH,
    ContentNodeType.IMAGE: TranslationStrategy.PASSTHROUGH,
    ContentNodeType.CODE: TranslationStrategy.PASSTHROUGH,
    ContentNodeType.COMPOSITE_BLOCK: TranslationStrategy.PASSTHROUGH,
}

# NOTA DE DISEÑO SEGURO: Si aparece un tipo estructural desconocido, el fallback más
# pragmático es PASSTHROUGH. No destruye información ni altera el formato crudo del archivo.
_DEFAULT_STRATEGY: Final[TranslationStrategy] = TranslationStrategy.PASSTHROUGH

def resolve_strategy(node_type: ContentNodeType) -> TranslationStrategy:
    """SOTA: Determina de forma funcional y puramente determinística la estrategia 
    de traducción de un nodo a partir de su tipo lógico en tiempo constante O(1)."""
    
    # Alerta SRE: Control de anomalías estructurales
    if node_type == ContentNodeType.COMPOSITE_BLOCK:
        logger.warning(
            "[AST-002] [COMPOSITE_BLOCK_REACHED] Anomalía en el parser. Un bloque mixto "
            "ha alcanzado la fase de resolución de estrategias sin ser desensamblado. "
            "Forzando contención mediante PASSTHROUGH."
        )

    if node_type not in _STRATEGY_MAP:
        # SRE Guardrail: Identificador indexable para sistemas de alertas masivas (Datadog/ELK)
        logger.warning(
            f"[AST-001] [UNMAPPED_NODE_TYPE] El tipo lógico '{node_type}' carece de una "
            f"estrategia explícita. Ejecutando fallback defensivo a: {_DEFAULT_STRATEGY.value}."
        )
        return _DEFAULT_STRATEGY
        
    return _STRATEGY_MAP[node_type]