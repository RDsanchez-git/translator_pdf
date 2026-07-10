import os
import re
import json
import logging
import gc
import html
import io
import shutil  # SOTA: Requerido para la política de limpieza de assets masivos
from concurrent.futures import ThreadPoolExecutor  # SOTA: Paralelización thread-safe de CPU-bound tasks
import fitz  # PyMuPDF
import pymupdf4llm
import pytesseract
from PIL import Image

from core.ast.models import ASTNode, ContentNodeType
from core.ast.router import PDFRouter
from core.ast.models import (
    ParagraphPayload, ImagePayload, HeadingPayload,
    MathPayload, CodePayload, TablePayload, ListPayload,
    NodeMetadata
)

logger = logging.getLogger(__name__)

# SOTA Windows Guardrail: Configuración estricta del motor OCR
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA_PATH = r"C:\Program Files\Tesseract-OCR\tessdata"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
# Inyectar la variable de entorno de Tesseract directamente en el subproceso
os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH

DEBUG_PARSER = True
KEEP_ASSETS = True  # Modificado para congelar las imágenes en disco hasta la integración de Gemini Vision

EQUATION_BLOCK_PATTERNS = re.compile(
    r'(^\s*\$\$)|(\\begin\{(equation|align|aligned|gather)\*?\})|(^\s*\\\[)',
    re.MULTILINE | re.IGNORECASE
)
STEM_TABLE_ROW_PATTERN = re.compile(r'\w+[\w\s\.\%\-\,\(\)]*\s{2,}\w+')

def sanitize_marker_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<sup>\s*(&|&amp;)\s*</sup>\s*lt\s*;\s*sup\s*>', '<sup>', text, flags=re.IGNORECASE)
    text = re.sub(r'<sup>\s*(&|&amp;)\s*</sup>lt;sup>', '<sup>', text, flags=re.IGNORECASE)
    return html.unescape(text)

def _is_stem_table(block: str) -> bool:
    if '|' in block and re.search(r'\|[\s\-:]+\|', block):
        return True
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if len(lines) < 2:
        return False
    matching_rows = sum(1 for line in lines if STEM_TABLE_ROW_PATTERN.search(line))
    return (matching_rows / len(lines)) >= 0.75

def _run_tesseract_on_bytes(img_data: bytes) -> str:
    """Ejecuta OCR clásico en memoria libre de asignación de VRAM."""
    try:
        image = Image.open(io.BytesIO(img_data))
        return pytesseract.image_to_string(image)
    except Exception as e:
        logger.error(f"Fallo en subproceso pytesseract: {str(e)}")
        return ""

def _extract_document_text(pdf_path: str, pdf_type: str, empty_pages: list[int]) -> str:
    """Orquestador de extracción asimétrica con paralelización thread-safe en CPU."""
    image_dir = f"{pdf_path}_assets"
    
    os.makedirs(image_dir, exist_ok=True)
    
    if pdf_type == "DIGITAL":
        logger.info("Enrutando por Fast-Path: Extracción vectorial directa via PyMuPDF4LLM.")
        res = pymupdf4llm.to_markdown(doc=pdf_path, write_images=True, image_path=image_dir)
        return res if isinstance(res, str) else ""
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    pages_tasks = []
    
    for page_num in range(total_pages):
        if pdf_type == "HYBRID" and page_num not in empty_pages:
            page_md = pymupdf4llm.to_markdown(doc=doc, pages=[page_num], write_images=True, image_path=image_dir)
            page_md_str = page_md if isinstance(page_md, str) else ""
            pages_tasks.append((page_num, "DIGITAL", page_md_str))
        else:
            pix = doc[page_num].get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            pages_tasks.append((page_num, "OCR", img_data))
            
    doc.close()
    
    final_pages: list[str] = [""] * total_pages
    
    def _worker_task(task):
        page_num, task_type, data = task
        if task_type == "DIGITAL":
            return page_num, data
        else:
            text = _run_tesseract_on_bytes(data)
            return page_num, text + "\n\n"
            
    logger.info(f"Lanzando pool de paralelización para {total_pages} páginas...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(_worker_task, pages_tasks)
        
    for page_num, text in results:
        final_pages[page_num] = text
        
    return "".join(final_pages)

def _build_payload(n_type: ContentNodeType, content: str):
    """SOTA: Envoltura polimórfica hacia el Payload correcto."""
    if n_type == ContentNodeType.HEADING:
        return HeadingPayload(content=content)
    elif n_type in (ContentNodeType.DISPLAY_EQUATION, ContentNodeType.INLINE_EQUATION):
        return MathPayload(content=content)
    elif n_type in (ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX):
        return TablePayload(content=content)
    elif n_type == ContentNodeType.IMAGE:
        # SOTA FIX: Pylance Strict. ImagePayload no requiere content.
        return ImagePayload() 
    elif n_type == ContentNodeType.LIST:
        return ListPayload(content=content)
    elif n_type == ContentNodeType.CODE:
        return CodePayload(content=content)
    return ParagraphPayload(content=content)

def parse_pdf(pdf_path: str) -> list[ASTNode]:
    for node_attr in ["TABLE_SIMPLE", "IMAGE", "DISPLAY_EQUATION", "CAPTION", "LIST"]:
        if not hasattr(ContentNodeType, node_attr):
            raise RuntimeError(f"Falta inicializar la variante enum: ContentNodeType.{node_attr}")
            
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")
        
    ast_cache_path = f"{pdf_path}.ast.json"
    if os.path.exists(ast_cache_path):
        logger.info(f"AST recuperado desde disco ({ast_cache_path}). Saltando extracción...")
        with open(ast_cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [ASTNode(**node) for node in data]
        
    pdf_type, empty_pages = PDFRouter.detect_pdf_type(pdf_path)
    logger.info(f"Clasificación de Ingesta: {pdf_type} | Páginas Opacas: {len(empty_pages)}")
    
    # Inyección forzada temporal
    pdf_type, empty_pages = "OCR", []
    
    raw_markdown = _extract_document_text(pdf_path, pdf_type, empty_pages)
    full_text = sanitize_marker_html(raw_markdown)
    
    with open(f"{pdf_path}.debug.md", "w", encoding="utf-8") as dbg_f:
        dbg_f.write(full_text)
        
    del raw_markdown
    gc.collect()
    
    from core.ast.segmenter import MarkdownSegmenter
    segmenter = MarkdownSegmenter()
    blocks = segmenter.segment(full_text)
    
    logger.info(f"Fase 4B: Extracción finalizada. Bloques lógicos estructurados: {len(blocks)}")
    
    ast_nodes = []
    stop_keywords = ["# references", "# bibliography", "# referencias", "# bibliografía", "## references"]
    node_counter = 0

    for idx, block in enumerate(blocks):
        node_type: ContentNodeType = ContentNodeType.PARAGRAPH
        has_latex_open = bool(re.search(r'\\begin\{|\$\$', block[:50]))
        has_latex_close = bool(re.search(r'\\end\{|\$\$', block[-50:]))
        
        if has_latex_open and not has_latex_close:
            node_type = ContentNodeType.COMPOSITE_BLOCK
        elif re.match(r'^#+\s+', block):
            node_type = ContentNodeType.HEADING
            block = re.sub(r'^#+\s*', '', block)
            
        block = block.strip()
        if not block:
            continue
            
        if any(block.lower().startswith(kw) for kw in stop_keywords):
            logger.info(f"Corte por bibliografía en bloque {idx}. Extracción de bloques detenida.")
            break
            
        if re.search(r'\.{4,}', block):
            continue
            
        image_matches = list(re.finditer(r'!\[(.*?)\]\((.*?)\)', block))
        if image_matches:
            last_idx = 0
            
            for match in image_matches:
                text_before = block[last_idx:match.start()].strip()
                if text_before:
                    node_id = f"node_{node_counter}"
                    ast_nodes.append(ASTNode(
                        node_id=node_id,
                        sequence_id=len(ast_nodes) + 1,
                        node_type=ContentNodeType.PARAGRAPH,
                        payload=ParagraphPayload(content=text_before),
                        metadata=NodeMetadata()
                    ))
                    node_counter += 1
                
                image_node_id = f"node_{node_counter}"
                ast_nodes.append(ASTNode(
                    node_id=image_node_id,
                    sequence_id=len(ast_nodes) + 1,
                    node_type=ContentNodeType.IMAGE,
                    payload=ImagePayload(
                        alt_text=match.group(1),    # SOTA FIX: Eliminado el parámetro "content"
                        asset_path=match.group(2)   # SOTA FIX: Eliminado el parámetro "content"
                    ),   
                    metadata=NodeMetadata()
                ))
                node_counter += 1
                last_idx = match.end()
                
            text_after = block[last_idx:].strip()
            if text_after:
                ast_nodes.append(ASTNode(
                    node_id=f"node_{node_counter}",
                    sequence_id=len(ast_nodes) + 1,
                    node_type=ContentNodeType.PARAGRAPH,
                    payload=ParagraphPayload(content=text_after),
                    metadata=NodeMetadata()
                ))
                node_counter += 1
            continue
        
        if node_type == ContentNodeType.PARAGRAPH:
            if (match := EQUATION_BLOCK_PATTERNS.search(block)) is not None:
                if match.start() <= 15 or (match.end() - match.start()) / len(block) > 0.7:
                    node_type = ContentNodeType.DISPLAY_EQUATION
            elif _is_stem_table(block):
                node_type = ContentNodeType.TABLE_SIMPLE
            elif re.match(r'^\*\*Fig\b|^\*\*Table\b|^Fig\.\s|^Table\s|^Figure\s|^Chart\s|^Source\s', block, re.I):
                node_type = ContentNodeType.CAPTION
            elif block.startswith("- ") or block.startswith("* ") or re.match(r'^\d+\.\s', block):
                node_type = ContentNodeType.LIST
        
        if DEBUG_PARSER:
            preview = block[:150].replace('\n', ' ') + ("..." if len(block) > 150 else "")
            type_val = node_type.value if hasattr(node_type, "value") else str(node_type)
            logger.info(f"Nodo {node_counter} [{type_val}]: {preview}")
        
        ast_nodes.append(ASTNode(
            node_id=f"node_{node_counter}",
            sequence_id=len(ast_nodes) + 1,
            node_type=node_type,
            payload=_build_payload(node_type, block),
            metadata=NodeMetadata()
        ))
        node_counter += 1
        
    logger.info(f"Fase 4B: {len(ast_nodes)} Nodos AST tipados inyectados.")
    
    del full_text
    del blocks
    gc.collect()
    
    with open(ast_cache_path, "w", encoding="utf-8") as f:
        json.dump([n.model_dump() for n in ast_nodes], f, indent=2, ensure_ascii=False)
        
    if not KEEP_ASSETS:
        image_dir = f"{pdf_path}_assets"
        if os.path.exists(image_dir):
            logger.info(f"Política de limpieza activa: Removiendo directorio de assets {image_dir}")
            shutil.rmtree(image_dir)
            
    return ast_nodes