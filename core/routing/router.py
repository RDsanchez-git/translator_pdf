from typing import Final, Mapping
from core.ast.models import ASTNode
from core.ast.enums import TranslationStrategy
from core.routing.models import RouteChannel

class StrategyRouter:
    """
    SOTA: Enrutador declarativo determinista en tiempo constante O(1).
    Función pura disfrazada de objeto. No decide estrategias, únicamente las interpreta.
    """

    # Inmutabilidad estática garantizada a nivel del Type-Checker (mypy/pyright)
    _ROUTING_TABLE: Final[Mapping[TranslationStrategy, RouteChannel]] = {
        TranslationStrategy.TRANSLATE: RouteChannel.TRANSLATE,
        TranslationStrategy.PASSTHROUGH: RouteChannel.PASSTHROUGH,
        TranslationStrategy.KEEP_ORIGINAL: RouteChannel.PASSTHROUGH,
        TranslationStrategy.OMIT: RouteChannel.OMIT,
    }

    def route(self, node: ASTNode) -> RouteChannel:
        """
        Deriva el canal basándose estrictamente en la estrategia del nodo.
        Política Fail-Open (SRE): Estrategias anómalas derivan a TRANSLATE para evitar
        pérdida silenciosa de información de misión crítica.
        """
        return self._ROUTING_TABLE.get(node.strategy, RouteChannel.TRANSLATE)