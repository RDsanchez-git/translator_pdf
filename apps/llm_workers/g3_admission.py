"""Offline-verifiable G3 pre-effect admission against the Groq wire request.

No configured provider, quota or estimator by itself grants egress or spending.
No default production approval policy is constructed. The explicit caller
must attest a real policy; test-only positives do not attest a commercial account.
"""
from dataclasses import dataclass
from decimal import Decimal, DecimalException
from hashlib import sha256
import json
import time
from typing import Any, NoReturn

from apps.llm_workers.prompt_builder import PromptEnvelope
from core.execution.exceptions import G3ExternalEffectNotStartedError
from core.prompting.dialects.openai_compatible import InferenceDialect, OpenAICompatibleDialect
from core.prompting.renderer import PromptRenderer
from core.validation.protocols import TokenEstimatorProtocol


GPT_OSS_120B = "openai/gpt-oss-120b"


def build_groq_request_kwargs(
    envelope: PromptEnvelope, dialect: InferenceDialect,
) -> tuple[dict[str, Any], str]:
    """Single request construction used by admission AND the actual adapter."""
    reserve = envelope.budget_stats.reserved_tokens
    if type(reserve) is not int or reserve <= 0:
        raise G3ExternalEffectNotStartedError("PPPR_G3_OUTPUT_RESERVE_INVALID")
    rendered = PromptRenderer.render(envelope.schema)
    kwargs: dict[str, Any] = {
        "model": envelope.model_name,
        "temperature": 1e-5,
        "stream": False,
        "max_completion_tokens": reserve,
        **dialect.build_request_kwargs(rendered),
    }
    if envelope.model_name == GPT_OSS_120B:
        # Keep reasoning explicit and bounded by the same output reserve.
        # No tools, browsing, service-tier upgrade or alternate model.
        kwargs.update(reasoning_effort="low", include_reasoning=False)
    return kwargs, rendered.expected_output_key


@dataclass(frozen=True, slots=True)
class GroqHarmonyInputBound:
    """Conditional upper bound for the supported two-message GPT-OSS request.

    Every ordinary byte-level BPE token consumes at least one UTF-8 byte.
    Count the decoded message contents by bytes, not the escaped HTTP JSON.
    The caller MUST independently attest a ceiling for ALL additional
    server tokens (roles, separators, system/developer instructions, response
    format, reasoning configuration and assistant prefix), including any
    content transformation beyond the supplied message bytes. Neither the
    local vocabulary nor the public Harmony format attests Groq's deployment.

    No default framing allowance, implicit acquisition or provider request.
    Reference: https://developers.openai.com/cookbook/articles/openai-harmony
    """
    framing_token_ceiling: int
    framing_evidence_ref: str

    def __post_init__(self) -> None:
        if (type(self.framing_token_ceiling) is not int
                or self.framing_token_ceiling <= 0
                or not isinstance(self.framing_evidence_ref, str)
                or not self.framing_evidence_ref.strip()):
            raise ValueError("PPPR_G6_HARMONY_FRAMING_EVIDENCE_REQUIRED")

    def estimate_tokens(self, text: str) -> int:
        # This estimator is a wire-contract adapter, not a generic text
        # tokenizer. Reject any additional features rather than undercount.
        try:
            wire = json.loads(text)
            if (not isinstance(wire, dict) or set(wire) != {
                    "model", "temperature", "stream", "max_completion_tokens",
                    "messages", "response_format", "reasoning_effort", "include_reasoning",
                } or wire["model"] != GPT_OSS_120B
                    or wire["temperature"] != 1e-5 or wire["stream"] is not False
                    or wire["response_format"] != {"type": "json_object"}
                    or wire["reasoning_effort"] != "low"
                    or wire["include_reasoning"] is not False
                    or type(wire["max_completion_tokens"]) is not int
                    or not 0 < wire["max_completion_tokens"] <= 4096):
                raise ValueError("unsupported request")
            messages = wire["messages"]
            if not isinstance(messages, list) or len(messages) != 2:
                raise ValueError("unsupported messages")
            content_bytes = 0
            for message, role in zip(messages, ("system", "user"), strict=True):
                if (not isinstance(message, dict) or set(message) != {"role", "content"}
                        or message["role"] != role or not isinstance(message["content"], str)):
                    raise ValueError("unsupported message")
                content_bytes += len(message["content"].encode("utf-8"))
            # The admission caller supplies this exact canonical serialization.
            # Reject duplicate keys, noncanonical or ambiguous alternate JSON.
            if text != json.dumps(wire, ensure_ascii=False, sort_keys=True,
                                  separators=(",", ":"), allow_nan=False):
                raise ValueError("noncanonical request")
        except (ValueError, TypeError, KeyError, RecursionError) as exc:
            raise ValueError("PPPR_G6_HARMONY_WIRE_UNSUPPORTED") from exc
        return content_bytes + self.framing_token_ceiling


@dataclass(frozen=True, slots=True)
class G3AdmissionDecision:
    """Operational admission facts, never scientific identity."""
    request_sha256: str
    audit_json: str


def _deny(code: str, *, permanent: bool = True) -> NoReturn:
    raise G3ExternalEffectNotStartedError(code, permanent=permanent)


@dataclass(frozen=True, slots=True)
class GroqFreeTierWitness:
    """Operator-attributed, short-lived free entitlement and quota evidence.

    The default is one historical witness. A document-bound snapshot may
    authorize a bounded batch; the durable journal conservatively debits all
    reserved requests/tokens without refill or refund during that snapshot.
    No account API, implicit authority, or proof of provider accounting.
    The caller must attest the actual account/project, exclusive quota scope,
    evidence, and conservative estimator before constructing this object.
    """

    witness_id: str
    account_evidence_ref: str
    quota_evidence_ref: str
    free_entitlement_ref: str
    observed_at_ns: int
    valid_until_ns: int
    remaining_rpm: int
    remaining_rpd: int
    remaining_tpm: int
    remaining_tpd: int
    plan: str
    no_billable_overage: bool
    global_zdr: bool
    model_allowed: bool
    # Default remains the historical one-shot witness. Only an explicitly
    # document-bound snapshot can reserve multiple requests.
    document_id: str | None = None
    max_requests: int = 1

    def verify(self, *, model_name: str, target_provider: str,
               combined_tokens: int) -> dict[str, object]:
        if (model_name != GPT_OSS_120B or target_provider != "primary"
                or self.plan != "FREE" or self.no_billable_overage is not True
                or self.global_zdr is not True or self.model_allowed is not True
                or not all(isinstance(v, str) and v.strip() for v in (
                    self.witness_id, self.account_evidence_ref,
                    self.quota_evidence_ref, self.free_entitlement_ref,
                ))):
            _deny("PPPR_G5_FREE_ENTITLEMENT_NOT_ACCREDITED")
        now = time.time_ns()
        if (type(self.observed_at_ns) is not int or type(self.valid_until_ns) is not int
                or not self.observed_at_ns <= now < self.valid_until_ns
                or self.valid_until_ns - self.observed_at_ns > 300_000_000_000):
            _deny("PPPR_G5_FREE_EVIDENCE_STALE")
        for name, remaining, ceiling, needed in (
            ("RPM", self.remaining_rpm, 30, 1),
            ("RPD", self.remaining_rpd, 1000, 1),
            ("TPM", self.remaining_tpm, 8000, combined_tokens),
            ("TPD", self.remaining_tpd, 200000, combined_tokens),
        ):
            if type(remaining) is not int or not 0 <= remaining <= ceiling:
                _deny("PPPR_G5_FREE_QUOTA_INVALID_" + name)
            if remaining < needed:
                _deny("PPPR_G5_FREE_QUOTA_INSUFFICIENT_" + name)
        if (type(self.max_requests) is not int or self.max_requests < 1
                or (self.document_id is None and self.max_requests != 1)
                or (self.document_id is not None and (
                    not isinstance(self.document_id, str)
                    or len(self.document_id) != 64
                    or any(c not in "0123456789abcdef" for c in self.document_id)
                    or self.max_requests > min(self.remaining_rpm, self.remaining_rpd)
                ))):
            _deny("PPPR_G6_FREE_DOCUMENT_SCOPE_INVALID")
        scope = ({"document_id": self.document_id, "max_requests": self.max_requests}
                 if self.document_id is not None else {})
        return {
            **scope,
            "witness_id": self.witness_id, "plan": self.plan,
            "account_evidence_ref": self.account_evidence_ref,
            "quota_evidence_ref": self.quota_evidence_ref,
            "free_entitlement_ref": self.free_entitlement_ref,
            "observed_at_ns": self.observed_at_ns, "valid_until_ns": self.valid_until_ns,
            "remaining_rpm": self.remaining_rpm, "remaining_rpd": self.remaining_rpd,
            "remaining_tpm": self.remaining_tpm, "remaining_tpd": self.remaining_tpd,
            "reserved_requests": 1, "reserved_tokens": combined_tokens,
            "no_billable_overage": True, "global_zdr": True, "model_allowed": True,
        }


@dataclass(frozen=True, slots=True)
class G3PreEffectAdmission:
    """Explicit, request-scoped policy, never constructed by product defaults.

    Approval refs are *inputs from competent authority*, not inferred from
    installed credentials. The offline witnesses are deliberately synthetic.
    """
    provider_id: str
    model_name: str
    root_config_sha256: str
    input_limit: int
    output_limit: int
    context_window: int
    input_estimator: TokenEstimatorProtocol
    estimator_evidence_ref: str
    egress_authorization_ref: str
    data_scope_ref: str
    purpose_ref: str
    retention_ref: str
    training_use_ref: str
    budget_authorization_ref: str
    price_evidence_ref: str
    input_price_per_token: Decimal
    output_price_per_token: Decimal
    authorized_max_cost: Decimal
    free_tier_witness: GroqFreeTierWitness | None = None

    def measure_request(self, envelope: PromptEnvelope) -> tuple[str, int, int]:
        """Local sizing only. Never grants authority, consumes quota or records a decision."""
        if self.model_name != envelope.model_name:
            _deny("PPPR_G3_ADMISSION_SELECTION_DRIFT")
        if not self.estimator_evidence_ref:
            _deny("PPPR_G3_ESTIMATOR_NOT_ACCREDITED")
        if (isinstance(self.input_estimator, GroqHarmonyInputBound)
                and self.input_estimator.framing_evidence_ref != self.estimator_evidence_ref):
            _deny("PPPR_G6_HARMONY_FRAMING_EVIDENCE_DRIFT")
        wire, _ = build_groq_request_kwargs(envelope, OpenAICompatibleDialect())
        serialized = json.dumps(wire, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        try:
            count = self.input_estimator.estimate_tokens(serialized)
        except Exception as exc:
            raise G3ExternalEffectNotStartedError(
                "PPPR_G3_ESTIMATOR_FAILED"
            ) from exc
        reserve = envelope.budget_stats.reserved_tokens
        if (type(count) is not int or count <= 0
                or type(self.input_limit) is not int or self.input_limit <= 0
                or type(self.output_limit) is not int or self.output_limit <= 0
                or type(self.context_window) is not int or self.context_window <= 0):
            _deny("PPPR_G3_MEASUREMENT_OR_LIMIT_INVALID")
        if count > self.input_limit:
            _deny("PPPR_G3_INPUT_LIMIT_EXCEEDED")
        if reserve > self.output_limit:
            _deny("PPPR_G3_OUTPUT_LIMIT_EXCEEDED")
        if count + reserve > self.context_window:
            _deny("PPPR_G3_CONTEXT_WINDOW_EXCEEDED")
        return serialized, count, reserve

    def verify(
        self, *, provider_id: str, root_config_sha256: str,
        envelope: PromptEnvelope,
    ) -> G3AdmissionDecision:
        if (self.provider_id != provider_id or self.model_name != envelope.model_name
                or self.root_config_sha256 != root_config_sha256):
            _deny("PPPR_G3_ADMISSION_SELECTION_DRIFT")
        serialized, count, reserve = self.measure_request(envelope)
        if not all((self.egress_authorization_ref, self.data_scope_ref,
                    self.purpose_ref, self.retention_ref, self.training_use_ref)):
            _deny("PPPR_G3_EGRESS_NOT_AUTHORIZED")
        amounts = (self.input_price_per_token, self.output_price_per_token,
                   self.authorized_max_cost)
        if (not self.budget_authorization_ref or not self.price_evidence_ref
                or any(not isinstance(x, Decimal) or not x.is_finite() or x < 0
                       for x in amounts)):
            _deny("PPPR_G3_BUDGET_NOT_AUTHORIZED")
        try:
            upper_cost = (count * self.input_price_per_token
                          + reserve * self.output_price_per_token)
        except (DecimalException, TypeError, ValueError) as exc:
            raise G3ExternalEffectNotStartedError(
                "PPPR_G3_BUDGET_NOT_AUTHORIZED", permanent=True,
            ) from exc
        if not upper_cost.is_finite():
            _deny("PPPR_G3_BUDGET_NOT_AUTHORIZED")
        nominal_upper_cost = upper_cost
        free_audit: dict[str, object] | None = None
        if self.model_name == GPT_OSS_120B or self.free_tier_witness is not None:
            if (self.free_tier_witness is None or provider_id != "groq"
                    or self.authorized_max_cost != Decimal("0")
                    or self.input_price_per_token <= 0 or self.output_price_per_token <= 0):
                _deny("PPPR_G5_FREE_ENTITLEMENT_NOT_ACCREDITED")
            free_audit = self.free_tier_witness.verify(
                model_name=self.model_name, target_provider=envelope.target_provider,
                combined_tokens=count + reserve,
            )
            if self.free_tier_witness.document_id is not None:
                try:
                    document_id = json.loads(envelope.schema.payload.content)["response_binding"]["document_id"]
                except (TypeError, ValueError, KeyError) as exc:
                    raise G3ExternalEffectNotStartedError(
                        "PPPR_G6_FREE_DOCUMENT_BINDING_INVALID", permanent=True,
                    ) from exc
                if document_id != self.free_tier_witness.document_id:
                    _deny("PPPR_G6_FREE_DOCUMENT_BINDING_INVALID")
            # Conditional zero billable cap based on explicit free entitlement.
            # Preserve the nominal tariff, never fabricate a zero price.
            upper_cost = Decimal("0")
        if upper_cost > self.authorized_max_cost:
            _deny("PPPR_G3_BUDGET_CAP_EXCEEDED")
        digest = sha256(serialized.encode("utf-8")).hexdigest()
        # Operational audit: no source content, credentials or attempt in generation key.
        evidence: dict[str, object] = {
            "contract": "PPPR_G3_ADMISSION_V1",
            "request_sha256": digest, "provider_id": provider_id,
            "model_name": envelope.model_name,
            "root_config_sha256": root_config_sha256,
            "target_provider": envelope.target_provider,
            "source_language": "en", "target_language": "es",
            "input_tokens": count, "reserved_output_tokens": reserve,
            "input_limit": self.input_limit, "output_limit": self.output_limit,
            "context_window": self.context_window,
            "estimator_evidence_ref": self.estimator_evidence_ref,
            "egress_authorization_ref": self.egress_authorization_ref,
            "data_scope_ref": self.data_scope_ref,
            "purpose_ref": self.purpose_ref,
            "retention_ref": self.retention_ref,
            "training_use_ref": self.training_use_ref,
            "budget_authorization_ref": self.budget_authorization_ref,
            "price_evidence_ref": self.price_evidence_ref,
            "input_price_per_token": str(self.input_price_per_token),
            "output_price_per_token": str(self.output_price_per_token),
            "authorized_max_cost": str(self.authorized_max_cost),
            "upper_bound_cost": str(upper_cost),
        }
        if isinstance(self.input_estimator, GroqHarmonyInputBound):
            evidence.update(
                input_bound_method="UTF8_MESSAGE_BYTES_PLUS_ATTESTED_FRAMING_V1",
                framing_token_ceiling=self.input_estimator.framing_token_ceiling,
            )
        if free_audit is not None:
            evidence.update(
                free_tier_witness=free_audit,
                nominal_upper_bound_cost=str(nominal_upper_cost),
                cost_basis="CONDITIONAL_FREE_ENTITLEMENT_NOT_BILLING_EVIDENCE",
            )
        return G3AdmissionDecision(
            request_sha256=digest,
            audit_json=json.dumps(evidence, sort_keys=True,
                                  ensure_ascii=False, separators=(",", ":")),
        )
