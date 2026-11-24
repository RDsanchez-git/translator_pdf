"""F18-05 R4–R9: bounded, derived report, not execution or billing authority.

The input admissions are from a verified durable snapshot. SDK entry logs
observe the client boundary, not transport delivery. An absent log may mean
no entry or lost telemetry. No live provider evidence adapter is connected.
External evidence, when supplied by an upstream verifier, is explicitly
scoped; the synthetic tests exercise classification, not real duplication.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

SDK_ENTRY = "PPPR_G3_CLIENT_SDK_ENTRY"
RECEIPT_WINDOW = "PPPR_G3_CLIENT_RECEIPT_WINDOW"
AttemptKey = tuple[str, str]  # task_id, execution_id
OperationKey = tuple[str, str]  # task_id, generation_sha256


@dataclass(frozen=True, slots=True)
class ExternalEvidence:
    """Normalized evidence only, already verified/attributed by the caller.

    Each application pair is (distinct external application ID, evidence ref).
    A source ref alone, multiple requests or aggregate charges are insufficient.
    This report does not verify provider records or establish their authority.
    """

    scope: str
    inference_refs: tuple[str, ...] = ()
    verified_applications: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.scope.strip() or any(not ref.strip() for ref in self.inference_refs):
            raise ValueError("PPPR_EFFECT_EVIDENCE_SCOPE_REQUIRED")
        if any(not app.strip() or not ref.strip() for app, ref in self.verified_applications):
            raise ValueError("PPPR_EFFECT_APPLICATION_ATTRIBUTION_REQUIRED")

    def classification(self) -> str:
        if len({app for app, _ in self.verified_applications}) >= 2:
            return "CONFIRMED"
        return "INFERRED" if self.inference_refs else "UNKNOWN"


@dataclass(frozen=True, slots=True)
class IndirectExposureEstimate:
    duration_ns: int
    basis_ref: str

    def __post_init__(self) -> None:
        if type(self.duration_ns) is not int or self.duration_ns < 0 or not self.basis_ref.strip():
            raise ValueError("PPPR_EFFECT_INVALID_INDIRECT_ESTIMATE")


def build_effect_report(
    admissions: Mapping[AttemptKey, str],
    events: Sequence[Mapping[str, object]],
    *,
    start_ns: int,
    end_ns: int,
    scope: str,
    capture_complete: bool = False,
    external_evidence: Mapping[OperationKey, ExternalEvidence] | None = None,
    indirect_estimate: IndirectExposureEstimate | None = None,
) -> dict[str, object]:
    """Report admitted attempts only, for the declared observation interval.

    Caller must select the admission population in the same interval; do not
    treat admission as dispatch. The capture flag describes the supplied sink,
    not global coverage of the provider. Missing entries remain unavailable.
    """
    if type(start_ns) is not int or type(end_ns) is not int or start_ns >= end_ns or not scope.strip():
        raise ValueError("PPPR_EFFECT_INVALID_OBSERVATION_SCOPE")
    operations: dict[OperationKey, list[AttemptKey]] = {}
    for key, generation in admissions.items():
        task, execution = key
        if not task or not execution or len(generation) != 64 or any(c not in "0123456789abcdef" for c in generation):
            raise ValueError("PPPR_EFFECT_INVALID_ADMISSION_IDENTITY")
        operations.setdefault((task, generation), []).append(key)

    external = external_evidence or {}
    if set(external) - set(operations):
        raise ValueError("PPPR_EFFECT_UNATTRIBUTED_EXTERNAL_EVIDENCE")
    counts: dict[AttemptKey, int] = {}
    windows: dict[AttemptKey, int | None] = {}
    seen: set[tuple[str, AttemptKey, int]] = set()
    for event in events:
        kind = event.get("message")
        if kind not in (SDK_ENTRY, RECEIPT_WINDOW):
            continue
        task, execution, stamp = event.get("task_id"), event.get("execution_id"), event.get("observed_at_ns")
        if not isinstance(task, str) or not isinstance(execution, str) or not isinstance(kind, str):
            raise ValueError("PPPR_EFFECT_INVALID_EVENT_IDENTITY")
        key = (task, execution)
        if key not in admissions or type(stamp) is not int or not start_ns <= stamp <= end_ns:
            raise ValueError("PPPR_EFFECT_EVENT_OUTSIDE_SCOPE")
        identity = (kind, key, stamp)
        if identity in seen:
            raise ValueError("PPPR_EFFECT_DUPLICATE_CAPTURE_EVENT")
        seen.add(identity)
        if kind == SDK_ENTRY:
            counts[key] = counts.get(key, 0) + 1
        else:
            duration = event.get("duration_ns")
            classification = event.get("classification")
            if (event.get("generation_sha256") != admissions[key] or key in windows
                    or not ((type(duration) is int and duration >= 0 and classification == "MEASURED")
                            or (duration is None and classification == "NOT_OBSERVABLE"))):
                raise ValueError("PPPR_EFFECT_INVALID_RECEIPT_WINDOW")
            windows[key] = duration if isinstance(duration, int) else None

    rows: list[dict[str, object]] = []
    reexecuted = 0
    observed_operations = 0
    for operation, attempts in sorted(operations.items()):
        observed = sum(key in counts for key in attempts)
        observed_operations += int(observed > 0)
        entries = sum(counts.get(key, 0) for key in attempts)
        # More than one SDK entry is observable client repetition even if
        # the caller reused the same execution_id. Keep distinct attempt
        # identities separate from the count of SDK boundary crossings.
        reexecuted += int(entries > 1)
        evidence = external.get(operation)
        rows.append({
            "task_id": operation[0], "generation_sha256": operation[1],
            "client_activity": {
                "admitted_attempts": len(attempts),
                "observed_sdk_entry_attempts": observed,
                "observed_sdk_entries": entries,
                "repeated_sdk_entry_within_attempt": True if any(
                    counts.get(key, 0) > 1 for key in attempts
                ) else (False if capture_complete and observed == len(attempts) else None),
                "distinct_execution_ids_observed": observed,
                "reexecution_observed": True if entries > 1 else (
                    False if capture_complete and observed == len(attempts) else None
                ),
                "attempts": [{
                    "execution_id": key[1], "observed_sdk_entries": counts.get(key),
                    "client_receipt_window": {
                        "classification": "MEASURED" if windows.get(key) is not None else "NOT_OBSERVABLE",
                        "duration_ns": windows.get(key),
                        "boundary": "VALIDATED_BRIDGE_RETURN_TO_NEW_LOCAL_RECEIPT_COMMIT",
                    },
                } for key in sorted(attempts)],
            },
            "external_duplication": {
                "classification": evidence.classification() if evidence else "UNKNOWN",
                "scope": evidence.scope if evidence else "NO_VERIFIED_EXTERNAL_EVIDENCE",
                "inference_refs": evidence.inference_refs if evidence else (),
                "verified_applications": evidence.verified_applications if evidence else (),
                "confirmation_criterion": "MORE_THAN_ONE_DISTINCT_VERIFIED_ATTRIBUTED_APPLICATION",
            },
            "external_causal_window": {
                "classification": "NOT_OBSERVABLE", "duration_ns": None,
                "validated_upper_bound_ns": None,
            },
        })

    complete = capture_complete and len(counts) == len(admissions)
    return {
        "scope": scope, "start_ns": start_ns, "end_ns": end_ns,
        "operations": rows,
        "client_reexecution_rate": {
            "numerator": reexecuted, "denominator": observed_operations,
            "unit": "logical_operation_with_observed_sdk_entry",
            "start_ns": start_ns, "end_ns": end_ns,
            "coverage": {
                "admitted_attempts": len(admissions), "attempts_with_sdk_entry": len(counts),
                "attempts_with_measured_receipt_window": sum(v is not None for v in windows.values()),
                "admitted_operations": len(operations), "observed_operations": observed_operations,
                "capture_declared_complete": capture_complete,
            },
            "value": reexecuted / observed_operations if complete and observed_operations else None,
            "limitations": (
                "Admitted population only; pre-admission failures excluded. Numerator counts logical "
                "operations with multiple observed SDK entries, including within one execution ID. "
                "SDK entry is not HTTP "
                "delivery or remote application. Missing entries are unresolved, not no-start. "
                "Not comparable to provider-effect or billing rates."
            ),
        },
        "external_duplication_rate": None,
        "external_rate_limitation": "No denominator of verified external effects; not a zero rate.",
        "indirect_exposure_estimate": {
            "classification": "ESTIMATED" if indirect_estimate else "NOT_OBSERVABLE",
            "duration_ns": indirect_estimate.duration_ns if indirect_estimate else None,
            "basis_ref": indirect_estimate.basis_ref if indirect_estimate else None,
            "validated_upper_bound_ns": None,
        },
    }
