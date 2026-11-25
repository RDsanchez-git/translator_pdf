"""PPPR R4-R6: pure admission, not PDF->AST certification or a scientific verdict.

Records are projections of originals resolved by a trusted custody channel.
Neither constructing these DTOs nor hashing a file establishes that trust.
The application boundary owns channel selection and byte acquisition.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Dimension(Enum):
    LANGUAGE = "language"
    STEM = "stem"
    STRUCTURE = "structure"


class Role(Enum):
    BOARD = "board"
    SCIENTIFIC = "scientific"
    CUSTODIAN = "custodian"
    EVALUATOR = "evaluator"


class ReferenceKind(Enum):
    HUMAN_TRANSLATION = "human_translation"
    AUTHORIZED_BILINGUAL = "authorized_bilingual"
    BILINGUAL_ANNOTATION = "bilingual_annotation"
    SOURCE_PDF = "source_pdf"
    SPECIALIZED_ANNOTATION = "specialized_annotation"
    PRIMARY_MATERIAL = "primary_material"


class Decision(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class Scope:
    domain: str
    dimension: Dimension
    property_name: str


@dataclass(frozen=True, slots=True)
class ArtifactIdentity:
    path: str
    revision: str
    version: str
    sha256: str


@dataclass(frozen=True, slots=True)
class ReferenceRequest:
    artifact: ArtifactIdentity
    scope: Scope


@dataclass(frozen=True, slots=True)
class EvaluationRequest:
    adr: ArtifactIdentity
    protocol: ArtifactIdentity
    source: ArtifactIdentity
    candidate: ArtifactIdentity
    generation_id: str
    scopes: frozenset[Scope]
    references: tuple[ReferenceRequest, ...]
    evaluator_id: str

    @property
    def artifacts(self) -> frozenset[ArtifactIdentity]:
        return frozenset((self.adr, self.protocol, self.source, self.candidate,
                          *(ref.artifact for ref in self.references)))


@dataclass(frozen=True, slots=True)
class Origin:
    """Original record identity and event time resolved by custody, not caller time."""
    record_ref: str
    actor_id: str
    channel_ref: str
    occurred_at: datetime | None


@dataclass(frozen=True, slots=True)
class Accreditation:
    actor_id: str
    role: Role
    scopes: frozenset[Scope]
    origin: Origin
    competence_ref: str
    mandate_ref: str
    valid_from: datetime
    valid_until: datetime | None
    decision: Decision


@dataclass(frozen=True, slots=True)
class Approval:
    origin: Origin
    role: Role
    objects: frozenset[ArtifactIdentity]
    scopes: frozenset[Scope]
    decision: Decision


@dataclass(frozen=True, slots=True)
class ReferenceEvidence:
    reference: ReferenceRequest
    source: ArtifactIdentity
    kind: ReferenceKind
    author_id: str
    provenance_ref: str
    method_ref: str
    license_ref: str
    validation: Approval
    permission: Approval


@dataclass(frozen=True, slots=True)
class IndependenceEvidence:
    """Competent review of known source families and controlled experiment history.

    Keys include exact source/reference hashes and reviewed semantic-family keys.
    General pretraining uncertainty is recorded separately, not automatic leakage.
    An empty adjustment set is meaningful only inside an attributable review.
    """
    origin: Origin
    decision: Decision
    generation_id: str
    source: ArtifactIdentity
    candidate: ArtifactIdentity
    references: frozenset[ReferenceRequest]
    scopes: frozenset[Scope]
    producer_ids: frozenset[str]
    confirmatory_keys: frozenset[str]
    adjustment_keys: frozenset[str]
    history_ref: str
    pretraining_limitation: str
    candidate_derived_references: frozenset[ReferenceRequest]


@dataclass(frozen=True, slots=True)
class AdmissionEvidence:
    """Current records from independent authorized custody; never request fields."""
    accreditations: tuple[Accreditation, ...]
    approvals: tuple[Approval, ...]
    references: tuple[ReferenceEvidence, ...]
    independence: IndependenceEvidence | None


class Condition(Enum):
    R4_AUTHORITY = "R4_AUTHORITY"
    R4_REFERENCE = "R4_REFERENCE"
    R4_INTEGRITY = "R4_INTEGRITY"
    R5_INDEPENDENCE = "R5_INDEPENDENCE"
    R6_POLICY = "R6_POLICY"
    R6_PRIOR_APPROVAL = "R6_PRIOR_APPROVAL"
    TRUST_CHANNEL = "TRUST_CHANNEL"


@dataclass(frozen=True, slots=True)
class Violation:
    condition: Condition
    detail: str


@dataclass(frozen=True, slots=True)
class AdmissionReport:
    violations: tuple[Violation, ...]

    @property
    def admitted(self) -> bool:
        return not self.violations


def _text(value: str) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _time(value: datetime | None) -> bool:
    return isinstance(value, datetime) and value.utcoffset() is not None


def _identity(value: ArtifactIdentity) -> bool:
    return (all(_text(x) for x in (value.path, value.revision, value.version))
            and len(value.sha256) == 64
            and all(c in "0123456789abcdef" for c in value.sha256))


def _scope(value: Scope) -> bool:
    return (_text(value.domain) and isinstance(value.dimension, Dimension)
            and _text(value.property_name))


def _prior(origin: Origin, start: datetime) -> bool:
    occurred = origin.occurred_at
    return (all(_text(x) for x in (origin.record_ref, origin.actor_id, origin.channel_ref))
            and occurred is not None and _time(occurred) and occurred < start)


def _grant(grant: Accreditation, at: datetime, start: datetime,
           scopes: frozenset[Scope]) -> bool:
    issued = grant.origin.occurred_at
    return (grant.decision is Decision.APPROVED and _text(grant.actor_id)
            and grant.origin.actor_id != grant.actor_id
            and _prior(grant.origin, start) and issued is not None and issued <= at
            and _text(grant.competence_ref) and _text(grant.mandate_ref)
            and _time(grant.valid_from) and grant.valid_from <= at
            and (grant.valid_until is None or
                 (_time(grant.valid_until) and start < grant.valid_until))
            and scopes <= grant.scopes)


def _authorized(evidence: AdmissionEvidence, actor: str, role: Role,
                at: datetime, start: datetime, scopes: frozenset[Scope]) -> bool:
    # Exactly one current accreditation per actor/role in the custody snapshot.
    grants = tuple(g for g in evidence.accreditations
                   if g.actor_id == actor and g.role is role)
    return len(grants) == 1 and _grant(grants[0], at, start, scopes)


def _approval(evidence: AdmissionEvidence, act: Approval, role: Role,
              objects: frozenset[ArtifactIdentity], scope: Scope,
              start: datetime) -> bool:
    occurred = act.origin.occurred_at
    return (act.role is role and act.decision is Decision.APPROVED
            and act.objects == objects and scope in act.scopes
            and _prior(act.origin, start) and occurred is not None
            and _authorized(evidence, act.origin.actor_id, role, occurred, start,
                            frozenset((scope,))))


def evaluate_admission(
    request: EvaluationRequest,
    evidence: AdmissionEvidence,
    computed_hashes: tuple[tuple[ArtifactIdentity, str], ...],
    start: datetime,
) -> AdmissionReport:
    """Evaluate already resolved data; no I/O, clocks, caller flags or certification."""
    failures: list[Violation] = []

    def deny(condition: Condition, detail: str) -> None:
        failures.append(Violation(condition, detail))

    if not _time(start):
        return AdmissionReport((Violation(Condition.R6_PRIOR_APPROVAL, "START_UNVERIFIABLE"),))
    if (not request.scopes or any(not _scope(s) for s in request.scopes)
            or not _text(request.generation_id) or not _text(request.evaluator_id)):
        deny(Condition.R4_AUTHORITY, "SCOPE_OR_SUBJECT_MISSING")
    if not all(_identity(a) for a in request.artifacts):
        deny(Condition.R6_POLICY, "IDENTITY_OR_VERSION_MISSING")
    hashes = dict(computed_hashes)
    if (len(hashes) != len(computed_hashes) or hashes.keys() != request.artifacts
            or any(hashes.get(a) != a.sha256 for a in request.artifacts)):
        deny(Condition.R4_INTEGRITY, "ARTIFACT_IDENTITY_MISMATCH")
    if request.adr == request.protocol:
        deny(Condition.R6_POLICY, "POLICY_OBJECTS_NOT_DISTINCT")

    policy_objects = frozenset((request.adr, request.protocol))
    for scope in request.scopes:
        for role in (Role.BOARD, Role.SCIENTIFIC):
            acts = tuple(a for a in evidence.approvals if a.role is role
                         and scope in a.scopes)
            # A conflicting/current rejected act cannot be hidden behind another approval.
            if len(acts) != 1 or not _approval(
                evidence, acts[0], role, policy_objects, scope, start
            ):
                deny(Condition.R6_PRIOR_APPROVAL, role.value + "_APPROVAL_NOT_VERIFIED")
        if not _authorized(evidence, request.evaluator_id, Role.EVALUATOR,
                           start, start, frozenset((scope,))):
            deny(Condition.R4_AUTHORITY, "EVALUATOR_NOT_ACCREDITED")

    refs = frozenset(request.references)
    if (not refs or len(refs) != len(request.references)
            or {ref.scope for ref in refs} != request.scopes
            or len(evidence.references) != len(refs)
            or {item.reference for item in evidence.references} != refs):
        deny(Condition.R4_REFERENCE, "REFERENCE_SCOPE_OR_CARDINALITY_MISMATCH")
    for item in evidence.references:
        ref = item.reference
        objects = frozenset((item.source, ref.artifact))
        if (item.source != request.source or ref.scope not in request.scopes
                or not isinstance(item.kind, ReferenceKind)
                or not all(_text(x) for x in (item.author_id, item.provenance_ref,
                                              item.method_ref, item.license_ref))
                or not _approval(evidence, item.validation, Role.SCIENTIFIC,
                                 objects, ref.scope, start)
                or not _approval(evidence, item.permission, Role.CUSTODIAN,
                                 objects, ref.scope, start)):
            deny(Condition.R4_REFERENCE, "REFERENCE_NOT_VALIDATED_OR_PERMITTED")
        if (ref.scope.dimension is Dimension.LANGUAGE
                and item.kind not in (ReferenceKind.HUMAN_TRANSLATION,
                                      ReferenceKind.AUTHORIZED_BILINGUAL,
                                      ReferenceKind.BILINGUAL_ANNOTATION)):
            deny(Condition.R4_REFERENCE, "BILINGUAL_REFERENCE_REQUIRED")
        if item.kind is ReferenceKind.SOURCE_PDF and ref.artifact != request.source:
            deny(Condition.R4_REFERENCE, "SOURCE_REFERENCE_IDENTITY_MISMATCH")
        if ref.artifact.sha256 == request.candidate.sha256:
            deny(Condition.R5_INDEPENDENCE, "CANDIDATE_AS_REFERENCE")

    review = evidence.independence
    if review is None:
        deny(Condition.R5_INDEPENDENCE, "INDEPENDENCE_REVIEW_MISSING")
    else:
        occurred = review.origin.occurred_at
        required_keys = {request.source.sha256, *(ref.artifact.sha256 for ref in refs)}
        if (review.decision is not Decision.APPROVED
                or not _prior(review.origin, start) or occurred is None
                or not _authorized(evidence, review.origin.actor_id, Role.SCIENTIFIC,
                                   occurred, start, request.scopes)
                or review.generation_id != request.generation_id
                or review.source != request.source or review.candidate != request.candidate
                or review.references != refs or review.scopes != request.scopes
                or not review.producer_ids or not all(_text(x) for x in review.producer_ids)
                or not _text(review.history_ref) or not _text(review.pretraining_limitation)
                or not required_keys <= review.confirmatory_keys
                or not all(_text(x) for x in review.confirmatory_keys | review.adjustment_keys)
                or review.confirmatory_keys & review.adjustment_keys
                or review.candidate_derived_references
                or request.evaluator_id in review.producer_ids
                or review.origin.actor_id in review.producer_ids):
            deny(Condition.R5_INDEPENDENCE, "INDEPENDENCE_NOT_ESTABLISHED")
        for item in evidence.references:
            if item.validation.origin.actor_id in review.producer_ids:
                deny(Condition.R5_INDEPENDENCE, "REFERENCE_VALIDATED_BY_PRODUCER")
        if evidence.references and all(
            item.author_id in review.producer_ids for item in evidence.references
        ):
            deny(Condition.R5_INDEPENDENCE, "SOLE_PRODUCER_EVIDENCE")
    return AdmissionReport(tuple(failures))
