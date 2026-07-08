# core/pipeline/workflow.py
import logging
from enum import StrEnum
from dataclasses import dataclass
from collections.abc import Iterator
from typing import Iterable
from core.ast.models import ASTNode
from core.routing.protocols import NodeRouter
from core.routing.models import RouteChannel
from core.pipeline.protocols import PassthroughSink

logger = logging.getLogger(__name__)

class RoutingEvents(StrEnum):
    COMPLETED = "routing.workflow.completed"
    # Preparado para expansión: FAILED = "routing.workflow.failed", etc.

@dataclass(slots=True)
class RoutingMetrics:
    translated: int = 0
    passthrough: int = 0
    omitted: int = 0

class RoutingWorkflow:
    """Orquestador Imperativo para la bifurcación del AST (Back-Pressure Nativo)."""

    def __init__(self, router: NodeRouter, passthrough_sink: PassthroughSink):
        self._router = router
        self._passthrough_sink = passthrough_sink

    def stream_translate_channel(self, nodes: Iterable[ASTNode]) -> Iterator[ASTNode]:
        metrics = RoutingMetrics()

        for node in nodes:
            channel = self._router.route(node)

            match channel:
                case RouteChannel.TRANSLATE:
                    metrics.translated += 1
                    yield node
                
                case RouteChannel.PASSTHROUGH:
                    metrics.passthrough += 1
                    self._passthrough_sink.sink(node)
                
                case RouteChannel.OMIT:
                    metrics.omitted += 1

        logger.info(
            "Routing stage completed",
            extra={
                "event_id": RoutingEvents.COMPLETED,
                "metrics": {
                    "translated": metrics.translated,
                    "passthrough": metrics.passthrough,
                    "omitted": metrics.omitted
                }
            }
        )