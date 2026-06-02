from core.ast.models import ASTNode, ContentNodeType, StructuralNodeType

class PromptBuilder:
    @staticmethod
    def build(node: ASTNode, chunk_idx: int, total_chunks: int) -> str:
        # SOTA: Contexto base universal (Aplica a todo el documento)
        base_context = f"""---
        ESTA ES LA PARTE {chunk_idx} DE {total_chunks} DEL DOCUMENTO COMPLETO.

        REGLAS CRÍTICAS UNIVERSALES:
        - NO omitir contenido.
        - NO resumir ni agregar explicaciones.
        - NO inventar texto.
        - Traducir fielmente manteniendo la terminología técnica.
        """
        
        # SOTA: Enrutamiento dinámico (Strategy)
        type_context = ""
        
        if node.type == ContentNodeType.MACRO_CHUNK:
            type_context = """
            INSTRUCCIONES PARA BLOQUE MACRO (TEXTO + ESTRUCTURA):
            - Este bloque contiene múltiples párrafos agrupados.
            - PROHIBIDO fusionar párrafos. Mantén estrictamente los saltos de línea originales (\\n\\n).
            - Escapa caracteres reservados de LaTeX (%, &, _, #) si aparecen en texto plano.
            - NO modifiques la estructura de comandos LaTeX si detectas alguno.
            """
        elif node.type == StructuralNodeType.SECTION:
            type_context = """
            INSTRUCCIONES PARA TÍTULO/SECCIÓN:
            - Traduce de forma concisa. Es un encabezado estructural.
            - Mantén las mayúsculas iniciales si corresponde.
            """
        elif node.type == ContentNodeType.TABLE:
            type_context = """
            INSTRUCCIONES PARA TABLA:
            - PROHIBIDO traducir código estructural (alineaciones, bordes, comandos de celda).
            - Traduce ÚNICAMENTE el texto legible dentro de las celdas.
            """
        elif node.type == ContentNodeType.EQUATION:
            type_context = """
            INSTRUCCIONES PARA ECUACIÓN:
            - PROHIBIDO modificar símbolos matemáticos o renombrar variables.
            - Si hay texto dentro de comandos como \\text{}, tradúcelo. El resto queda intacto.
            """
        else:
            type_context = """
            INSTRUCCIONES GENERALES:
            - Traduce el texto preservando exactamente el formato original.
            """

        # Ensamblaje final
        return f"{base_context}\n{type_context}\n---\n\nTEXT TO TRANSLATE:\n{node.content}\n\nOUTPUT:\n"