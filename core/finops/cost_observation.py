"""F18-05 R12: per-attempt cost observation, never admission or billing authority.

Rates come from the checked admission evidence, not a hardcoded tariff.
The calculation is conditional on those rates; a provider response is usage
evidence, not proof of actual charges or zero-cost account entitlement.
"""
from decimal import Decimal, InvalidOperation
from typing import Mapping, Sequence

SDK_RESPONSE = "PPPR_G3_CLIENT_SDK_RESPONSE"


def _amount(value: object) -> Decimal:
    if not isinstance(value, str):
        raise ValueError("PPPR_COST_RATE_INVALID")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("PPPR_COST_RATE_INVALID") from exc
    if not parsed.is_finite() or parsed < 0:
        raise ValueError("PPPR_COST_RATE_INVALID")
    return parsed


def observe_attempt_cost(
    admission: Mapping[str, object],
    responses: Sequence[Mapping[str, object]],
    *,
    sdk_entries: int,
    capture_complete: bool,
) -> dict[str, object]:
    """Only report an estimate for an unambiguous attributed response.

    The possible-exposure amount is a single admitted request scenario,
    not a bound on aggregate external effects or confirmed spend. Even a
    complete client capture cannot exclude duplication at the provider.
    """
    price_ref = admission.get("price_evidence_ref")
    if not isinstance(price_ref, str) or not price_ref.strip():
        raise ValueError("PPPR_COST_PRICE_EVIDENCE_REQUIRED")
    input_rate = _amount(admission.get("input_price_per_token"))
    output_rate = _amount(admission.get("output_price_per_token"))
    admitted_cost = _amount(admission.get("upper_bound_cost"))
    attributed = []
    for response in responses:
        if response.get("request_sha256") != admission.get("request_sha256"):
            raise ValueError("PPPR_COST_REQUEST_CORRELATION_FAILED")
        i, o, total = (response.get(k) for k in ("input_tokens", "output_tokens", "total_tokens"))
        response_id = response.get("response_id")
        valid = (
            response.get("response_model") == admission.get("model_name")
            and isinstance(response_id, str) and bool(response_id.strip())
            and type(i) is int and i > 0 and type(o) is int and o >= 0
            and type(total) is int and total == i + o
        )
        attributed.append({
            "response_id": response_id,
            "response_model": response.get("response_model"),
            "input_tokens": i if valid else None,
            "output_tokens": o if valid else None,
            "total_tokens": total if valid else None,
            "classification": "SDK_REPORTED" if valid else "UNATTRIBUTED_OR_UNAVAILABLE",
        })
    estimate: str | None = None
    if len(attributed) == 1 and sdk_entries == 1 and attributed[0]["classification"] == "SDK_REPORTED":
        i, o = attributed[0]["input_tokens"], attributed[0]["output_tokens"]
        assert isinstance(i, int) and isinstance(o, int)
        estimate = str(i * input_rate + o * output_rate)
    unresolved = not capture_complete or sdk_entries != 1 or estimate is None
    return {
        "price_evidence_ref": price_ref,
        "provider_id": admission.get("provider_id"),
        "requested_model": admission.get("model_name"),
        "admitted_request_cost_ceiling_usd": str(admitted_cost),
        "responses": attributed,
        "observed_or_invoiced_cost": {
            "classification": "NOT_OBSERVABLE", "amount_usd": None,
            "basis": "NO_ATTRIBUTED_BILLING_EVIDENCE",
        },
        "estimated_cost": {
            "classification": "ESTIMATED" if estimate is not None else "NOT_OBSERVABLE",
            "amount_usd": estimate,
            "basis": "SDK_USAGE_TIMES_ADMITTED_RATES_SINGLE_RESPONSE",
        },
        "potential_unconfirmed_exposure": {
            "classification": "HYPOTHETICAL" if unresolved else "NOT_OBSERVABLE",
            "amount_usd": str(admitted_cost) if unresolved else None,
            "basis": "ONE_ADMITTED_REQUEST_SCENARIO_NOT_AGGREGATE_BOUND",
            "validated_upper_bound_usd": None,
        },
        "limitations": (
            "No billing verification or free-tier entitlement attestation. "
            "Missing responses and incomplete capture do not establish zero usage or spend. "
            "No external duplication guarantee; synthetic rates and usage are not production charges."
        ),
    }
