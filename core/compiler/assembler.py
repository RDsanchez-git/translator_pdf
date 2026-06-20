import time
from enum import Enum
from typing import List, Optional, Protocol, FrozenSet
from collections import Counter
from dataclasses import dataclass, field

# SOTA FIX: Importación de DispatchResult agregada
from core.ast.models import ReconstructedDocument, ChunkOutcome, ExecutionStatus, FailureReason, DispatchResult
from core.execution.exceptions import IncompleteDocumentError

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
    """SOTA: DTO inmutable para telemetría persistente (Grafana/DataDog)."""
    timestamp: float
    total_chunks: int
    total_failed: int
    failure_reasons: dict
    degradation_applied: bool
    assembler_version: str = "v15.4.0-SOTA"

@dataclass(frozen=True, slots=True)
class DocumentAssemblyDecision:
    status: AssemblyStatus
    document: Optional[ReconstructedDocument]
    failed_outcomes: List[ChunkOutcome]
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

    def _validate_sequence(self, outcomes: List[ChunkOutcome]) -> None:
        if not outcomes:
            return

        indexes = [o.chunk_index for o in outcomes]
        if len(set(indexes)) != len(indexes):
            raise ValueError("Duplicate chunk_index detected in Outcomes")

        expected_index = 1
        for outcome in outcomes:
            if outcome.chunk_index != expected_index:
                raise IncompleteDocumentError(
                    document_id=outcome.chunk_id, 
                    expected=expected_index, 
                    actual=outcome.chunk_index
                )
            expected_index += 1

    def assemble(self, job_id: str, dispatch_result: DispatchResult) -> DocumentAssemblyDecision:
        outcomes = dispatch_result.outcomes
        if not outcomes:
            return self._build_rejection("Lista de outcomes vacía.", [])

        sorted_outcomes = sorted(outcomes, key=lambda x: x.chunk_index)
        self._validate_sequence(sorted_outcomes)

        total_chunks = len(sorted_outcomes)
        failed_outcomes = [o for o in sorted_outcomes if not o.is_success]
        failure_ratio = len(failed_outcomes) / total_chunks if total_chunks > 0 else 1.0

        if failure_ratio > self.policy.tolerance_ratio:
            return self._build_rejection(
                f"Failure ratio {failure_ratio:.2%} excede umbral de {self.policy.tolerance_ratio:.2%}",
                failed_outcomes
            )

        if failed_outcomes and not self.policy.allow_fallback:
            return self._build_rejection(
                f"Tolerancia admitida ({failure_ratio:.2%}), pero allow_fallback=False prohíbe ensamblado.",
                failed_outcomes
            )

        for outcome in failed_outcomes:
            if outcome.failure_reason not in self.policy.degradable_failures:
                # SOTA FIX: Type-safe property access
                reason_val = outcome.failure_reason.value if outcome.failure_reason else "UNKNOWN_ERROR"
                return self._build_rejection(
                    f"Fallo no degradable detectado: {reason_val} en chunk {outcome.chunk_id}",
                    failed_outcomes
                )

        content_parts = []
        translated_count = 0
        passthrough_count = 0
        total_input = 0
        total_output = 0

        for outcome in sorted_outcomes:
            if outcome.status == ExecutionStatus.SUCCESS and outcome.translated_unit:
                unit = outcome.translated_unit
                content_parts.append(unit.translated_payload)
                if unit.chunk_type == "translate":
                    translated_count += 1
                else:
                    passthrough_count += 1
                total_input += unit.input_tokens
                total_output += unit.output_tokens
            else:
                try:
                    # SOTA FIX: Inyección limpia del job_id recibido por parámetro
                    verified_payload = self.repository.get_verified_payload(
                        job_id, 
                        outcome.chunk_id, 
                        outcome.original_payload_sha256
                    )
                    content_parts.append(verified_payload)
                    passthrough_count += 1
                except (PayloadNotFoundError, HashMismatchError) as e:
                    return self._build_rejection(f"Falla de integridad referencial: {str(e)}", failed_outcomes)
                except RepositoryUnavailableError:
                    raise

        content = self.separator.join(content_parts)

        reconstructed = ReconstructedDocument(
            content=content,
            total_chunks=total_chunks,
            translated_chunks=translated_count,
            passthrough_chunks=passthrough_count,
            total_input_tokens=total_input,
            total_output_tokens=total_output
        )

        status = AssemblyStatus.DEGRADED if failed_outcomes else AssemblyStatus.SUCCESS
        
        report = AssemblyReport(
            timestamp=time.time(),
            total_chunks=total_chunks,
            total_failed=len(failed_outcomes),
            failure_reasons=dict(Counter(f.failure_reason.value for f in failed_outcomes if f.failure_reason)),
            degradation_applied=bool(failed_outcomes)
        )

        return DocumentAssemblyDecision(
            status=status,
            document=reconstructed,
            failed_outcomes=failed_outcomes,
            rejection_reason=None,
            audit_report=report
        )

    def _build_rejection(self, reason: str, failed_outcomes: List[ChunkOutcome]) -> DocumentAssemblyDecision:
        report = AssemblyReport(
            timestamp=time.time(),
            total_chunks=max(1, len(failed_outcomes)), 
            total_failed=len(failed_outcomes),
            failure_reasons=dict(Counter(f.failure_reason.value for f in failed_outcomes if f.failure_reason)),
            degradation_applied=False
        )
        return DocumentAssemblyDecision(
            status=AssemblyStatus.REJECTED,
            document=None,
            failed_outcomes=failed_outcomes,
            rejection_reason=reason,
            audit_report=report
        )