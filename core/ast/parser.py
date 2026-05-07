import os
import re
import logging
# NUEVA API de Marker 1.0+
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from core.ast.models import ASTNode

logger = logging.getLogger(__name__)

_converter = None
DEBUG_PARSER = True  # Flag para observabilidad de Data Quality

def _get_converter():
    global _converter
    if _converter is None:
        logger.info("Cargando modelos pesados de Marker en memoria (solo la primera vez)...")
        # create_model_dict carga los modelos. PdfConverter inicializa el motor.
        _converter = PdfConverter(artifact_dict=create_model_dict())
    return _converter

def parse_pdf(pdf_path: str) -> list[ASTNode]:
    """Extrae contenido de PDF (Fase 4A: Bootstrap Parser con API SOTA)."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")
    
    # Invocamos la nueva API de extracción
    converter = _get_converter()
    rendered = converter(pdf_path)
    full_text = rendered.markdown
    
    # Separación SOTA por bloques semánticos de Markdown (doble salto de línea)
    blocks = re.split(r'\n{2,}', full_text)
    logger.info(f"Fase 4A: Marker finalizó. Bloques crudos detectados: {len(blocks)}")
    
    ast_nodes = []
    stop_keywords = ["# references", "# bibliography", "# referencias", "# bibliografía", "## references"]
    
    for idx, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
            
        if any(block.lower().startswith(kw) for kw in stop_keywords):
            logger.info(f"Corte por bibliografía en bloque {idx}. Extracción detenida.")
            break
            
        node_type = "text_block"
        if re.match(r'^#+\s+', block):
            node_type = "section"
            # SANEAMIENTO CAPA 2: Purgamos los '#' para que el LLM reciba texto limpio
            block = re.sub(r'^#+\s*', '', block)
        
        # SANEAMIENTO CAPA 2: Neutralizamos imágenes Markdown antes del LLM
        block = re.sub(r'!\[.*?\]\(.*?\)', '% [Imagen omitida]', block)
        
        # Observabilidad condicional
        if DEBUG_PARSER:
            preview = block[:150].replace('\n', ' ') + ("..." if len(block) > 150 else "")
            logger.info(f"Nodo {idx} [{node_type}]: {preview}")
        
        ast_nodes.append(ASTNode(
            node_id=f"node_{idx}",
            type=node_type,
            content=block
        ))
        
    logger.info(f"Fase 4A: Nodos AST válidos inyectados al pipeline: {len(ast_nodes)}")
    return ast_nodes