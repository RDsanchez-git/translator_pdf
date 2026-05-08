import os
import re
import logging
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from core.ast.models import ASTNode, NodeType

logger = logging.getLogger(__name__)

_converter = None
DEBUG_PARSER = True

def _get_converter():
    global _converter
    if _converter is None:
        logger.info("Cargando modelos pesados de Marker en memoria (solo la primera vez)...")
        _converter = PdfConverter(artifact_dict=create_model_dict())
    return _converter

def parse_pdf(pdf_path: str) -> list[ASTNode]:
    """Extrae contenido de PDF (Fase 4B: Parser con Tipado Estricto)."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")
    
    converter = _get_converter()
    rendered = converter(pdf_path)
    full_text = rendered.markdown
    
    blocks = re.split(r'\n{2,}', full_text)
    logger.info(f"Fase 4B: Marker finalizó. Bloques crudos detectados: {len(blocks)}")
    
    ast_nodes = []
    stop_keywords = ["# references", "# bibliography", "# referencias", "# bibliografía", "## references"]
    
    for idx, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
            
        if any(block.lower().startswith(kw) for kw in stop_keywords):
            logger.info(f"Corte por bibliografía en bloque {idx}. Extracción detenida.")
            break
            
        if re.search(r'\.{4,}', block):
            logger.info(f"Índice detectado y descartado en bloque {idx}.")
            continue
            
        node_type = NodeType.PARAGRAPH
        
        if re.match(r'^#+\s+', block):
            node_type = NodeType.SECTION
            block = re.sub(r'^#+\s*', '', block)
        
        # Saneamiento puramente estructural (NO de formato LaTeX)
        block = re.sub(r'!\[.*?\]\(.*?\)', '% [Imagen omitida]', block)
        
        if DEBUG_PARSER:
            preview = block[:150].replace('\n', ' ') + ("..." if len(block) > 150 else "")
            logger.info(f"Nodo {idx} [{node_type.value}]: {preview}")
        
        ast_nodes.append(ASTNode(
            node_id=f"node_{idx}",
            type=node_type,
            content=block,
            metadata={}
        ))
        
    logger.info(f"Fase 4B: {len(ast_nodes)} Nodos AST tipados inyectados.")
    return ast_nodes