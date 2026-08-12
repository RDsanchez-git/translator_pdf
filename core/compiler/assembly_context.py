# core/compiler/assembly_context.py
"""
Contexto de ensamblado físico (NADR-06 §5.3).

VO inmutable que transporta evidencia validada del Execution Plane.
La validación es responsabilidad de CQRSAssemblyContextResolver.

Invariantes de estrategia:
- TRANSLATE: espera ProjectionRecord. Si falta → fallback.
- PASSTHROUGH / KEEP_ORIGINAL: puede faltar ProjectionRecord → fallback original.
- OMIT: excluido del contexto. No participa del ensamblado.

missing_node_ids = nodos ensamblables sin materialización CURRENT.
NO significa "traducciones faltantes". Incluye PASSTHROUGH sin proyección.
"""
from dataclasses import dataclass
from typing import Tuple
from core.ast.models import ASTNode
from core.execution.ports import ProjectionRecord


@dataclass(frozen=True)
class AssemblyExecutionContext:
    """
    Contenedor inmutable de evidencia validada para ensamblado.

    Precondiciones (garantizadas por el resolver):
    - ast_nodes ordenado por sequence_id
    - ast_nodes excluye nodos con strategy == OMIT
    - ast_nodes tiene node_id únicos
    - projections contiene solo materializaciones CURRENT
    - document_id + ast_hash forman la clave compuesta de identidad
    """
    document_id: str
    ast_hash: str
    ast_nodes: Tuple[ASTNode, ...]
    projections: Tuple[ProjectionRecord, ...]
    projection_version: int

    @property
    def expected_node_ids(self) -> frozenset[str]:
        """Identidad topológica esperada según el AST canónico (sin OMIT)."""
        return frozenset(node.node_id for node in self.ast_nodes)

    @property
    def materialized_node_ids(self) -> frozenset[str]:
        """Identidad materializada según el plano CQRS."""
        return frozenset(proj.node_id for proj in self.projections)

    @property
    def missing_node_ids(self) -> frozenset[str]:
        """
        Nodos ensamblables sin materialización CURRENT.
        Incluye TRANSLATE sin proyección y PASSTHROUGH sin proyección.
        """
        return self.expected_node_ids - self.materialized_node_ids