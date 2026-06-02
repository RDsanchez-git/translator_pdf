import json
import hashlib
import logging
from core.ast.models import ASTNode, ContentNodeType, StructuralNodeType

logger = logging.getLogger(__name__)

def compute_ast_hash(ast: list[ASTNode]) -> str:
    """SOTA: Generación determinística de firma para el árbol sintáctico completo."""
    def serialize_node(n: ASTNode) -> dict:
        # Usamos .value para extraer el string nativo puro ('paragraph', 'section', etc.)
        type_str = n.type.value if hasattr(n.type, "value") else str(n.type)
        return {
            "node_id": n.node_id,
            "type": type_str,
            "content": n.content,
            "latex": getattr(n, "latex", None),
            "children": [serialize_node(c) for c in getattr(n, "children", [])] if getattr(n, "children", None) else []
        }
        
    raw = json.dumps(
        [serialize_node(n) for n in ast], 
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def build_semantic_chunks(ast: list[ASTNode]) -> list[ASTNode]:
    """SOTA: Agrupación semántica segura con preservación topológica y memoria optimizada O(1)."""
    macro_nodes = []
    current_content = []
    absorbed_nodes = []  
    current_len = 0
    chunk_idx = 1
    
    STRUCTURAL_BOUNDARIES = {
        StructuralNodeType.DOCUMENT,
        StructuralNodeType.PART,
        StructuralNodeType.CHAPTER,
        StructuralNodeType.SECTION,
        StructuralNodeType.SUBSECTION
    }
    
    PROTECTED_CONTENT_TYPES = {
        ContentNodeType.EQUATION,
        ContentNodeType.INLINE_EQUATION,
        ContentNodeType.TABLE,
        ContentNodeType.CODE_BLOCK,
        ContentNodeType.ALGORITHM,
        ContentNodeType.FIGURE,
        ContentNodeType.IMAGE,
        ContentNodeType.COMPOSITE_BLOCK,
        ContentNodeType.UNKNOWN,
        ContentNodeType.CITATION,
        ContentNodeType.REFERENCE_ENTRY,
        ContentNodeType.BIBLIOGRAPHY
    }

    def flush_current_chunk():
        nonlocal chunk_idx, current_content, current_len, absorbed_nodes
        if current_content:
            first_seq_id = absorbed_nodes[0].sequence_id if absorbed_nodes else -1
            last_seq_id = absorbed_nodes[-1].sequence_id if absorbed_nodes else -1
            
            macro_nodes.append(ASTNode(
                node_id=f"macro_{chunk_idx}",
                sequence_id=first_seq_id,
                type=ContentNodeType.MACRO_CHUNK,
                content="\n\n".join(current_content),
                metadata={
                    # Optimización SOTA: Rango O(1) inmutable en lugar de listado dinámico de strings
                    "source_sequence_range": (first_seq_id, last_seq_id)
                }
            ))
            chunk_idx += 1
            current_content = []
            absorbed_nodes = []
            current_len = 0

    for node in ast:
        content = node.content or ""

        if node.type in STRUCTURAL_BOUNDARIES:
            flush_current_chunk()
            macro_nodes.append(node)
            continue

        # Corte duro inmediato ante cualquier nodo de contenido protegido por passthrough
        if node.type in PROTECTED_CONTENT_TYPES:
            flush_current_chunk()
            macro_nodes.append(node)
            continue

        if not content:
            continue
            
        current_content.append(content)
        absorbed_nodes.append(node)
        current_len += len(content)
        
        if current_len > 4000:
            flush_current_chunk()
            
    flush_current_chunk()
    
    logger.info("macro_chunks_built", extra={"extra_data": {"count": len(macro_nodes)}})
    return macro_nodes