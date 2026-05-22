import json
import hashlib
import logging
from core.ast.models import ASTNode, NodeType

logger = logging.getLogger(__name__)

def compute_ast_hash(ast: list[ASTNode]) -> str:
    """SOTA: Generación determinística de firma para el árbol sintáctico completo."""
    def serialize_node(n: ASTNode) -> dict:
        return {
            "node_id": n.node_id,
            "type": str(n.type),
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
    """SOTA: Agrupación semántica de nodos crudos en Macro Chunks para optimización de LLM."""
    macro_nodes = []
    current_content = []
    current_len = 0
    chunk_idx = 1
    boundaries = {NodeType.SECTION}

    for node in ast:
        content = node.content or ""
        if content is None:
            continue
            
        is_boundary = node.type in boundaries
        if is_boundary and current_len > 800:
            macro_nodes.append(ASTNode(node_id=f"macro_{chunk_idx}", type=NodeType.MACRO_CHUNK, content="\n\n".join(current_content)))
            chunk_idx += 1
            current_content = []
            current_len = 0
            
        current_content.append(content)
        current_len += len(content)
        
        if current_len > 4000:
            macro_nodes.append(ASTNode(node_id=f"macro_{chunk_idx}", type=NodeType.MACRO_CHUNK, content="\n\n".join(current_content)))
            chunk_idx += 1
            current_content = []
            current_len = 0
            
    if current_content:
        macro_nodes.append(ASTNode(node_id=f"macro_{chunk_idx}", type=NodeType.MACRO_CHUNK, content="\n\n".join(current_content)))
        
    logger.info("macro_chunks_built", extra={"extra_data": {"count": len(macro_nodes)}})
    return macro_nodes