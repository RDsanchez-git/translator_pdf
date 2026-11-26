"""Offline PPPR R4-R6 falsators. Nothing here is scientific authority."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from apps.benchmark import pppr_scientific_admission as shell
from core.benchmark.certification.pppr_admission import (
    Accreditation, AdmissionEvidence, Approval, ArtifactIdentity, Condition,
    Decision, Dimension, EvaluationRequest, IndependenceEvidence, Origin,
    ReferenceEvidence, ReferenceKind, ReferenceRequest, Role, Scope,
)
from core.shared.crypto import compute_sha256

pytestmark = pytest.mark.unit


class SyntheticChannel:
    kind = shell.ChannelKind.SYNTHETIC

    def __init__(self, records, contents):
        self.records = records
        self.contents = contents
        self.reads = []

    def resolve_records(self, request):
        return self.records

    def read_immutable(self, identity):
        self.reads.append(identity)
        return self.contents[identity]


@pytest.fixture
def witness():
    # Fixed past origin times, independent of caller-controlled evaluation dates.
    before = datetime(2020, 1, 1, tzinfo=timezone.utc)
    act_time = before + timedelta(days=1)
    scopes = frozenset(Scope("physics", d, "meaning") for d in Dimension)
    contents = {}

    def artifact(name, content):
        identity = ArtifactIdentity(name, "synthetic-revision", "0.3.0",
                                    compute_sha256(content))
        contents[identity] = content
        return identity

    def origin(actor, record):
        return Origin(record, actor, "synthetic-original-channel", act_time)

    def grant(actor, role):
        return Accreditation(actor, role, scopes,
                             Origin("grant-" + actor, "synthetic-verifier",
                                    "synthetic-grant-channel", before),
                             "competence-" + actor, "mandate-" + actor,
                             before, None, Decision.APPROVED)

    adr = artifact("adr", b"synthetic architecture")
    protocol = artifact("protocol", b"synthetic criteria")
    source = artifact("source", b"synthetic EN")
    candidate = artifact("candidate", b"synthetic ES")
    bilingual = artifact("reference", b"independent bilingual annotation")
    refs = tuple(ReferenceRequest(bilingual if s.dimension is Dimension.LANGUAGE
                                  else source, s)
                 for s in sorted(scopes, key=lambda s: s.dimension.value))
    req = EvaluationRequest(adr, protocol, source, candidate, "generation-1",
                            scopes, refs, "evaluator")
    grants = tuple(grant(actor, role) for actor, role in (
        ("board", Role.BOARD), ("scientist", Role.SCIENTIFIC),
        ("custodian", Role.CUSTODIAN), ("evaluator", Role.EVALUATOR),
    ))
    approvals = tuple(Approval(origin(actor, "policy-" + actor), role,
                               frozenset((adr, protocol)), scopes, Decision.APPROVED)
                      for actor, role in (("board", Role.BOARD),
                                           ("scientist", Role.SCIENTIFIC)))
    reference_records = tuple(ReferenceEvidence(
        ref, source, ReferenceKind.BILINGUAL_ANNOTATION
        if ref.scope.dimension is Dimension.LANGUAGE else ReferenceKind.SOURCE_PDF,
        "independent-author", "source-provenance", "reference-method", "license",
        Approval(origin("scientist", "validation-" + ref.scope.dimension.value),
                 Role.SCIENTIFIC, frozenset((source, ref.artifact)),
                 frozenset((ref.scope,)), Decision.APPROVED),
        Approval(origin("custodian", "permission-" + ref.scope.dimension.value),
                 Role.CUSTODIAN, frozenset((source, ref.artifact)),
                 frozenset((ref.scope,)), Decision.APPROVED),
    ) for ref in refs)
    independence = IndependenceEvidence(
        origin("scientist", "history-review"), Decision.APPROVED,
        req.generation_id, source, candidate, frozenset(refs), scopes,
        frozenset(("producer",)),
        frozenset((source.sha256, bilingual.sha256, "source-family-1")),
        frozenset(("adjustment-family-2",)), "reviewed-history",
        "general pretraining unknown; concrete PDF only", frozenset(),
    )
    return req, SyntheticChannel(AdmissionEvidence(grants, approvals, reference_records,
                                                   independence), contents)


def test_positive_synthetic_admission_recomputes_all_bytes(witness):
    req, channel = witness
    report, inputs = shell._inspect(req, channel)
    assert report.admitted and inputs is not None
    assert frozenset(channel.reads) == req.artifacts
    assert len(channel.reads) == len(req.artifacts)
    assert dict(inputs.artifacts) == channel.contents


@pytest.mark.parametrize("mutation,expected", [
    ("no_policy", Condition.R6_PRIOR_APPROVAL),
    ("board_only", Condition.R6_PRIOR_APPROVAL),
    ("unapproved_policy", Condition.R6_PRIOR_APPROVAL),
    ("hash_without_authority", Condition.R6_PRIOR_APPROVAL),
    ("unknown_actor", Condition.R6_PRIOR_APPROVAL),
    ("self_attested_grant", Condition.R6_PRIOR_APPROVAL),
    ("wrong_scope", Condition.R6_PRIOR_APPROVAL),
    ("missing_version", Condition.R6_POLICY),
    ("different_version", Condition.R6_PRIOR_APPROVAL),
    ("retroactive", Condition.R6_PRIOR_APPROVAL),
    ("unknown_order", Condition.R6_PRIOR_APPROVAL),
    ("unattributable", Condition.R6_PRIOR_APPROVAL),
    ("expired", Condition.R6_PRIOR_APPROVAL),
    ("conflicting_approval", Condition.R6_PRIOR_APPROVAL),
    ("altered_policy", Condition.R4_INTEGRITY),
    ("altered_reference", Condition.R4_INTEGRITY),
    ("missing_license", Condition.R4_REFERENCE),
    ("wrong_permission_scope", Condition.R4_REFERENCE),
    ("missing_provenance", Condition.R4_REFERENCE),
    ("source_only_language", Condition.R4_REFERENCE),
    ("missing_reference", Condition.R4_REFERENCE),
    ("duplicate_reference", Condition.R4_REFERENCE),
    ("candidate_as_reference", Condition.R5_INDEPENDENCE),
    ("candidate_derived", Condition.R5_INDEPENDENCE),
    ("no_independence", Condition.R5_INDEPENDENCE),
    ("unresolved_history", Condition.R5_INDEPENDENCE),
    ("overlap_hash", Condition.R5_INDEPENDENCE),
    ("overlap_family", Condition.R5_INDEPENDENCE),
    ("wrong_generation", Condition.R5_INDEPENDENCE),
    ("producer_evaluator", Condition.R5_INDEPENDENCE),
    ("sole_producer_evidence", Condition.R5_INDEPENDENCE),
])
def test_fail_closed_falsators(witness, mutation, expected):
    req, channel = witness
    ev = channel.records
    board, science = ev.approvals
    grants = ev.accreditations
    first = ev.references[0]
    review = ev.independence
    assert review is not None
    if mutation == "no_policy":
        ev = replace(ev, approvals=())
    elif mutation == "board_only":
        ev = replace(ev, approvals=(board,))
    elif mutation == "unapproved_policy":
        ev = replace(ev, approvals=(board, replace(science, decision=Decision.REJECTED)))
    elif mutation == "hash_without_authority":
        ev = replace(ev, accreditations=())
    elif mutation == "unknown_actor":
        ev = replace(ev, approvals=(board, replace(science, origin=replace(
            science.origin, actor_id="unknown"))))
    elif mutation == "self_attested_grant":
        ev = replace(ev, accreditations=(grants[0], replace(grants[1], origin=replace(
            grants[1].origin, actor_id=grants[1].actor_id)), *grants[2:]))
    elif mutation == "wrong_scope":
        ev = replace(ev, accreditations=(grants[0], replace(grants[1], scopes=frozenset()),
                                         *grants[2:]))
    elif mutation in ("missing_version", "different_version"):
        modified = replace(req.protocol, version="" if mutation == "missing_version" else "0.4.0")
        channel.contents[modified] = channel.contents.pop(req.protocol)
        req = replace(req, protocol=modified)
    elif mutation in ("retroactive", "unknown_order", "unattributable"):
        changes = {
            "retroactive": {"occurred_at": datetime.now(timezone.utc) + timedelta(days=1)},
            "unknown_order": {"occurred_at": None},
            "unattributable": {"channel_ref": ""},
        }
        ev = replace(ev, approvals=(board, replace(science, origin=replace(
            science.origin, **changes[mutation]))))
    elif mutation == "expired":
        ev = replace(ev, accreditations=(grants[0], replace(grants[1],
            valid_until=datetime(2021, 1, 1, tzinfo=timezone.utc)), *grants[2:]))
    elif mutation == "conflicting_approval":
        ev = replace(ev, approvals=(*ev.approvals, replace(science, decision=Decision.REJECTED)))
    elif mutation == "altered_policy":
        channel.contents[req.protocol] += b"changed without version bump"
    elif mutation == "altered_reference":
        channel.contents[first.reference.artifact] += b"changed reference"
    elif mutation == "missing_license":
        ev = replace(ev, references=(replace(first, license_ref=""), *ev.references[1:]))
    elif mutation == "wrong_permission_scope":
        ev = replace(ev, references=(replace(first, permission=replace(
            first.permission, scopes=frozenset())), *ev.references[1:]))
    elif mutation == "missing_provenance":
        ev = replace(ev, references=(replace(first, provenance_ref=""), *ev.references[1:]))
    elif mutation == "source_only_language":
        ev = replace(ev, references=(replace(first, kind=ReferenceKind.SOURCE_PDF),
                                      *ev.references[1:]))
    elif mutation == "missing_reference":
        ev = replace(ev, references=ev.references[1:])
    elif mutation == "duplicate_reference":
        req = replace(req, references=(*req.references, req.references[0]))
    elif mutation == "candidate_as_reference":
        ref = replace(first.reference, artifact=req.candidate)
        req = replace(req, references=(ref, *req.references[1:]))
        ev = replace(ev, references=(replace(first, reference=ref), *ev.references[1:]))
    elif mutation == "candidate_derived":
        ev = replace(ev, independence=replace(review,
                     candidate_derived_references=frozenset((first.reference,))))
    elif mutation == "no_independence":
        ev = replace(ev, independence=None)
    elif mutation == "unresolved_history":
        ev = replace(ev, independence=replace(review, decision=Decision.UNRESOLVED))
    elif mutation in ("overlap_hash", "overlap_family"):
        key = req.source.sha256 if mutation == "overlap_hash" else "source-family-1"
        ev = replace(ev, independence=replace(review, adjustment_keys=frozenset((key,))))
    elif mutation == "wrong_generation":
        ev = replace(ev, independence=replace(review, generation_id="other"))
    elif mutation == "producer_evaluator":
        ev = replace(ev, independence=replace(review, producer_ids=frozenset((req.evaluator_id,))))
    elif mutation == "sole_producer_evidence":
        ev = replace(ev, references=tuple(replace(x, author_id="producer") for x in ev.references))
    else:
        pytest.fail("unhandled falsator")
    channel.records = ev
    report, inputs = shell._inspect(req, channel)
    assert not report.admitted and inputs is None
    assert expected in {v.condition for v in report.violations}


def test_real_consumer_default_blocks_before_evaluator(witness):
    req, _ = witness
    with pytest.raises(shell.AdmissionBlocked) as failure:
        shell.evaluate_certifying(req, lambda _: pytest.fail("evaluation entered"))
    assert failure.value.report.violations[0].condition is Condition.TRUST_CHANNEL


def test_complete_synthetic_fixture_cannot_enable_certifying_consumer(witness, monkeypatch):
    req, channel = witness
    assert shell._inspect(req, channel)[0].admitted
    channel.reads.clear()
    monkeypatch.setattr(shell, "_configured_channel", lambda: channel)
    with pytest.raises(shell.AdmissionBlocked):
        shell.evaluate_certifying(req, lambda _: pytest.fail("synthetic bypass"))
    assert channel.reads == []


def test_unavailable_original_and_missing_bytes_block(witness):
    req, channel = witness
    del channel.contents[req.protocol]
    report, inputs = shell._inspect(req, channel)
    assert not report.admitted and inputs is None
    assert report.violations[0].condition is Condition.TRUST_CHANNEL


def test_no_channel_cannot_be_replaced_by_self_consistent_request(witness):
    req, _ = witness
    report, inputs = shell._inspect(req, None)
    assert not report.admitted and inputs is None


class AccreditedChannelDouble(SyntheticChannel):
    """Test-only stand-in for a trusted composition dependency.

    Never registered outside these tests; does not authenticate real originals
    or establish scientific authority.
    """
    kind = shell.ChannelKind.ACCREDITED


def _add_language_reference(req, channel, *, scope, author_id, content, path):
    """Add one attributed reference and extend the synthetic review consistently."""
    ev = channel.records
    review = ev.independence
    assert review is not None
    original = next(item for item in ev.references
                    if item.reference.scope.dimension is Dimension.LANGUAGE)
    artifact = replace(original.reference.artifact, path=path,
                       sha256=compute_sha256(content))
    reference = ReferenceRequest(artifact, scope)
    objects = frozenset((req.source, artifact))
    record = replace(
        original, reference=reference, author_id=author_id,
        validation=replace(original.validation, objects=objects,
                           scopes=frozenset((scope,))),
        permission=replace(original.permission, objects=objects,
                           scopes=frozenset((scope,))),
    )
    scopes = req.scopes | frozenset((scope,))
    req = replace(req, scopes=scopes, references=(*req.references, reference))
    channel.contents[artifact] = content
    channel.records = replace(
        ev,
        accreditations=tuple(replace(g, scopes=scopes) for g in ev.accreditations),
        approvals=tuple(replace(a, scopes=scopes) for a in ev.approvals),
        references=(*ev.references, record),
        independence=replace(review, scopes=scopes,
                             references=frozenset(req.references),
                             confirmatory_keys=review.confirmatory_keys | frozenset((artifact.sha256,))),
    )
    return req


@pytest.mark.parametrize("separate_property", [False, True],
                         ids=["other-dimensions", "same-dimension-other-property"])
def test_h_g6_04_sole_producer_scope_cannot_be_compensated(
    witness, separate_property,
):
    req, channel = witness
    ev = channel.records
    language = next(s for s in req.scopes if s.dimension is Dimension.LANGUAGE)
    if separate_property:
        # The original language property still has independent evidence.
        req = _add_language_reference(
            req, channel, scope=replace(language, property_name="terminology"),
            author_id="producer", content=b"producer terminology reference",
            path="producer-terminology",
        )
    else:
        # Other dimensions have independent evidence, but language does not.
        channel.records = replace(ev, references=tuple(
            replace(item, author_id="producer") if item.reference.scope == language else item
            for item in ev.references
        ))
    report, inputs = shell._inspect(req, channel)
    assert inputs is None and not report.admitted
    assert {(v.condition, v.detail) for v in report.violations} == {
        (Condition.R5_INDEPENDENCE, "SOLE_PRODUCER_EVIDENCE")
    }


def test_h_g6_04_preexisting_producer_reference_with_same_scope_independent_evidence(witness):
    req, channel = witness
    language = next(s for s in req.scopes if s.dimension is Dimension.LANGUAGE)
    # Synthetic preexisting reference, separately validated, not candidate-derived.
    # The original independent reference for the SAME scope remains present.
    req = _add_language_reference(
        req, channel, scope=language, author_id="producer",
        content=b"preexisting producer-authored reference", path="preexisting",
    )
    report, inputs = shell._inspect(req, channel)
    assert report.admitted and inputs is not None


@pytest.mark.parametrize("condition", [
    Condition.R4_INTEGRITY, Condition.R5_INDEPENDENCE, Condition.R6_PRIOR_APPROVAL,
])
def test_h_g6_05_certifying_consumer_rejects_invalid_evidence(
    witness, monkeypatch, condition,
):
    from unittest.mock import Mock

    req, channel = witness
    ev = channel.records
    if condition is Condition.R4_INTEGRITY:
        channel.contents[req.protocol] += b"altered bytes"
    elif condition is Condition.R5_INDEPENDENCE:
        channel.records = replace(ev, references=tuple(
            replace(item, author_id="producer")
            if item.reference.scope.dimension is Dimension.LANGUAGE else item
            for item in ev.references
        ))
    else:
        channel.records = replace(ev, approvals=tuple(
            a for a in ev.approvals if a.role is not Role.SCIENTIFIC
        ))
    double = AccreditedChannelDouble(channel.records, channel.contents)
    monkeypatch.setattr(shell, "_configured_channel", lambda: double)
    evaluator = Mock(side_effect=AssertionError("invalid evidence entered evaluator"))
    with pytest.raises(shell.AdmissionBlocked) as failure:
        shell.evaluate_certifying(req, evaluator)
    evaluator.assert_not_called()
    assert condition in {v.condition for v in failure.value.report.violations}
    assert frozenset(double.reads) == req.artifacts
    assert len(double.reads) == len(req.artifacts)


def test_h_g6_05_certifying_consumer_passes_exact_examined_bytes_once(witness, monkeypatch):
    from unittest.mock import Mock

    req, channel = witness
    double = AccreditedChannelDouble(channel.records, channel.contents)
    monkeypatch.setattr(shell, "_configured_channel", lambda: double)
    examined = dict(double.contents)
    sentinel = object()

    def observe(inputs):
        assert inputs.request == req
        assert dict(inputs.artifacts) == examined
        assert len(inputs.artifacts) == len(examined)
        assert all(compute_sha256(content) == identity.sha256
                   for identity, content in inputs.artifacts)
        # Mutating the backing store cannot change the immutable bytes delivered.
        double.contents[req.candidate] = b"replacement after admission"
        assert dict(inputs.artifacts) == examined
        return sentinel

    evaluator = Mock(side_effect=observe)
    assert shell.evaluate_certifying(req, evaluator) is sentinel
    evaluator.assert_called_once()
    assert frozenset(double.reads) == req.artifacts
    assert len(double.reads) == len(req.artifacts)
