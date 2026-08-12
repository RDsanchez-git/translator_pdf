# core/compiler/context_resolver.py
"""
Resolver de contexto de ensamblado desde el Execution Plane (CQRS).

NADR-06 §5.3 R9-R12: El ensamblado debe ser recuperable exclusivamente
desde el plano de ejecución.

Responsabilidades del Resolver:
- Cargar AST vía ASTProviderProtocol
- Filtrar nodos OMIT
- Validar unicidad de node_id
- Obtener proyecciones CURRENT vía MaterializedPlanePort
- Detectar evidencia válida (missing, duplicate)

NO es responsabilidad del Resolver:
- Decidir tolerancia o degradación (pertenece al Assembler)
- Renderizar o compilar (pertenece a CompilationService)
"""
import logging
from core.ast.enums import TranslationStrategy
from core.compiler.ports import ASTProviderProtocol
from core.execution.ports import MaterializedPlanePort
from core.compiler.assembly_context import AssemblyExecutionContext
from core.compiler.exceptions import ASTConsistencyError

logger = logging.getLogger(__name__)


class AssemblyContextResolutionError(Exception):
    """Fallo en la resolución del contexto de ensamblado."""
    pass


class CQRSAssemblyContextResolver:
    """
    Construye AssemblyExecutionContext desde el Execution Plane.

    NADR-06 §5.3: Este resolver es el único punto donde el ensamblado
    físico accede a la evidencia durable del plano de ejecución.

    Invariantes verificadas:
    - AST existe y no es vacío
    - AST node_id único (sin duplicados)
    - Nodos OMIT excluidos
    - Sin proyecciones duplicadas
    """

    def __init__(
        self,
        ast_provider: ASTProviderProtocol,
        materialized_plane: MaterializedPlanePort,
    ):
        self._ast_provider = ast_provider
        self._materialized = materialized_plane

    def resolve(
        self,
        document_id: str,
        ast_hash: str,
        projection_version: int = 1,
    ) -> AssemblyExecutionContext:
        log_ctx = {"document_id": document_id[:12], "ast_hash": ast_hash[:12]}

        # Paso 1: Cargar AST vía puerto canónico
        ast_nodes = self._ast_provider.get_document_ast(document_id, ast_hash)
        if not ast_nodes:
            raise ASTConsistencyError(
                f"AST vacío o no disponible para {document_id}"
            )

        # Paso 2: Ordenar por sequence_id (topología canónica)
        sorted_nodes = sorted(ast_nodes, key=lambda n: n.sequence_id)

        # Paso 3: Validar unicidad de node_id
        node_ids = [node.node_id for node in sorted_nodes]
        if len(node_ids) != len(set(node_ids)):
            seen = set()
            duplicates = set()
            for nid in node_ids:
                if nid in seen:
                    duplicates.add(nid)
                seen.add(nid)
            raise ASTConsistencyError(
                f"AST contiene node_id duplicados para {document_id}: {duplicates}"
            )

        # Paso 4: VALIDAR TOPOLOGÍA COMPLETA (antes del filtro OMIT)
        # La continuidad 1..N se verifica sobre el AST completo.
        # Los gaps de OMIT son legales porque el nodo existe en el AST.
        self._validate_full_topology(document_id, sorted_nodes)

        # Paso 5: Filtrar nodos OMIT (después de validar topología)
        assemblable_nodes = tuple(
            node for node in sorted_nodes
            if node.strategy != TranslationStrategy.OMIT
        )

        if not assemblable_nodes:
            raise AssemblyContextResolutionError(
                f"Todos los nodos del documento {document_id} son OMIT. Nada que ensamblar."
            )

        omitted_count = len(sorted_nodes) - len(assemblable_nodes)
        if omitted_count > 0:
            logger.info(
                "ASSEMBLY_OMIT_NODES_EXCLUDED",
                extra={"extra_data": {**log_ctx, "omitted_count": omitted_count}}
            )

        # Paso 6: Obtener proyecciones CURRENT
        expected_node_ids = [node.node_id for node in assemblable_nodes]
        projections = self._materialized.get_assemblable_chunks(
            document_id=document_id,
            ast_hash=ast_hash,
            expected_node_ids=expected_node_ids,
            required_projection_v=projection_version,
        )
        projection_tuple = tuple(projections)

        # Paso 7: Verificar proyecciones duplicadas
        node_id_counts = {}
        for p in projection_tuple:
            node_id_counts[p.node_id] = node_id_counts.get(p.node_id, 0) + 1
        dup_projections = {nid for nid, count in node_id_counts.items() if count > 1}
        if dup_projections:
            raise AssemblyContextResolutionError(
                f"Proyecciones duplicadas detectadas para {document_id}: {dup_projections}"
            )

        # Paso 8: Log de missing (el Assembler decide tolerancia)
        expected_set = frozenset(expected_node_ids)
        materialized_set = frozenset(p.node_id for p in projection_tuple)
        missing = expected_set - materialized_set

        if missing:
            logger.info(
                "ASSEMBLY_MISSING_PROJECTIONS",
                extra={"extra_data": {
                    **log_ctx,
                    "missing_count": len(missing),
                    "missing_node_ids": sorted(missing),
                }}
            )

        # Paso 9: Construir contexto inmutable
        return AssemblyExecutionContext(
            document_id=document_id,
            ast_hash=ast_hash,
            ast_nodes=assemblable_nodes,
            projections=projection_tuple,
            projection_version=projection_version,
        )

    def _validate_full_topology(self, document_id: str, sorted_nodes: list) -> None:
        """
        Valida que la secuencia del AST completo sea contigua desde 1.
        Se ejecuta ANTES del filtro OMIT para que los gaps de OMIT sean legales.
        """
        expected_seq = 1
        for node in sorted_nodes:
            if node.sequence_id != expected_seq:
                raise ASTConsistencyError(
                    f"Topología AST inconsistente para {document_id}: "
                    f"esperado sequence_id={expected_seq}, encontrado={node.sequence_id} "
                    f"(node_id={node.node_id})"
                )
            expected_seq += 1