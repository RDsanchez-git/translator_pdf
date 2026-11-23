"""Offline-verifiable G3 pre-effect admission against the Groq wire request.

No configured provider, quota or estimator by itself grants egress or spending.
Production currently supplies NO approval policy: this fails closed. Test-only
positive policies use a fake provider and do not attest a commercial account.
"""
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any

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
    ) -> str:
        if (self.provider_id != provider_id or self.model_name != envelope.model_name
                or self.root_config_sha256 != root_config_sha256):
            raise G3ExternalEffectNotStartedError("PPPR_G3_ADMISSION_SELECTION_DRIFT")
        if not self.estimator_evidence_ref:
            raise G3ExternalEffectNotStartedError("PPPR_G3_ESTIMATOR_NOT_ACCREDITED")

        wire, _ = build_groq_request_kwargs(envelope, OpenAICompatibleDialect())
        serialized = json.dumps(wire, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        count = self.input_estimator.estimate_tokens(serialized)
        reserve = envelope.budget_stats.reserved_tokens
        if (not isinstance(count, int) or isinstance(count, bool) or count <= 0
                or self.input_limit <= 0 or self.output_limit <= 0
                or self.context_window <= 0):
            raise G3ExternalEffectNotStartedError("PPPR_G3_MEASUREMENT_OR_LIMIT_INVALID")
        if count > self.input_limit:
            raise G3ExternalEffectNotStartedError("PPPR_G3_INPUT_LIMIT_EXCEEDED")
        if reserve > self.output_limit:
            raise G3ExternalEffectNotStartedError("PPPR_G3_OUTPUT_LIMIT_EXCEEDED")
        if count + reserve > self.context_window:
            raise G3ExternalEffectNotStartedError("PPPR_G3_CONTEXT_WINDOW_EXCEEDED")

        if not all((
            self.egress_authorization_ref, self.data_scope_ref,
            self.purpose_ref, self.retention_ref, self.training_use_ref,
        )):
            raise G3ExternalEffectNotStartedError("PPPR_G3_EGRESS_NOT_AUTHORIZED")
        if (not self.budget_authorization_ref or not self.price_evidence_ref
                or self.input_price_per_token < 0 or self.output_price_per_token < 0
                or self.authorized_max_cost < 0):
            raise G3ExternalEffectNotStartedError("PPPR_G3_BUDGET_NOT_AUTHORIZED")
        upper_cost = (count * self.input_price_per_token
                      + reserve * self.output_price_per_token)
        if upper_cost > self.authorized_max_cost:
            raise G3ExternalEffectNotStartedError("PPPR_G3_BUDGET_CAP_EXCEEDED")
        # No protected content is persisted in the decision identifier.
        return sha256(serialized.encode("utf-8")).hexdigest()
