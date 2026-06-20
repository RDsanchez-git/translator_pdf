import hashlib
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Literal, Union
from core.ast.models import TranslationUnit, TranslationTaskType, TokenEstimator
from core.context.context_resolver import ResolvedContext

class BuildFailureReason(str, Enum):
    """SOTA: Taxonomía determinista de fallos en construcción."""
    CONTEXT_OVERFLOW = "context_overflow"
    MISSING_TARGET_PAYLOAD = "missing_target_payload"

@dataclass(frozen=True, slots=True)
class PromptBudget:
    estimated_input: int
    safe_input: int
    output_reserve: int
    total_required: int
    window_limit: int
    pruning_level: int
    predicted_tpm: int

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

# =====================================================================
# SOTA: DISCRIMINATED UNION (Result Pattern Estricto)
# Erradica los estados inválidos (ej. success=True pero envelope=None)
# =====================================================================

@dataclass(frozen=True, slots=True)
class BuildSuccess:
    status: Literal["success"]
    envelope: PromptEnvelope
    budget_stats: PromptBudget

@dataclass(frozen=True, slots=True)
class BuildFailure:
    status: Literal["failed"]
    error_reason: BuildFailureReason
    message: str
    budget_stats: Optional[PromptBudget] = None

PromptBuildResult = Union[BuildSuccess, BuildFailure]

# =====================================================================

class AdaptiveBudgetManager:
    @staticmethod
    def calculate(system_prompt: str, user_prompt: str, payload: str, 
                  estimator: TokenEstimator, window_limit: int, pruning_level: int) -> PromptBudget:
        
        input_tokens = estimator.estimate(system_prompt + user_prompt)
        payload_tokens = estimator.estimate(payload)
        output_reserve = int(payload_tokens * 1.3)
        safe_input = int(input_tokens * 1.2)
        total_required = safe_input + output_reserve
        predicted_tpm = input_tokens + output_reserve

        return PromptBudget(
            estimated_input=input_tokens,
            safe_input=safe_input,
            output_reserve=output_reserve,
            total_required=total_required,
            window_limit=window_limit,
            pruning_level=pruning_level,
            predicted_tpm=predicted_tpm
        )

class PromptBuilder:
    def __init__(self, model_name: str, prompt_version: str, estimator: TokenEstimator, 
                 context_window: int = 8192, enforce_budget: bool = True):
        self.model_name = model_name
        self.prompt_version = prompt_version
        self.estimator = estimator
        self.context_window = context_window
        self.enforce_budget = enforce_budget

    def _build_system(self, unit: TranslationUnit, context: ResolvedContext, pruning_level: int) -> str:
        if pruning_level >= 1 or not context.breadcrumbs:
            breadcrumbs_str = "CONTEXTO OMITIDO (PRUNED)"
        else:
            breadcrumbs_str = " > ".join(context.breadcrumbs)
            
        if pruning_level >= 2:
            base_system = (
                f"PARTE {unit.chunk_index}.\n"
                f"Profundidad: Nivel {context.depth}\n"
                f"REGLAS: Traducir fielmente, no omitir, no resumir."
            )
        else:
            base_system = (
                f"ESTA ES LA PARTE {unit.chunk_index} DEL DOCUMENTO COMPLETO.\n"
                f"[CONTEXTO ESTRUCTURAL]\n"
                f"Jerarquía Lógica: {breadcrumbs_str}\n"
                f"Profundidad: Nivel {context.depth}\n\n"
                f"REGLAS CRÍTICAS UNIVERSALES:\n"
                f"- NO omitir contenido.\n"
                f"- NO resumir ni agregar explicaciones.\n"
                f"- NO inventar texto.\n"
                f"- Traducir fielmente manteniendo la terminología técnica."
            )

        type_instructions = ""
        if unit.chunk_type == TranslationTaskType.TRANSLATE:
            if pruning_level >= 2:
                type_instructions = "\nMACRO: Mantén saltos de línea (\\n\\n). Escapa LaTeX reservado."
            else:
                type_instructions = (
                    "\nINSTRUCCIONES PARA BLOQUE MACRO:\n"
                    "- PROHIBIDO fusionar párrafos. Mantén estrictamente los saltos de línea originales (\\n\\n).\n"
                    "- Escapa caracteres reservados de LaTeX (%, &, _, #) si aparecen en texto plano.\n"
                    "- NO modifiques la estructura de comandos LaTeX si detectas alguno."
                )
        elif unit.chunk_type == TranslationTaskType.PARTIAL:
            if pruning_level >= 2:
                type_instructions = "\nHÍBRIDO: Traduce SOLO texto natural. Mantén grilla/LaTeX."
            else:
                type_instructions = (
                    "\nINSTRUCCIONES PARA ELEMENTOS HÍBRIDOS:\n"
                    "- Traduce EXCLUSIVAMENTE el texto natural (captions, celdas de texto).\n"
                    "- MANTÉN INTACTA la grilla Markdown o la estructura LaTeX."
                )
        elif unit.chunk_type == TranslationTaskType.PRESERVE:
            if pruning_level >= 2:
                type_instructions = "\nPROTEGIDO: NO MODIFICAR. DEVUELVE IGUAL."
            else:
                type_instructions = (
                    "\nINSTRUCCIONES PROTEGIDAS:\n"
                    "- PROHIBIDO modificar contenido. DEVUELVE EL TEXTO EXACTAMENTE IGUAL."
                )

        return f"{base_system}{type_instructions}"

    def build(self, unit: TranslationUnit, context: ResolvedContext) -> PromptBuildResult:
        # 1. Validación temprana
        if not unit.target_payload:
            return BuildFailure(
                status="failed",
                error_reason=BuildFailureReason.MISSING_TARGET_PAYLOAD, 
                message="Target payload vacío.",
                budget_stats=None
            )

        user_prompt = f"TEXT TO TRANSLATE:\n{unit.target_payload}\n\nOUTPUT:\n"
        
        # 2. Bypass (Testing / Forzado)
        if not self.enforce_budget or self.context_window <= 0:
            system_prompt = self._build_system(unit, context, pruning_level=0)
            dummy_budget = PromptBudget(0, 0, 0, 0, self.context_window, 0, 0)
            envelope = self._forge_envelope(unit, system_prompt, user_prompt, dummy_budget)
            return BuildSuccess(status="success", envelope=envelope, budget_stats=dummy_budget)

        # 3. Cascading Pruning
        budget = None
        for current_level in range(3):
            system_prompt = self._build_system(unit, context, pruning_level=current_level)
            budget = AdaptiveBudgetManager.calculate(
                system_prompt, user_prompt, unit.target_payload, 
                self.estimator, self.context_window, current_level
            )
            
            if budget.total_required <= self.context_window:
                envelope = self._forge_envelope(unit, system_prompt, user_prompt, budget)
                return BuildSuccess(status="success", envelope=envelope, budget_stats=budget)
                
        assert budget is not None
        
        # 4. Fallo Determinista sin excepciones (Context Overflow)
        return BuildFailure(
            status="failed",
            error_reason=BuildFailureReason.CONTEXT_OVERFLOW,
            message=f"Requerido: {budget.total_required} (SafeInput: {budget.safe_input}, OutputReserve: {budget.output_reserve})",
            budget_stats=budget
        )

    def _forge_envelope(self, unit: TranslationUnit, system_prompt: str, user_prompt: str, budget: PromptBudget) -> PromptEnvelope:
        hash_input = f"{self.model_name}|{self.prompt_version}|{system_prompt}|{user_prompt}"
        prompt_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
        
        return PromptEnvelope(
            prompt_id=f"prm_{prompt_hash[:16]}",
            chunk_id=unit.chunk_id,
            chunk_type=unit.chunk_type,
            model_name=self.model_name,
            prompt_version=self.prompt_version,
            prompt_hash=prompt_hash,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            raw_payload=unit.target_payload,
            estimated_tokens=budget.estimated_input,
            budget_stats=budget
        )