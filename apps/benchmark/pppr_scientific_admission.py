"""Application boundary for PPPR certification admission (Task 6.1.1 only).

The channel is a composition dependency, never a request argument, CLI flag,
environment toggle, uploaded manifest or a caller-provided approval boolean.
There is no accredited scientific channel configured today. A later authorized
adapter must resolve current records from original trusted custody, verify
authorship/mandate and chronology independently of the applicant, and return
actual immutable bytes. Missing channel or unavailable evidence blocks.

No evaluator, corpus acquisition, or certification result is implemented here.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol, TypeVar

from core.benchmark.certification.pppr_admission import (
    AdmissionEvidence, AdmissionReport, ArtifactIdentity, Condition,
    EvaluationRequest, Violation, evaluate_admission,
)
from core.shared.crypto import compute_sha256


class ChannelKind(Enum):
    ACCREDITED = "accredited"
    SYNTHETIC = "synthetic"


class EvidenceUnavailable(Exception):
    """Custody cannot resolve or authenticate the required original evidence."""


class TrustedEvidenceChannel(Protocol):
    """Read-only trusted composition port, not a caller-supplied evidence schema.

    Records must be resolved from independent current originals (including
    revocation/conflict information); Origin timestamps and actors are facts
    verified by the channel, not JSON assertions. Raise EvidenceUnavailable
    when any provenance, authority or temporal evidence cannot be established.
    Artifact resolution must honor immutable revision/path, without fallback
    to mutable working-tree content. A hash alone is never authentication.
    """

    @property
    def kind(self) -> ChannelKind: ...

    def resolve_records(self, request: EvaluationRequest) -> AdmissionEvidence: ...

    def read_immutable(self, identity: ArtifactIdentity) -> bytes: ...


@dataclass(frozen=True, slots=True)
class ResolvedInputs:
    request: EvaluationRequest
    artifacts: tuple[tuple[ArtifactIdentity, bytes], ...]


class AdmissionBlocked(Exception):
    def __init__(self, report: AdmissionReport) -> None:
        self.report = report
        super().__init__("PPPR_SCIENTIFIC_EVALUATION_BLOCKED")


def _blocked(detail: str) -> AdmissionReport:
    return AdmissionReport((Violation(Condition.TRUST_CHANNEL, detail),))


def _inspect(
    request: EvaluationRequest, channel: TrustedEvidenceChannel | None,
) -> tuple[AdmissionReport, ResolvedInputs | None]:
    """Real byte reads and digest recomputation, followed by the pure decision.

    Synthetic channels may exercise this function offline; its report cannot
    authorize the certifying consumer. Never return a reusable certification token.
    """
    if channel is None:
        return _blocked("ACCREDITED_CHANNEL_UNAVAILABLE"), None
    try:
        evidence = channel.resolve_records(request)
        artifacts = tuple((identity, channel.read_immutable(identity))
                          for identity in sorted(request.artifacts,
                                                key=lambda a: (a.revision, a.path, a.version, a.sha256)))
        if any(type(content) is not bytes for _, content in artifacts):
            return _blocked("IMMUTABLE_BYTES_UNAVAILABLE"), None
        computed = tuple((identity, compute_sha256(content)) for identity, content in artifacts)
        # Capture the real start boundary after I/O; not an applicant timestamp.
        report = evaluate_admission(request, evidence, computed, datetime.now(timezone.utc))
    except (EvidenceUnavailable, OSError, ValueError, TypeError, AttributeError, KeyError):
        return _blocked("EVIDENCE_UNVERIFIABLE"), None
    return report, ResolvedInputs(request, artifacts) if report.admitted else None


def _configured_channel() -> TrustedEvidenceChannel | None:
    # No authorized real custody source/adapter exists at this checkpoint.
    # Do not infer one from local paths, Git hashes, PR text or environment.
    return None


T = TypeVar("T")


def evaluate_certifying(
    request: EvaluationRequest, evaluator: Callable[[ResolvedInputs], T],
) -> T:
    """Only application entry to the future PPPR certifying evaluator.

    Re-resolve records and exact bytes on every invocation. A synthetic channel
    cannot enter this path even if every technical precondition would pass.
    The evaluator receives the exact immutable bytes inspected, not file paths
    to reopen or an independently supplied admission flag. This is admission,
    not certification; the evaluator itself belongs to Task 6.1.3.
    """
    channel = _configured_channel()
    if channel is None or channel.kind is not ChannelKind.ACCREDITED:
        raise AdmissionBlocked(_blocked("ACCREDITED_CHANNEL_UNAVAILABLE"))
    report, inputs = _inspect(request, channel)
    if not report.admitted or inputs is None:
        raise AdmissionBlocked(report)
    return evaluator(inputs)
