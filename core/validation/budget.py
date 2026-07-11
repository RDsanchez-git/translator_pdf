from enum import Enum
from dataclasses import dataclass
from typing import Protocol, List
from core.prompting.models import PromptSchema
from core.prompting.canonicalizer import PromptCanonicalizer
from core.validation.budget_models import BudgetDecision, PromptBudget, BudgetDecisionType, BudgetViolationReason, ContextReductionLevel
from core.finops.measurement import InferenceMeasurement

class TokenEstimatorProtocol(Protocol):
    """SOTA: Puerto Hexagonal para estimación (FastWordEstimator, TikToken, SentencePiece)."""
    def estimate_tokens(self, text: str) -> int: ...

class BudgetViolationReason(str, Enum):
    NONE = "none"
    PAYLOAD_TOO_LARGE = "payload_too_large"
    SYSTEM_PROMPT_TOO_LARGE = "system_prompt_too_large"
    CONTEXT_TOO_LARGE = "context_too_large"
    OUTPUT_RESERVE_TOO_LARGE = "output_reserve_too_large"

class BudgetDecisionType(str, Enum):
    VALID = "valid"
    COMPRESS_CONTEXT = "compress_context"
    SWITCH_MODEL = "switch_model"
    REJECT = "reject"

class ContextReductionLevel(str, Enum):
    FULL = "full"
    HEADINGS = "headings"
    BREADCRUMBS = "breadcrumbs"
    NONE = "none"

# SOTA FIX: Inversión de dependencias para políticas de compresión
class ContextCompressionPolicy(Protocol):
    """SOTA: Protocolo inyectable para estrategias de compresión iterativa de contexto."""
    def get_levels(self) -> List[ContextReductionLevel]: ...

class StandardCompressionPolicy(ContextCompressionPolicy):
    def get_levels(self) -> List[ContextReductionLevel]:
        return [
            ContextReductionLevel.HEADINGS,
            ContextReductionLevel.BREADCRUMBS,
            ContextReductionLevel.NONE
        ]

@dataclass(frozen=True, slots=True)
class PromptBudget:
    """SOTA: Trazabilidad FinOps y SRE de la construcción del sobre."""
    system_tokens: int
    context_tokens: int
    payload_tokens: int
    reserved_tokens: int
    window_limit: int

    @property
    def total_estimated(self) -> int:
        return self.system_tokens + self.context_tokens + self.payload_tokens + self.reserved_tokens

    @property
    def utilization_ratio(self) -> float:
        return self.total_estimated / self.window_limit if self.window_limit > 0 else 0.0

@dataclass(frozen=True, slots=True)
class BudgetDecision:
    """SOTA: DTO Inmutable con directivas deterministas de enrutamiento y degradación."""
    status: BudgetDecisionType
    violation_reason: BudgetViolationReason
    budget: PromptBudget
    suggested_context_level: ContextReductionLevel
    max_allowed_context_tokens: int = 0
    required_window_size: int = 0

class PromptBudgetCalculator:
    """SOTA: Validador algebraico acoplado exclusivamente a la abstracción de medida."""
    
    def __init__(self, primary_window_limit: int = 8192, fallback_window_limit: int = 1048576, min_output_reserve: int = 256, max_output_reserve: int = 4096):
        # NOTA: El TokenEstimatorProtocol fue inyectado al PromptMeasurer. 
        # El Calculator ya no necesita conocer cómo estimar, solo cómo calcular finanzas.
        self.primary_window_limit = primary_window_limit
        self.fallback_window_limit = fallback_window_limit
        self.min_output_reserve = min_output_reserve
        self.max_output_reserve = max_output_reserve

    def calculate(self, measurement: InferenceMeasurement, expansion_factor: float = 1.2) -> BudgetDecision:
        sys_tok = measurement.instruction_tokens + measurement.structural_overhead
        ctx_tok = measurement.context_tokens
        pay_tok = measurement.payload_tokens

        dyn_reserve = int(pay_tok * expansion_factor)
        reserve = min(self.max_output_reserve, max(self.min_output_reserve, dyn_reserve))

        initial_budget = PromptBudget(sys_tok, ctx_tok, pay_tok, reserve, self.primary_window_limit)
        core_tokens = sys_tok + pay_tok + reserve

        if initial_budget.total_estimated <= self.primary_window_limit:
            return BudgetDecision(
                status=BudgetDecisionType.VALID,
                violation_reason=BudgetViolationReason.NONE,
                budget=initial_budget,
                suggested_context_level=ContextReductionLevel.FULL,
                max_allowed_context_tokens=self.primary_window_limit - core_tokens,
                required_window_size=core_tokens
            )

        remaining_for_context = self.primary_window_limit - core_tokens

        if remaining_for_context > 0:
            return BudgetDecision(
                status=BudgetDecisionType.COMPRESS_CONTEXT,
                violation_reason=BudgetViolationReason.CONTEXT_TOO_LARGE,
                budget=initial_budget,
                suggested_context_level=ContextReductionLevel.HEADINGS,
                max_allowed_context_tokens=remaining_for_context,
                required_window_size=core_tokens
            )

        if core_tokens <= self.fallback_window_limit:
            # SOTA FIX: Evaluamos si el rechazo fue por el payload o por reglas de negocio pesadas
            reason = BudgetViolationReason.PAYLOAD_TOO_LARGE if pay_tok > sys_tok else BudgetViolationReason.SYSTEM_PROMPT_TOO_LARGE
            return BudgetDecision(
                status=BudgetDecisionType.SWITCH_MODEL,
                violation_reason=reason,
                budget=initial_budget,
                suggested_context_level=ContextReductionLevel.FULL,
                max_allowed_context_tokens=self.fallback_window_limit - core_tokens,
                required_window_size=core_tokens + ctx_tok
            )

        return BudgetDecision(
            status=BudgetDecisionType.REJECT,
            violation_reason=BudgetViolationReason.PAYLOAD_TOO_LARGE,
            budget=initial_budget,
            suggested_context_level=ContextReductionLevel.NONE,
            max_allowed_context_tokens=0,
            required_window_size=core_tokens + ctx_tok
        )