"""Offline-verifiable G3 pre-effect admission against the Groq wire request.

No configured provider, quota or estimator by itself grants egress or spending.
Production currently supplies NO approval policy: this fails closed. Test-only
positive policies use a fake provider and do not attest a commercial account.
"""
from dataclasses import dataclass
from decimal import Decimal, DecimalException
from hashlib import sha256
import json
from typing import Any, NoReturn

from apps.llm_workers.prompt_builder import PromptEnvelope
from core.execution.exceptions import G3ExternalEffectNotStartedError
from core.prompting.dialects.openai_compatible import InferenceDialect, OpenAICompatibleDialect
from core.prompting.renderer import PromptRenderer
from core.validation.protocols import TokenEstimatorProtocol


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
    return kwargs, rendered.expected_output_key


@dataclass(frozen=True, slots=True)
class G3AdmissionDecision:
    """Operational admission facts, never scientific identity."""
    request_sha256: str
    audit_json: str


def _deny(code: str, *, permanent: bool = True) -> NoReturn:
    raise G3ExternalEffectNotStartedError(code, permanent=permanent)


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

    def verify(
        self, *, provider_id: str, root_config_sha256: str,
        envelope: PromptEnvelope,
    ) -> G3AdmissionDecision:
        if (self.provider_id != provider_id or self.model_name != envelope.model_name
                or self.root_config_sha256 != root_config_sha256):
            _deny("PPPR_G3_ADMISSION_SELECTION_DRIFT")
        if not self.estimator_evidence_ref:
            _deny("PPPR_G3_ESTIMATOR_NOT_ACCREDITED")
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
        if upper_cost > self.authorized_max_cost:
            _deny("PPPR_G3_BUDGET_CAP_EXCEEDED")
        digest = sha256(serialized.encode("utf-8")).hexdigest()
        # Operational audit: no source content, credentials or attempt in generation key.
        evidence = {
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
        return G3AdmissionDecision(
            request_sha256=digest,
            audit_json=json.dumps(evidence, sort_keys=True,
                                  ensure_ascii=False, separators=(",", ":")),
        )
