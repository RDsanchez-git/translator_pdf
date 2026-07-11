from dataclasses import dataclass
from core.prompting.models import PromptSchema

@dataclass(frozen=True)
class RenderedPrompt:
    system_text: str
    user_text: str
    expected_output_key: str  # Delega la clave esperada al parseador

class PromptRenderer:
    """SOTA: Transforma la intención semántica en instrucciones textuales."""
    
    @staticmethod
    def render(schema: PromptSchema) -> RenderedPrompt:
        ctx = schema.context
        breadcrumbs_str = " > ".join(ctx.breadcrumbs) if not ctx.is_pruned and ctx.breadcrumbs else "CONTEXTO OMITIDO (PRUNED)"
        
        # La estrategia JSON se inyecta aquí, en el dominio, no en el dialecto HTTP
        system_text = (
            f"INTENT: {schema.intent.value}\n"
            f"TOPOLOGY: Part {ctx.chunk_index}, Depth {ctx.depth}\n"
            f"BREADCRUMBS: {breadcrumbs_str}\n"
            f"CONSTRAINTS: {schema.constraints.model_dump_json(exclude_none=True)}\n\n"
            f"CRITICAL INSTRUCTION: You must respond ONLY with a valid JSON object. "
            f"The root key must be 'content' containing the resulting text."
        )
        
        return RenderedPrompt(
            system_text=system_text,
            user_text=schema.payload.content,
            expected_output_key="content"
        )