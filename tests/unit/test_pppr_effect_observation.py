"""F18-05 R4–R9 falsifiers; synthetic evidence, not provider certification."""
import pytest

from core.finops.effect_observation import (
    ExternalEvidence, IndirectExposureEstimate, SDK_ENTRY, RECEIPT_WINDOW, build_effect_report,
)

pytestmark = pytest.mark.unit
GEN = "a" * 64
ADMISSIONS = {("task", "exec-1"): GEN, ("task", "exec-2"): GEN}


def _entry(execution, timestamp):
    return {"message": SDK_ENTRY, "task_id": "task", "execution_id": execution,
            "observed_at_ns": timestamp}


def _report(events, **kwargs):
    return build_effect_report(
        ADMISSIONS, events, start_ns=1, end_ns=100,
        scope="SYNTHETIC_CLASSIFICATION", **kwargs,
    )


def test_client_reexecution_does_not_confirm_external_duplication():
    report = _report([_entry("exec-1", 10), _entry("exec-2", 20)], capture_complete=True)
    row, = report["operations"]
    assert row["client_activity"]["reexecution_observed"] is True
    assert row["client_activity"]["observed_sdk_entries"] == 2
    assert row["external_duplication"]["classification"] == "UNKNOWN"
    assert report["external_duplication_rate"] is None
    rate = report["client_reexecution_rate"]
    assert (rate["numerator"], rate["denominator"], rate["value"]) == (1, 1, 1.0)
    assert rate["unit"] == "logical_operation_with_observed_sdk_entry"
    assert (rate["start_ns"], rate["end_ns"]) == (1, 100)
    assert rate["coverage"]["admitted_attempts"] == rate["coverage"]["attempts_with_sdk_entry"] == 2
    assert rate["limitations"]


def test_external_evidence_evolves_without_double_counting_or_erasing_client_activity():
    events = [_entry("exec-1", 10), _entry("exec-2", 20)]
    inferred = ExternalEvidence("SYNTHETIC_VERIFIED_FIXTURE", inference_refs=("signal",))
    repeated = ExternalEvidence("SYNTHETIC_VERIFIED_FIXTURE", inference_refs=("signal",),
                                verified_applications=(("effect-1", "ref-a"), ("effect-1", "ref-b")))
    confirmed = ExternalEvidence("SYNTHETIC_VERIFIED_FIXTURE", inference_refs=("signal",),
                                 verified_applications=(("effect-1", "ref-a"), ("effect-2", "ref-b")))
    for proof, expected in [(inferred, "INFERRED"), (repeated, "INFERRED"), (confirmed, "CONFIRMED")]:
        report = _report(events, capture_complete=True, external_evidence={("task", GEN): proof})
        row, = report["operations"]
        assert row["client_activity"]["reexecution_observed"] is True
        assert row["external_duplication"]["classification"] == expected
        assert row["external_duplication"]["scope"] == "SYNTHETIC_VERIFIED_FIXTURE"
        assert row["external_duplication"]["inference_refs"] == ("signal",)
        assert report["external_duplication_rate"] is None
    with pytest.raises(ValueError, match="ATTRIBUTION_REQUIRED"):
        ExternalEvidence("SYNTHETIC", verified_applications=(("effect", ""),))


def test_missing_capture_is_not_zero_or_complete_rate():
    report = _report([_entry("exec-1", 10)], capture_complete=True)
    row, = report["operations"]
    assert row["client_activity"]["reexecution_observed"] is None
    assert row["client_activity"]["attempts"][1]["observed_sdk_entries"] is None
    assert report["client_reexecution_rate"]["value"] is None
    assert report["client_reexecution_rate"]["coverage"]["attempts_with_sdk_entry"] == 1
    assert _report([], capture_complete=True)["client_reexecution_rate"]["value"] is None
    assert _report([_entry("exec-1", 10), _entry("exec-2", 20)])["client_reexecution_rate"]["value"] is None


def test_measured_client_interval_and_indirect_estimate_are_not_external_bounds():
    events = [_entry("exec-1", 10), _entry("exec-2", 20), {
        "message": RECEIPT_WINDOW, "task_id": "task", "execution_id": "exec-1",
        "generation_sha256": GEN, "observed_at_ns": 30,
        "duration_ns": 7, "classification": "MEASURED",
    }]
    report = _report(events, capture_complete=True,
                     indirect_estimate=IndirectExposureEstimate(15, "synthetic-indirect-method"))
    row, = report["operations"]
    windows = [a["client_receipt_window"] for a in row["client_activity"]["attempts"]]
    assert [(w["classification"], w["duration_ns"]) for w in windows] == [("MEASURED", 7), ("NOT_OBSERVABLE", None)]
    assert row["external_causal_window"] == {
        "classification": "NOT_OBSERVABLE", "duration_ns": None, "validated_upper_bound_ns": None,
    }
    assert report["indirect_exposure_estimate"] == {
        "classification": "ESTIMATED", "duration_ns": 15,
        "basis_ref": "synthetic-indirect-method", "validated_upper_bound_ns": None,
    }


@pytest.mark.parametrize("events,match", [
    ([_entry("exec-3", 10)], "OUTSIDE_SCOPE"),
    ([_entry("exec-1", 101)], "OUTSIDE_SCOPE"),
    ([_entry("exec-1", 10), _entry("exec-1", 10)], "DUPLICATE_CAPTURE_EVENT"),
    ([{"message": RECEIPT_WINDOW, "task_id": "task", "execution_id": "exec-1",
       "observed_at_ns": 20, "generation_sha256": "b"*64,
       "duration_ns": 0, "classification": "MEASURED"}], "INVALID_RECEIPT_WINDOW"),
])
def test_invalid_or_ambiguous_observations_fail_closed(events, match):
    with pytest.raises(ValueError, match=match):
        _report(events)


def test_repeated_sdk_entry_within_same_attempt_is_not_hidden():
    report = build_effect_report(
        {("task", "exec-1"): GEN},
        [_entry("exec-1", 10), _entry("exec-1", 20)],
        start_ns=1, end_ns=100, scope="SYNTHETIC_SAME_ATTEMPT", capture_complete=True,
    )
    row, = report["operations"]
    client = row["client_activity"]
    assert client["distinct_execution_ids_observed"] == 1
    assert client["observed_sdk_entries"] == 2
    assert client["repeated_sdk_entry_within_attempt"] is True
    assert client["reexecution_observed"] is True
    rate = report["client_reexecution_rate"]
    assert (rate["numerator"], rate["denominator"], rate["value"]) == (1, 1, 1.0)
    assert row["external_duplication"]["classification"] == "UNKNOWN"
