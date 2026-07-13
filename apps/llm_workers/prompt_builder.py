# apps/llm_workers/prompt_builder.py
from typing import Optional, Literal, Union, Dict, Any, List
from dataclasses import dataclass, field

from core.ast.models import TranslationUnit, TranslationTaskType
from core.context.context_resolver import ResolvedContext
from core.validation.budget import PromptBudget, BudgetViolationReason, BudgetDecisionType, ContextReductionLevel, ContextCompressionPolicy
from core.prompting.models import PromptSchema, PromptContext, PromptPayload
from core.prompting.intent_mapper import PromptIntentMapper
from core.prompting.constraint_factory import ConstraintFactory
from core.prompting.canonicalizer import PromptCanonicalizer
from core.finops.measurement import InferenceMeasurementService
from core.prompting.measurement_adapter import PromptMeasurementAdapter
from core.validation.budget import PromptBudgetCalculator

def _empty_telemetry() -> Dict[str, Any]:
    return {}

@dataclass(frozen=True, slots=True)
class PromptEnvelope:
    prompt_id: str
    chunk_id: str
    chunk_type: TranslationTaskType
    model_name: str
    prompt_version: str
    prompt_hash: str
    schema: PromptSchema
    estimated_tokens: int
    budget_stats: PromptBudget
    telemetry: Dict[str, Any] = field(default_factory=_empty_telemetry)
    target_provider: str = "primary"

@dataclass(frozen=True, slots=True)
class BuildSuccess:
    status: Literal["success"]
    envelope: PromptEnvelope

@dataclass(frozen=True, slots=True)
class BuildFailure:
    status: Literal["failed"]
    error_reason: BudgetViolationReason
    message: str
    budget_stats: Optional[PromptBudget] = None

PromptBuildResult = Union[BuildSuccess, BuildFailure]

class PromptBuilder:
    def __init__(
        self, 
        model_name: str, 
        prompt_version: str, 
        measurement_service: InferenceMeasurementService, 
        budget_calculator: PromptBudgetCalculator,
        compression_policy: ContextCompressionPolicy
    ):
        self.model_name = model_name
        self.prompt_version = prompt_version
        self.measurement_service = measurement_service
        self.budget_calculator = budget_calculator
        self.compression_policy = compression_policy

    def build(self, unit: TranslationUnit, resolved_context: ResolvedContext, target_lang_expansion: float = 1.2) -> PromptBuildResult:
        if not unit.target_payload:
            return BuildFailure(status="failed", error_reason=BudgetViolationReason.NONE, message="Target payload vacío.")

        intent = PromptIntentMapper.map_from_task(unit.chunk_type)
        constraints = ConstraintFactory.create_for_task(unit.chunk_type)
        payload = PromptPayload(content=unit.target_payload)

        best_schema: Optional[PromptSchema] = None
        decision = None
        final_level = ContextReductionLevel.NONE

        evaluation_levels = [ContextReductionLevel.FULL] + self.compression_policy.get_levels()

        for level in evaluation_levels:
            # SOTA FIX: Casting explícito a lista para cumplir la firma de PromptContext
            current_breadcrumbs: List[str] = list(resolved_context.breadcrumbs) if level in [ContextReductionLevel.FULL, ContextReductionLevel.BREADCRUMBS] else []
            is_pruned = level != ContextReductionLevel.FULL

            test_schema = PromptSchema(
                intent=intent,
                context=PromptContext(
                    chunk_index=unit.chunk_index,
                    depth=resolved_context.depth,
                    breadcrumbs=current_breadcrumbs,
                    is_pruned=is_pruned
                ),
                constraints=constraints,
                payload=payload
            )
            
            measurable = PromptMeasurementAdapter(test_schema)
            measurement = self.measurement_service.measure(measurable)
            decision = self.budget_calculator.calculate(measurement, target_lang_expansion)

            if decision.status in (BudgetDecisionType.VALID, BudgetDecisionType.SWITCH_MODEL):
                best_schema = test_schema
                final_level = level
                break

        if not best_schema or not decision or decision.status == BudgetDecisionType.REJECT:
            reason = decision.violation_reason if decision else BudgetViolationReason.NONE
            stats = decision.budget if decision else None
            return BuildFailure(status="failed", error_reason=reason, message="Presupuesto excedido tras máxima compresión.", budget_stats=stats)

        prompt_hash = PromptCanonicalizer.compute_hash(best_schema)
        
        # SOTA FIX: Tipado estricto en la instanciación local
        telemetry: Dict[str, Any] = {
            "utilization_ratio": decision.budget.utilization_ratio,
            "decision": decision.status.value,
            "compression_level": final_level.value
        }

        envelope = PromptEnvelope(
            prompt_id=f"prm_{prompt_hash[:16]}",
            chunk_id=unit.chunk_id,
            chunk_type=unit.chunk_type,
            model_name=self.model_name,
            prompt_version=self.prompt_version,
            prompt_hash=prompt_hash,
            schema=best_schema,
            estimated_tokens=decision.budget.total_estimated,
            budget_stats=decision.budget,
            telemetry=telemetry,
            target_provider="fallback_large_window" if decision.status == BudgetDecisionType.SWITCH_MODEL else "primary"
        )
        
        return BuildSuccess(status="success", envelope=envelope)