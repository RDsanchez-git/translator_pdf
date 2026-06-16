from core.ast.models import TranslationUnit, TranslationTaskType

class PromptBuilder:
    """SOTA: Constructor determinista alineado al contrato de Fase 13."""
    PROMPT_VERSION = "v1.1"
    
    def build(self, unit: TranslationUnit) -> str:
        base_context = f"""---
ESTA ES LA PARTE {unit.chunk_index} DEL DOCUMENTO COMPLETO.

REGLAS CRÍTICAS UNIVERSALES:
- NO omitir contenido.
- NO resumir ni agregar explicaciones.
- NO inventar texto.
- Traducir fielmente manteniendo la terminología técnica."""
        
        # SOTA: Preparado para Fase 14. Aquí se consultará el context_registry vía SQLite usando el context_id.
        context_window = f"""\n\n[CONTEXTO ESTRUCTURAL (FASE 13)]
ID Lógico: {unit.context_id}
Profundidad: Nivel {unit.context_depth}"""

        # Corrección estricta: Dependencia del Enum tipado (TranslationTaskType)
        type_context = ""
        if unit.chunk_type == TranslationTaskType.TRANSLATE:
            type_context = """
INSTRUCCIONES PARA BLOQUE MACRO (TEXTO + ESTRUCTURA):
- Este bloque contiene múltiples párrafos agrupados.
- PROHIBIDO fusionar párrafos. Mantén estrictamente los saltos de línea originales (\\n\\n).
- Escapa caracteres reservados de LaTeX (%, &, _, #) si aparecen en texto plano.
- NO modifiques la estructura de comandos LaTeX si detectas alguno."""
        elif unit.chunk_type == TranslationTaskType.PARTIAL:
            type_context = """
INSTRUCCIONES PARA ELEMENTOS HÍBRIDOS (TABLAS / FIGURAS):
- Traduce EXCLUSIVAMENTE el texto natural (captions, celdas de texto).
- MANTÉN INTACTA la grilla Markdown o la estructura LaTeX."""
        elif unit.chunk_type == TranslationTaskType.PRESERVE:
            # Fallback defensivo: El dispatcher bypassa esto, pero mantiene el contrato cerrado
            type_context = """
INSTRUCCIONES PARA ELEMENTO PROTEGIDO / ESTRUCTURAL:
- PROHIBIDO modificar símbolos matemáticos, alineaciones o código estructural.
- DEVUELVE EL PAYLOAD EXACTAMENTE IGUAL AL ORIGINAL."""
        else:
            type_context = """
INSTRUCCIONES GENERALES:
- Traduce el texto preservando exactamente el formato original."""

        return f"{base_context}{context_window}\n{type_context}\n---\n\nTEXT TO TRANSLATE:\n{unit.target_payload}\n\nOUTPUT:\n"