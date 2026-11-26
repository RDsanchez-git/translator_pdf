"""R12 arithmetic and epistemic boundary; synthetic evidence only."""
import pytest
from core.finops.cost_observation import observe_attempt_cost

pytestmark = pytest.mark.unit
ADMISSION = {
    "provider_id": "synthetic", "model_name": "fake", "request_sha256": "a" * 64,
    "price_evidence_ref": "synthetic-price", "input_price_per_token": "0.000001",
    "output_price_per_token": "0.000002", "upper_bound_cost": "0.01",
}
RESPONSE = {
    "response_model": "fake", "response_id": "r-1", "request_sha256": "a" * 64,
    "input_tokens": 100, "output_tokens": 50, "total_tokens": 150,
}


def test_usage_estimate_is_not_billed_cost():
    report = observe_attempt_cost(ADMISSION, [RESPONSE], sdk_entries=1, capture_complete=True)
    assert report["estimated_cost"]["amount_usd"] == "0.000200"
    assert report["observed_or_invoiced_cost"]["amount_usd"] is None
    assert report["potential_unconfirmed_exposure"]["amount_usd"] is None


@pytest.mark.parametrize("responses,count,complete", [
    ([], 1, True), ([], 0, False),
    ([dict(RESPONSE, input_tokens=None)], 1, True),
    ([dict(RESPONSE, response_model="wrong")], 1, True),
    ([RESPONSE, dict(RESPONSE, response_id="r-2")], 2, True),
])
def test_unresolved_cost_is_hypothetical_not_actual_or_validated_bound(responses, count, complete):
    report = observe_attempt_cost(ADMISSION, responses, sdk_entries=count, capture_complete=complete)
    assert report["estimated_cost"]["amount_usd"] is None
    assert report["observed_or_invoiced_cost"]["amount_usd"] is None
    assert report["potential_unconfirmed_exposure"]["classification"] == "HYPOTHETICAL"
    assert report["potential_unconfirmed_exposure"]["amount_usd"] == "0.01"
    assert report["potential_unconfirmed_exposure"]["validated_upper_bound_usd"] is None


def test_zero_rate_is_not_observed_zero_charge():
    admission = dict(ADMISSION, input_price_per_token="0", output_price_per_token="0", upper_bound_cost="0")
    report = observe_attempt_cost(admission, [RESPONSE], sdk_entries=1, capture_complete=True)
    assert report["estimated_cost"]["amount_usd"] == "0"
    assert report["observed_or_invoiced_cost"]["amount_usd"] is None


def test_request_drift_rejected():
    with pytest.raises(ValueError, match="REQUEST_CORRELATION_FAILED"):
        observe_attempt_cost(ADMISSION, [dict(RESPONSE, request_sha256="b"*64)],
                             sdk_entries=1, capture_complete=True)


def test_free_entitlement_keeps_nominal_estimate_separate_from_zero_cap():
    admission = dict(ADMISSION, upper_bound_cost="0", nominal_upper_bound_cost="0.01",
                     free_tier_witness={"witness_id": "synthetic"})
    report = observe_attempt_cost(admission, [RESPONSE], sdk_entries=1, capture_complete=True)
    assert report["admitted_request_cost_ceiling_usd"] == "0"
    assert report["estimated_cost"]["amount_usd"] == "0.000200"
    assert "NOMINAL" in report["estimated_cost"]["basis"]
    assert report["observed_or_invoiced_cost"]["amount_usd"] is None
    uncertain = observe_attempt_cost(admission, [], sdk_entries=1, capture_complete=False)
    assert uncertain["potential_unconfirmed_exposure"]["amount_usd"] == "0.01"
    assert uncertain["potential_unconfirmed_exposure"]["validated_upper_bound_usd"] is None
