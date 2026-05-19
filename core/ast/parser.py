import os
import re
import json
import logging
import gc

# SOTA: Gobernanza térmica estricta
os.environ["MIN_BATCH_SIZE"] = "1"
os.environ["MAX_BATCH_SIZE"] = "2"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import torch
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

from marker.converters.pdf import PdfConverter #noqa
from marker.models import create_model_dict #noqa
from core.ast.models import ASTNode, NodeType #noqa

logger = logging.getLogger(__name__)

_converter = None
DEBUG_PARSER = True

def _get_converter():
    global _converter
    if _converter is None:
        logger.info("Cargando Marker optimizado para papers STEM (Single-Thread)...")
        model_dict = create_model_dict()
        
        # SOTA: Amputación de módulos no críticos para STEM
        keys_to_drop = ["table_recognition", "ocr_error_detection"]
        for k in keys_to_drop:
            if k in model_dict:
                logger.info(f"Desactivando submódulo pesado: {k}")
                del model_dict[k]
                
        _converter = PdfConverter(artifact_dict=model_dict)
    return _converter

def parse_pdf(pdf_path: str) -> list[ASTNode]:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")

    ast_cache_path = f"{pdf_path}.ast.json"

    if os.path.exists(ast_cache_path):
        logger.info(f"AST recuperado desde disco ({ast_cache_path}). Saltando Marker OCR...")
        with open(ast_cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [ASTNode(**node) for node in data]

    converter = _get_converter()
    rendered = converter(pdf_path)
    full_text = rendered.markdown
    
    # SOTA: Destrucción explícita de tensores huérfanos y estructuras pesadas post-inferencia
    del rendered
    gc.collect()
    
    # SOTA: Stream-friendly split
    blocks = full_text.split("\n\n")
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
            continue
            
        node_type = NodeType.PARAGRAPH
        
        if re.match(r'^#+\s+', block):
            node_type = NodeType.SECTION
            block = re.sub(r'^#+\s*', '', block)
        
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

    # SOTA: Segunda purga antes del volcado I/O
    del full_text
    del blocks
    gc.collect()

    with open(ast_cache_path, "w", encoding="utf-8") as f:
        json.dump([n.model_dump() for n in ast_nodes], f, indent=2, ensure_ascii=False)

    return ast_nodes