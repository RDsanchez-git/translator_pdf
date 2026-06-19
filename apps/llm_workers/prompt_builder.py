import hashlib
from dataclasses import dataclass
from core.ast.models import TranslationUnit, TranslationTaskType, TokenEstimator
from core.context.context_resolver import ResolvedContext

@dataclass(frozen=True, slots=True)
class PromptEnvelope:
    """SOTA: Mensaje inmutable y autocontenido para la capa de inferencia."""
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

class PromptBuilder:
    """SOTA: Constructor determinista con cálculo de carga real y firmas estables."""
    
    def __init__(self, model_name: str, prompt_version: str, estimator: TokenEstimator):
        self.model_name = model_name
        self.prompt_version = prompt_version
        self.estimator = estimator

    def build(self, unit: TranslationUnit, context: ResolvedContext) -> PromptEnvelope:
        breadcrumbs_str = " > ".join(context.breadcrumbs) if context.breadcrumbs else "ROOT"
        
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

        system_prompt = f"{base_system}{type_instructions}"
        user_prompt = f"TEXT TO TRANSLATE:\n{unit.target_payload}\n\nOUTPUT:\n"

        hash_input = f"{self.model_name}|{self.prompt_version}|{system_prompt}|{user_prompt}"
        prompt_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
        prompt_id = f"prm_{prompt_hash[:16]}"

        total_estimated_tokens = self.estimator.estimate(system_prompt + user_prompt)

        return PromptEnvelope(
            prompt_id=prompt_id,
            chunk_id=unit.chunk_id,
            chunk_type=unit.chunk_type,
            model_name=self.model_name,
            prompt_version=self.prompt_version,
            prompt_hash=prompt_hash,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            raw_payload=unit.target_payload,  # Inyección directa
            estimated_tokens=total_estimated_tokens
        )