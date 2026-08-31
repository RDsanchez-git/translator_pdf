"""
Tests unitarios de CriticalityAwareCostContext.

Verifica:
- Determinismo (mismos inputs → mismo costo)
- Orden estricto CRITICAL > WARNING > INFO
- Configuración de pesos
- Integración con ZhangShashaEngine sin modificarlo
- NADR-18 §5.3 R12, R15
"""
from __future__ import annotations

import pytest

from core.ast.enums import ContentNodeType, TranslationStrategy
from core.ast.models import ASTNode, ParagraphPayload, HeadingPayload, MathPayload

from core.benchmark.topology.criticality.costs import (
    CriticalityAwareCostContext,
    DEFAULT_CRITICALITY_WEIGHTS,
)
from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.criticality.policy import DefaultCriticalityPolicy


def _make_node(
    node_id: str,
    node_type: ContentNodeType,
    content: str = "test content",
) -> ASTNode:
    """Helper para crear ASTNode de prueba."""
    payload_map = {
        ContentNodeType.PARAGRAPH: ParagraphPayload(content=content),
        ContentNodeType.HEADING: HeadingPayload(content=content),
        ContentNodeType.DISPLAY_EQUATION: MathPayload(content=content),
        ContentNodeType.INLINE_EQUATION: MathPayload(content=content),
    }
    payload = payload_map.get(node_type, ParagraphPayload(content=content))
    return ASTNode(
        node_id=node_id,
        node_type=node_type,
        strategy=TranslationStrategy.TRANSLATE,
        payload=payload,
    )


class TestCriticalityAwareCostContext:
    """Tests de CriticalityAwareCostContext."""

    @pytest.fixture
    def context(self) -> CriticalityAwareCostContext:
        return CriticalityAwareCostContext()

    @pytest.fixture
    def custom_context(self) -> CriticalityAwareCostContext:
        custom_weights = {
            NodeCriticality.CRITICAL: 10.0,
            NodeCriticality.WARNING: 3.0,
            NodeCriticality.INFO: 0.5,
        }
        return CriticalityAwareCostContext(weights=custom_weights)

    def test_determinism_deletion(self, context: CriticalityAwareCostContext):
        """NADR-18 §5.3 R12: Mismo nodo → mismo costo de eliminación."""
        node = _make_node("n1", ContentNodeType.PARAGRAPH)
        first = context.deletion_cost(node)
        second = context.deletion_cost(node)
        assert first == second

    def test_determinism_insertion(self, context: CriticalityAwareCostContext):
        """NADR-18 §5.3 R12: Mismo nodo → mismo costo de inserción."""
        node = _make_node("n1", ContentNodeType.HEADING)
        first = context.insertion_cost(node)
        second = context.insertion_cost(node)
        assert first == second

    def test_strict_order_deletion(self, context: CriticalityAwareCostContext):
        """NADR-18 §5.3 R14: CRITICAL > WARNING > INFO en penalización."""
        critical_node = _make_node("c1", ContentNodeType.DISPLAY_EQUATION)
        warning_node = _make_node("w1", ContentNodeType.PARAGRAPH)
        info_node = _make_node("i1", ContentNodeType.IMAGE)

        critical_cost = context.deletion_cost(critical_node)
        warning_cost = context.deletion_cost(warning_node)
        info_cost = context.deletion_cost(info_node)

        assert critical_cost > warning_cost > info_cost

    def test_strict_order_insertion(self, context: CriticalityAwareCostContext):
        """NADR-18 §5.3 R14: CRITICAL > WARNING > INFO en penalización."""
        critical_node = _make_node("c1", ContentNodeType.TABLE_SIMPLE)
        warning_node = _make_node("w1", ContentNodeType.HEADING)
        info_node = _make_node("i1", ContentNodeType.LIST)

        critical_cost = context.insertion_cost(critical_node)
        warning_cost = context.insertion_cost(warning_node)
        info_cost = context.insertion_cost(info_node)

        assert critical_cost > warning_cost > info_cost

    def test_substitution_identical_type_and_content_zero_cost(
        self, context: CriticalityAwareCostContext
    ):
        """Sustitución con mismo tipo Y contenido → costo 0.0."""
        node_a = _make_node("a", ContentNodeType.PARAGRAPH, content="same text")
        node_b = _make_node("b", ContentNodeType.PARAGRAPH, content="same text")

        assert context.substitution_cost(node_a, node_b) == 0.0

    def test_substitution_same_content_different_type_not_zero(
        self, context: CriticalityAwareCostContext
    ):
        """Sustitución con mismo contenido pero diferente tipo → costo > 0.0."""
        paragraph_node = _make_node("p", ContentNodeType.PARAGRAPH, content="same text")
        heading_node = _make_node("h", ContentNodeType.HEADING, content="same text")

        cost = context.substitution_cost(paragraph_node, heading_node)
        assert cost > 0.0

    def test_substitution_different_content_uses_max_criticality(
        self, context: CriticalityAwareCostContext
    ):
        """Sustitución con contenido diferente → costo = max(criticidades)."""
        critical_node = _make_node("c", ContentNodeType.DISPLAY_EQUATION, content="E=mc2")
        info_node = _make_node("i", ContentNodeType.IMAGE, content="[img]")

        cost = context.substitution_cost(critical_node, info_node)
        expected = DEFAULT_CRITICALITY_WEIGHTS[NodeCriticality.CRITICAL]
        assert cost == expected

    def test_substitution_symmetric(self, context: CriticalityAwareCostContext):
        """La sustitución es simétrica: costo(A,B) == costo(B,A)."""
        node_a = _make_node("a", ContentNodeType.DISPLAY_EQUATION, content="text1")
        node_b = _make_node("b", ContentNodeType.PARAGRAPH, content="text2")

        cost_ab = context.substitution_cost(node_a, node_b)
        cost_ba = context.substitution_cost(node_b, node_a)
        assert cost_ab == cost_ba

    def test_custom_weights(self, custom_context: CriticalityAwareCostContext):
        """NADR-18 §5.3 R13: Pesos configurables mediante inyección."""
        critical_node = _make_node("c", ContentNodeType.DISPLAY_EQUATION)
        warning_node = _make_node("w", ContentNodeType.PARAGRAPH)
        info_node = _make_node("i", ContentNodeType.IMAGE)

        assert custom_context.deletion_cost(critical_node) == 10.0
        assert custom_context.deletion_cost(warning_node) == 3.0
        assert custom_context.deletion_cost(info_node) == 0.5

    def test_missing_weight_raises(self):
        """Pesos incompletos → ValueError."""
        incomplete_weights = {
            NodeCriticality.CRITICAL: 5.0,
            NodeCriticality.WARNING: 2.0,
            # Falta INFO
        }
        with pytest.raises(ValueError, match="Missing weights"):
            CriticalityAwareCostContext(weights=incomplete_weights)

    def test_weights_property_returns_copy(self, context: CriticalityAwareCostContext):
        """La propiedad weights retorna una copia, no la referencia interna."""
        weights = context.weights
        weights[NodeCriticality.CRITICAL] = 999.0
        # El contexto interno no debe verse afectado
        node = _make_node("n", ContentNodeType.DISPLAY_EQUATION)
        assert context.deletion_cost(node) == DEFAULT_CRITICALITY_WEIGHTS[NodeCriticality.CRITICAL]

    def test_default_policy_used_when_none(self):
        """Si no se inyecta policy, usa DefaultCriticalityPolicy."""
        context = CriticalityAwareCostContext(policy=None)
        assert isinstance(context.policy, DefaultCriticalityPolicy)

    def test_implements_tree_edit_cost_context_protocol(
        self, context: CriticalityAwareCostContext
    ):
        """Verifica que implementa el protocolo TreeEditCostContext."""
        from core.benchmark.topology.ports import TreeEditCostContext

        assert isinstance(context, TreeEditCostContext)