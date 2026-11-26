"""G6 offline request sizing. No provider, policy fabrication or persistence.

A framing scenario is a mathematical assumption for planning only. Neither a
positive margin nor successful refinement authorizes inference. Callers retain
the original manifest; a candidate is never enqueued by this module.
"""
from collections.abc import Sequence
from dataclasses import dataclass
import json

from apps.bootstrap.provider_stack_factory import build_product_prompt_builder
from apps.llm_workers.g3_admission import GroqHarmonyInputBound, build_groq_request_kwargs
from apps.llm_workers.sync_bridge import prepare_chunk_prompt
from core.ast.models import ASTNode, TranslationTaskType, TranslationUnit
from core.chunking.manifest_contract import ChunkPlan
from core.chunking.semantic_chunking import refine_chunk_plan
from core.context.plan_context_contract import derive_verified_plan_contexts
from core.execution.exceptions import G3ExternalEffectNotStartedError
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
from core.validation.protocols import TokenEstimatorProtocol


@dataclass(frozen=True, slots=True)
class RequestBudgetObservation:
    chunk_index: int
    member_count: int
    message_bytes: int
    reserved_output_tokens: int
    framing_headroom: int


@dataclass(frozen=True, slots=True)
class ProductBudgetPreview:
    original_manifest_sha256: str
    candidate_manifest_sha256: str
    original_units: int
    candidate_units: int
    preserve_units: int
    framing_scenario: int
    requests: tuple[RequestBudgetObservation, ...]
    max_common_framing_tokens: int | None
    # This is a diagnostic, never a G3 admission decision.
    status: str = "OFFLINE_CONDITIONAL_SIZING_ONLY"


def preview_product_budget(
    plan: ChunkPlan, ast: Sequence[ASTNode], estimator: TokenEstimatorProtocol,
    *, framing_scenario: int = 0,
) -> ProductBudgetPreview:
    """Rebuild the real request and refine a disposable candidate if needed.

    Zero is an observation of headroom before any framing allowance; a
    positive scenario is explicitly hypothetical. A result does not attest
    the server, authorize a quota window, or estimate actual billed tokens.
    """
    if type(framing_scenario) is not int or not 0 <= framing_scenario < 8000:
        raise ValueError("PPPR_G6_PREVIEW_SCENARIO_INVALID")
    builder = build_product_prompt_builder(estimator)
    snapshots = derive_verified_plan_contexts(plan, ast)

    def measure(candidate: ChunkPlan, unit: TranslationUnit) -> RequestBudgetObservation:
        built, _, _ = prepare_chunk_prompt(
            candidate, unit, builder=builder, context_snapshots=snapshots,
            structured_response=True,
        )
        wire, _ = build_groq_request_kwargs(built.envelope, OpenAICompatibleDialect())
        serialized = json.dumps(wire, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        message_bytes = GroqHarmonyInputBound.measure_message_bytes(serialized)
        reserve = built.envelope.budget_stats.reserved_tokens
        return RequestBudgetObservation(
            unit.chunk_index, len(unit.members), message_bytes, reserve,
            8000 - message_bytes - reserve,
        )

    def fits(candidate: ChunkPlan, unit: TranslationUnit) -> bool:
        try:
            observed = measure(candidate, unit)
        except G3ExternalEffectNotStartedError as exc:
            if (str(exc) == "PPPR_G3_FALLBACK_BACKEND_NOT_ACCREDITED"
                    or str(exc).startswith("G3_B4_3A_PROMPT_REJECTED:")):
                return False
            raise
        # Require room for at least one framing token even when the
        # scenario is zero. Do not claim a zero-framing request fits.
        return observed.framing_headroom >= max(1, framing_scenario)

    candidate = refine_chunk_plan(plan, ast, estimator, fits)
    observations = tuple(
        measure(candidate, unit) for unit in candidate.units
        if unit.chunk_type != TranslationTaskType.PRESERVE
    )
    return ProductBudgetPreview(
        original_manifest_sha256=plan.digest,
        candidate_manifest_sha256=candidate.digest,
        original_units=len(plan.units), candidate_units=len(candidate.units),
        preserve_units=len(candidate.units) - len(observations),
        framing_scenario=framing_scenario, requests=observations,
        max_common_framing_tokens=min(
            (row.framing_headroom for row in observations), default=None,
        ),
    )
