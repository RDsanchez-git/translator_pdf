"""
Modelos de dominio del subsistema de criticidad de nodos (NADR-F17BIS-18 §5.1).

Este módulo define la taxonomía de criticidad que clasifica los nodos del AST
según su impacto científico en la evaluación topológica de regresión.

La taxonomía tiene exactamente tres niveles (NADR-18 §5.1 R2):
- CRITICAL: pérdida inaceptable independientemente del NSS
- WARNING: pérdida tolerable bajo umbrales configurables
- INFO: pérdida observable sin impacto en el veredicto

Esta clasificación es ortogonal al contenido específico del nodo:
depende exclusivamente de su tipo estructural (ContentNodeType).
"""
from __future__ import annotations

from enum import Enum


class NodeCriticality(str, Enum):
    """Taxonomía de criticidad de nodos para regresión topológica graduada.

    Cada nivel define el impacto científico de la pérdida de un nodo
    durante la evaluación del runtime contra el oráculo sellado.

    Levels:
        CRITICAL: Nodos cuya pérdida constituye un HARD_FAIL absoluto,
            independientemente del Normalized Structural Score (NSS).
            La pérdida de un solo nodo CRITICAL invalida la evaluación.
            Ejemplos: ecuaciones display, ecuaciones inline, tablas.

        WARNING: Nodos cuya pérdida se evalúa contra umbrales configurables.
            Pérdidas aisladas MAY emitirse como PASS con observación.
            Pérdidas que superan el umbral configuran un WARNING.
            Ejemplos: headings, paragraphs, code blocks.

        INFO: Nodos cuya pérdida se registra como observación sin impacto
            en el veredicto. MUST NOT causar un veredicto de fallo.
            Ejemplos: imágenes, captions, listas, bloques compuestos.

    NADR-18 §5.1 R2: Exactamente tres niveles.
    NADR-18 §5.1 R6: Declarativa, centralizada y extensible.
    """

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"