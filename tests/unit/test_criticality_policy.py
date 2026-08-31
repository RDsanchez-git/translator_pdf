"""
Tests unitarios de NodeCriticality y DefaultCriticalityPolicy.

Verifica:
- Cobertura exhaustiva de los 11 ContentNodeType
- Fallo explícito ante tipo sin clasificación (extensibilidad)
- Inmutabilidad del enum
- Orden de declaración
- NADR-18 §5.1 R1, R2; §5.2 R9
"""
from __future__ import annotations

import pytest

from core.ast.enums import ContentNodeType

from core.benchmark.topology.criticality.models import NodeCriticality
from core.benchmark.topology.criticality.policy import (
    DefaultCriticalityPolicy,
    _CRITICALITY_MAP,
)


class TestNodeCriticalityEnum:
    """Tests del enum NodeCriticality."""

    def test_exactly_three_levels(self):
        """NADR-18 §5.1 R2: Exactamente tres niveles."""
        members = list(NodeCriticality)
        assert len(members) == 3

    def test_canonical_values(self):
        """Los valores canónicos son CRITICAL, WARNING, INFO."""
        assert NodeCriticality.CRITICAL == "CRITICAL"
        assert NodeCriticality.WARNING == "WARNING"
        assert NodeCriticality.INFO == "INFO"

    def test_str_subclass(self):
        """Es str subclass para serialización y comparación."""
        assert isinstance(NodeCriticality.CRITICAL, str)
        assert NodeCriticality.CRITICAL == "CRITICAL"

    def test_immutable(self):
        """El enum es inmutable."""
        with pytest.raises(AttributeError):
            NodeCriticality.CRITICAL = "MODIFIED"  # type: ignore[misc]

    def test_hashable(self):
        """Es hashable para uso en sets y dicts."""
        test_set = {NodeCriticality.CRITICAL, NodeCriticality.WARNING, NodeCriticality.INFO}
        assert len(test_set) == 3

    def test_declaration_order(self):
        """El orden de declaración es CRITICAL > WARNING > INFO."""
        members = list(NodeCriticality)
        assert members[0] == NodeCriticality.CRITICAL
        assert members[1] == NodeCriticality.WARNING
        assert members[2] == NodeCriticality.INFO


class TestDefaultCriticalityPolicy:
    """Tests de DefaultCriticalityPolicy."""

    @pytest.fixture
    def policy(self) -> DefaultCriticalityPolicy:
        return DefaultCriticalityPolicy()

    def test_critical_nodes(self, policy: DefaultCriticalityPolicy):
        """NADR-18 §5.1 R3: DISPLAY_EQUATION, INLINE_EQUATION, TABLE_SIMPLE, TABLE_COMPLEX son CRITICAL."""
        critical_types = [
            ContentNodeType.DISPLAY_EQUATION,
            ContentNodeType.INLINE_EQUATION,
            ContentNodeType.TABLE_SIMPLE,
            ContentNodeType.TABLE_COMPLEX,
        ]
        for node_type in critical_types:
            assert policy.criticality_of(node_type) == NodeCriticality.CRITICAL, (
                f"{node_type.value} should be CRITICAL"
            )

    def test_warning_nodes(self, policy: DefaultCriticalityPolicy):
        """NADR-18 §5.1 R4: HEADING, PARAGRAPH, CODE son WARNING."""
        warning_types = [
            ContentNodeType.HEADING,
            ContentNodeType.PARAGRAPH,
            ContentNodeType.CODE,
        ]
        for node_type in warning_types:
            assert policy.criticality_of(node_type) == NodeCriticality.WARNING, (
                f"{node_type.value} should be WARNING"
            )

    def test_info_nodes(self, policy: DefaultCriticalityPolicy):
        """NADR-18 §5.1 R5: IMAGE, CAPTION, LIST, COMPOSITE_BLOCK son INFO."""
        info_types = [
            ContentNodeType.IMAGE,
            ContentNodeType.CAPTION,
            ContentNodeType.LIST,
            ContentNodeType.COMPOSITE_BLOCK,
        ]
        for node_type in info_types:
            assert policy.criticality_of(node_type) == NodeCriticality.INFO, (
                f"{node_type.value} should be INFO"
            )

    def test_exhaustive_coverage(self, policy: DefaultCriticalityPolicy):
        """NADR-18 §5.1 R1: Todo ContentNodeType tiene clasificación."""
        for node_type in ContentNodeType:
            result = policy.criticality_of(node_type)
            assert isinstance(result, NodeCriticality), (
                f"{node_type.value} has no classification"
            )

    def test_deterministic(self, policy: DefaultCriticalityPolicy):
        """Mismo input → mismo output (determinismo)."""
        for node_type in ContentNodeType:
            first = policy.criticality_of(node_type)
            second = policy.criticality_of(node_type)
            assert first == second

    def test_unknown_type_raises_value_error(self, policy: DefaultCriticalityPolicy):
        """NADR-18 §5.2 R9: Fallo explícito ante tipo sin clasificación."""
        original_map = _CRITICALITY_MAP.copy()
        import core.benchmark.topology.criticality.policy as policy_module
        try:
            policy_module._CRITICALITY_MAP = {}
            
            with pytest.raises(ValueError, match="no.*classification|has no criticality"):
                policy.criticality_of(ContentNodeType.PARAGRAPH)
        finally:
            policy_module._CRITICALITY_MAP = original_map

    def test_all_classified_types_returns_frozenset(self, policy: DefaultCriticalityPolicy):
        """all_classified_types() retorna un frozenset inmutable."""
        result = policy.all_classified_types()
        assert isinstance(result, frozenset)
        assert len(result) == len(ContentNodeType)