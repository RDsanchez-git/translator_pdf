from core.ast.models import TranslationUnit


class PromptBuilder:
    """SOTA: Constructor determinista que preserva las reglas críticas universales y el ruteo semántico."""
    PROMPT_VERSION = "v1.0"
    
    def build(self, unit: TranslationUnit) -> str:
        base_context = f"""---
ESTA ES LA PARTE {unit.chunk_index} DEL DOCUMENTO COMPLETO.

REGLAS CRÍTICAS UNIVERSALES:
- NO omitir contenido.
- NO resumir ni agregar explicaciones.
- NO inventar texto.
- Traducir fielmente manteniendo la terminología técnica."""
        
        context_window = ""
        if unit.reference_context:
            context_window = f"""\n\n[CONTEXTO PREVIO RELEVANTE - SOLO LECTURA]\n{unit.reference_context}"""

        # Corrección 1: Dependencia estricta de la propiedad semántica chunk_type
        type_context = ""
        if unit.chunk_type == "translate":
            type_context = """
INSTRUCCIONES PARA BLOQUE MACRO (TEXTO + ESTRUCTURA):
- Este bloque contiene múltiples párrafos agrupados.
- PROHIBIDO fusionar párrafos. Mantén estrictamente los saltos de línea originales (\\n\\n).
- Escapa caracteres reservados de LaTeX (%, &, _, #) si aparecen en texto plano.
- NO modifiques la estructura de comandos LaTeX si detectas alguno."""
        elif unit.chunk_type == "passthrough":
            # Fallback defensivo: El dispatcher bypassa esto, pero mantiene el contrato cerrado
            type_context = """
INSTRUCCIONES PARA ELEMENTO PROTEGIDO / ESTRUCTURAL:
- PROHIBIDO modificar símbolos matemáticos, alineaciones o código estructural LaTeX.
- Si hay texto legible, tradúcelo. El resto queda intacto."""
        else:
            type_context = """
INSTRUCCIONES GENERALES:
- Traduce el texto preservando exactamente el formato original."""

        return f"{base_context}{context_window}\n{type_context}\n---\n\nTEXT TO TRANSLATE:\n{unit.target_payload}\n\nOUTPUT:\n"