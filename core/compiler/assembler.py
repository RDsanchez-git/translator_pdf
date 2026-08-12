import time
from enum import Enum
from typing import Optional, Protocol, FrozenSet, Tuple
from dataclasses import dataclass, field
# SOTA FIX: Importación de DispatchResult agregada
from core.ast.models import FailureReason, ASTNode
from core.execution.exceptions import IncompleteDocumentError
from core.compiler.assembly_context import AssemblyExecutionContext

class RepositoryUnavailableError(Exception):
    """Excepción transitoria: Falla de red, timeout o inaccesibilidad del medio físico."""
    pass

class PayloadNotFoundError(Exception):
    """Excepción fatal: El registro no existe en el repositorio."""
    pass

class HashMismatchError(Exception):
    """Excepción fatal: Corrupción silenciosa, el payload materializado no coincide con la firma."""
    pass

class IntegrityCheckedDocumentRepository(Protocol):
    def get_verified_payload(self, job_id: str, chunk_id: str, expected_sha256: str) -> str: ...

class AssemblyStatus(str, Enum):
    SUCCESS = "success"
    DEGRADED = "degraded"
    REJECTED = "rejected"

@dataclass(frozen=True, slots=True)
class AssemblyPolicy:
    """SOTA: Motor de políticas con control granular de degradación."""
    tolerance_ratio: float = 0.0
    allow_fallback: bool = False
    degradable_failures: FrozenSet[FailureReason] = field(default_factory=frozenset)

@dataclass(frozen=True, slots=True)
class AssemblyReport:
    """
    DTO inmutable para telemetría persistente del plano de ensamblado.

    NADR-06 §5.3: Semántica explícita.
    - total_nodes: total de nodos ensamblables (excluyendo OMIT)
    - missing_projection_nodes: nodos sin proyección CURRENT (usaron fallback)
    """
    timestamp: float
    total_nodes: int
    missing_projection_nodes: int
    failure_reasons: dict
    degradation_applied: bool
    assembler_version: str = "v16.0.0-SOTA"

@dataclass(frozen=True, slots=True)
class DocumentAssemblyDecision:
    """
    Decisión estructural del ensamblado.

    NADR-06 §5.3: El Assembler decide política, NO reconstruye contenido.
    La materialización de RenderUnits es responsabilidad de CompilationService.
    """
    status: AssemblyStatus
    missing_node_ids: Tuple[str, ...]
    rejection_reason: Optional[str]
    audit_report: AssemblyReport

    @property
    def is_accepted(self) -> bool:
        return self.status in (AssemblyStatus.SUCCESS, AssemblyStatus.DEGRADED)

class DocumentAssembler:
    """SOTA: Motor de Ensamblado que delega la validación de integridad al repositorio."""
    
    def __init__(self, repository: IntegrityCheckedDocumentRepository, separator: str = "", policy: Optional[AssemblyPolicy] = None):
        self.repository = repository
        self.separator = separator
        self.policy = policy or AssemblyPolicy()
    
    def _validate_sequence(self, document_id: str, nodes: tuple[ASTNode, ...]) -> None:
        """Valida que la secuencia de nodos sea contigua desde 1."""
        if not nodes:
            return
        expected_seq = 1
        for node in nodes:
            if node.sequence_id != expected_seq:
                raise IncompleteDocumentError(
                    document_id=document_id,
                    expected=expected_seq,
                    actual=node.sequence_id
                )
            expected_seq += 1

    def assemble(self, context: AssemblyExecutionContext) -> DocumentAssemblyDecision:
        ast_nodes = context.ast_nodes
        projections = context.projections

        if not ast_nodes:
            return self._build_rejection("AST vacío.", (), 0)

        # Mapear proyecciones por node_id
        projection_map = {p.node_id for p in projections}
        total_nodes = len(ast_nodes)
        missing_nodes = [n for n in ast_nodes if n.node_id not in projection_map]
        missing_ratio = len(missing_nodes) / total_nodes if total_nodes > 0 else 1.0
        missing_node_ids = tuple(n.node_id for n in missing_nodes)

        # Aplicar política de tolerancia
        if missing_ratio > self.policy.tolerance_ratio:
            return self._build_rejection(
                f"Missing ratio {missing_ratio:.2%} excede umbral de {self.policy.tolerance_ratio:.2%}",
                missing_node_ids,
                total_nodes  # ← total_nodes real, no len(missing)
            )

        if missing_nodes and not self.policy.allow_fallback:
            return self._build_rejection(
                f"Tolerancia admitida ({missing_ratio:.2%}), pero allow_fallback=False prohíbe ensamblado.",
                missing_node_ids,
                total_nodes  # ← total_nodes real
            )

        status = AssemblyStatus.DEGRADED if missing_nodes else AssemblyStatus.SUCCESS

        report = AssemblyReport(
            timestamp=time.time(),
            total_nodes=total_nodes,
            missing_projection_nodes=len(missing_nodes),
            failure_reasons={"missing_projection": len(missing_nodes)} if missing_nodes else {},
            degradation_applied=bool(missing_nodes)
        )

        return DocumentAssemblyDecision(
            status=status,
            missing_node_ids=missing_node_ids,
            rejection_reason=None,
            audit_report=report
        )

    def _build_rejection(
        self,
        reason: str,
        missing_node_ids: Tuple[str, ...],
        total_nodes: int,
    ) -> DocumentAssemblyDecision:
        """
        Construye una decisión de rechazo con telemetría correcta.

        NADR-06 §5.3: total_nodes representa el total de nodos ensamblables,
        NO la cantidad de nodos faltantes.
        """
        report = AssemblyReport(
            timestamp=time.time(),
            total_nodes=total_nodes,
            missing_projection_nodes=len(missing_node_ids),
            failure_reasons={"missing_projection": len(missing_node_ids)} if missing_node_ids else {},
            degradation_applied=False
        )
        return DocumentAssemblyDecision(
            status=AssemblyStatus.REJECTED,
            missing_node_ids=missing_node_ids,
            rejection_reason=reason,
            audit_report=report
        )