import hashlib
from typing import Optional, Literal, Union
from core.ast.models import TranslationUnit, TranslationTaskType
from core.context.context_resolver import ResolvedContext

# SOTA: Integración estricta con el nuevo motor de validación algebraica (Fase 15.2)
from core.validation.budget import (
    PromptBudgetCalculator, 
    BudgetDecisionType, 
    ContextReductionLevel, 
    StandardCompressionPolicy,
    ContextCompressionPolicy,
    TokenEstimatorProtocol,
    PromptBudget,
    BudgetViolationReason
)

# =====================================================================
# SOTA: DISCRIMINATED UNION (Result Pattern Estricto)
# =====================================================================

from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class PromptEnvelope:
    prompt_id: str
    chunk_id: str
    chunk_type: TranslationTaskType
    model_name: str
    prompt_version: str
    prompt_hash: str
    system_prompt: str
    user_prompt: str
    raw_payload: str
    estimated_tokens: int
    budget_stats: PromptBudget
    telemetry: dict = field(default_factory=dict)
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

# =====================================================================

class PromptBuilder:
    def __init__(
        self, 
        model_name: str, 
        prompt_version: str, 
        budget_calculator: PromptBudgetCalculator, 
        estimator: TokenEstimatorProtocol,
        compression_policy: Optional[ContextCompressionPolicy] = None
    ):
        self.model_name = model_name
        self.prompt_version = prompt_version
        self.budget_calculator = budget_calculator
        self.estimator = estimator
        # SOTA FIX: Instanciar la política concreta, no el Protocolo
        self.compression_policy = compression_policy or StandardCompressionPolicy()

    def _build_system(self, unit: TranslationUnit, context: str, is_pruned: bool, depth: int) -> str:
        if is_pruned or not context:
            breadcrumbs_str = "CONTEXTO OMITIDO (PRUNED)"
        else:
            breadcrumbs_str = context
            
        base_system = (
            f"ESTA ES LA PARTE {unit.chunk_index} DEL DOCUMENTO COMPLETO.\n"
            f"[CONTEXTO ESTRUCTURAL]\n"
            f"Jerarquía Lógica: {breadcrumbs_str}\n"
            f"Profundidad: Nivel {depth}\n\n"
            f"REGLAS CRÍTICAS UNIVERSALES:\n"
            f"- NO omitir contenido.\n"
            f"- NO resumir ni agregar explicaciones.\n"
            f"- NO inventar texto.\n"
            f"- Traducir fielmente manteniendo la terminología técnica."
        )

        type_instructions = ""
        if unit.chunk_type == TranslationTaskType.TRANSLATE:
            type_instructions = (
                "\nINSTRUCCIONES PARA BLOQUE MACRO:\n"
                "- PROHIBIDO fusionar párrafos. Mantén estrictamente los saltos de línea originales (\\n\\n).\n"
                "- Escapa caracteres reservados de LaTeX (%, &, _, #) si aparecen en texto plano.\n"
                "- NO modifiques la estructura de comandos LaTeX si detectas alguno."
            )
        elif unit.chunk_type == TranslationTaskType.PARTIAL:
            type_instructions = (
                "\nINSTRUCCIONES PARA ELEMENTOS HÍBRIDOS:\n"
                "- Traduce EXCLUSIVAMENTE el texto natural (captions, celdas de texto).\n"
                "- MANTÉN INTACTA la grilla Markdown o la estructura LaTeX."
            )
        elif unit.chunk_type == TranslationTaskType.PRESERVE:
            type_instructions = (
                "\nINSTRUCCIONES PROTEGIDAS:\n"
                "- PROHIBIDO modificar contenido. DEVUELVE EL TEXTO EXACTAMENTE IGUAL."
            )

        return f"{base_system}{type_instructions}"

    def build(self, unit: TranslationUnit, resolved_context: ResolvedContext, target_lang_expansion: float = 1.2) -> PromptBuildResult:
        # 1. Validación temprana
        if not unit.target_payload:
            return BuildFailure(
                status="failed",
                error_reason=BudgetViolationReason.NONE, 
                message="Target payload vacío.",
                budget_stats=None
            )

        # 2. Extracción de niveles de contexto
        # Nota: Asume que resolved_context provee propiedades o diccionarios para los niveles.
        full_context_str = " > ".join(resolved_context.breadcrumbs) if resolved_context.breadcrumbs else ""
        context_levels = {
            ContextReductionLevel.FULL: full_context_str,
            ContextReductionLevel.HEADINGS: full_context_str, # Simplificado para el ejemplo
            ContextReductionLevel.BREADCRUMBS: full_context_str.split(" > ")[-1] if full_context_str else "",
            ContextReductionLevel.NONE: ""
        }
        
        full_context = context_levels.get(ContextReductionLevel.FULL, "")
        
        # 3. Creación del System Prompt Base (requerido para calcular budget)
        base_system_prompt = self._build_system(unit, full_context, is_pruned=False, depth=resolved_context.depth)
        user_prompt = f"TEXT TO TRANSLATE:\n{unit.target_payload}\n\nOUTPUT:\n"

        # 4. Cálculo Algebraico (Fase 15.2 SOTA)
        decision = self.budget_calculator.calculate(
            system_text=base_system_prompt,
            context_text=full_context,
            payload_text=user_prompt,
            expansion_factor=target_lang_expansion
        )
        
        telemetry = {
            "utilization_ratio": decision.budget.utilization_ratio,
            "decision": decision.status.value,
            "violation_reason": decision.violation_reason.value,
            "required_window": decision.required_window_size,
        }

        # 5. Aplicación de Directivas de Enrutamiento y Degradación
        target_provider = "primary"
        final_context_str = full_context
        is_pruned = False

        if decision.status == BudgetDecisionType.VALID:
            pass # Mantiene full_context
            
        elif decision.status == BudgetDecisionType.COMPRESS_CONTEXT:
            final_context_str = ""
            is_pruned = True
            # SOTA FIX: Usar el método del protocolo, no un atributo
            for level in self.compression_policy.get_levels():
                test_ctx = context_levels.get(level, "")
                if self.estimator.estimate_tokens(test_ctx) <= decision.max_allowed_context_tokens:
                    final_context_str = test_ctx
                    telemetry["compression_level"] = level.value
                    is_pruned = (level != ContextReductionLevel.FULL)
                    break
                    
        elif decision.status == BudgetDecisionType.SWITCH_MODEL:
            target_provider = "fallback_large_window"
            
        else: # REJECT (Fallo determinista)
            return BuildFailure(
                status="failed",
                error_reason=decision.violation_reason,
                message=f"Presupuesto excedido (Razón: {decision.violation_reason.value}). Requerido: {decision.required_window_size}",
                budget_stats=decision.budget
            )
            
        # 6. Ensamblado Final (Construcción del Sobre Seguro)
        final_system_prompt = self._build_system(unit, final_context_str, is_pruned=is_pruned, depth=resolved_context.depth)
        
        hash_input = f"{self.model_name}|{self.prompt_version}|{final_system_prompt}|{user_prompt}"
        prompt_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
        
        envelope = PromptEnvelope(
            prompt_id=f"prm_{prompt_hash[:16]}",
            chunk_id=unit.chunk_id,
            chunk_type=unit.chunk_type,
            model_name=self.model_name,
            prompt_version=self.prompt_version,
            prompt_hash=prompt_hash,
            system_prompt=final_system_prompt,
            user_prompt=user_prompt,
            raw_payload=unit.target_payload,
            # SOTA FIX: Uso de la propiedad canónica del DTO
            estimated_tokens=decision.budget.total_estimated,
            budget_stats=decision.budget,
            telemetry=telemetry,
            target_provider=target_provider
        )
        
        return BuildSuccess(status="success", envelope=envelope)