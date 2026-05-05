import os
import sys
import json
import hashlib
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Asegurar que el entorno reconozca el módulo raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ast.parser import load_mock_ast
from core.ast.models import ASTNode
from apps.llm_workers.gemini_client import GeminiClient
from apps.llm_workers.chunk_processor import ChunkProcessor, _safe_fallback
from apps.compiler.tex_builder import TexBuilder
from apps.compiler.docker_runner import DockerRunner
from core.utils.logger import setup_logger
from core.metrics.metrics import Metrics

# SOTA: Inicialización de telemetría y logs estructurados
setup_logger()
metrics = Metrics()
logger = logging.getLogger(__name__)

CHECKPOINT_INTERVAL = 5
CHECKPOINT_FILE = "checkpoint.json"

def compute_ast_hash(ast: list[ASTNode]) -> str:
    raw = json.dumps([
        {"node_id": n.node_id, "type": n.type, "content": n.content}
        for n in ast
    ], sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

# =========================
# Interceptor SOTA: Semantic Chunking (Purificado)
# =========================
def _build_semantic_chunks(ast: list[ASTNode]) -> list[ASTNode]:
    """Agrupa nodos microscópicos en macro-bloques semánticos seguros."""
    macro_nodes = []
    current_content = []
    current_len = 0
    chunk_idx = 1
    
    # Fronteras estructurales (Ajustado)
    boundaries = {"chapter", "section", "subsection", "subsubsection"}
    
    for node in ast:
        # FIX 1: Fuente de verdad pura (previene re-inyección en retries)
        content = node.content or ""
        
        # FIX 3: Evitar destrucción de nodos estructurales por un strip() agresivo
        if content is None:
            continue
            
        is_boundary = node.type in boundaries
        
        # FIX 7: Corte natural ajustado a 800 chars
        if is_boundary and current_len > 800:
            macro_nodes.append(ASTNode(
                node_id=f"macro_{chunk_idx}",
                type="text_block",
                content="\n\n".join(current_content) # FIX 5: Espaciado LaTeX seguro
            ))
            chunk_idx += 1
            current_content = []
            current_len = 0
            
        current_content.append(content)
        current_len += len(content)
        
        # Corte de emergencia
        if current_len > 4000:
            macro_nodes.append(ASTNode(
                node_id=f"macro_{chunk_idx}",
                type="text_block",
                content="\n\n".join(current_content)
            ))
            chunk_idx += 1
            current_content = []
            current_len = 0
            
    if current_content:
        macro_nodes.append(ASTNode(
            node_id=f"macro_{chunk_idx}",
            type="text_block",
            content="\n\n".join(current_content)
        ))
        
    # FIX 8: Sanity check log
    logger.info("macro_chunks_built", extra={"extra_data": {"count": len(macro_nodes)}})
    return macro_nodes


def main():
    pipeline_start = time.time()
    
    logger.info("1. Cargando AST y agrupando en Macro-Chunks...")
    raw_ast = load_mock_ast(mode="large")
    
    # FIX 6: Log para debugging de tipos reales
    logger.info("AST node types", extra={"extra_data": {"types": list(set(n.type for n in raw_ast))}})
    
    ast = _build_semantic_chunks(raw_ast)
    current_ast_hash = compute_ast_hash(ast)

    logger.info("2. Inicializando LLM y dependencias...")
    client = GeminiClient()
    processor = ChunkProcessor(client, metrics)

    ast_order_map = {n.node_id: idx for idx, n in enumerate(ast)}

    logger.info("3. Restaurando estado local...")
    processed = []
    processed_ids = set()
    
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if data.get("ast_hash") != current_ast_hash:
                logger.warning("Deriva de AST detectada. Hash no coincide. Ignorando checkpoint.")
            else:
                processed = [ASTNode(**n) for n in data.get("nodes", [])]
                processed_ids = {n.node_id for n in processed}
                logger.info(f"Retomando desde checkpoint. Macro-Chunks previamente procesados: {len(processed)}")
        except Exception as e:
            logger.warning(f"Fallo al leer checkpoint, iniciando desde cero: {e}")
            processed = []
            processed_ids = set()
    
    logger.info("4. Procesando Macro-Chunks en red...")
    
    processed_map = {n.node_id: n for n in processed}
    pending_nodes = [n for n in ast if n.node_id not in processed_ids]
    
    total_chunks = len(ast)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future_to_node = {}
        # FIX 2: Eliminación de loop O(N^2). Complejidad restaurada a O(N).
        for idx, node in enumerate(pending_nodes, 1):
            future = executor.submit(processor.process, node, idx, total_chunks)
            future_to_node[future] = node

        for count, future in enumerate(as_completed(future_to_node), 1):
            node = future_to_node[future]
            try:
                result = future.result()
                processed_map[node.node_id] = result
            except Exception as e:
                logger.error("fatal_thread_error", extra={"extra_data": {"node_id": node.node_id, "error": str(e)}})
                processed_map[node.node_id] = node.model_copy(
                    update={"latex": _safe_fallback(node.content), "status": "error"}
                )

            if count % CHECKPOINT_INTERVAL == 0 or count == len(pending_nodes):
                tmp_path = f"{CHECKPOINT_FILE}.tmp"
                
                ordered_current_nodes = sorted(
                    processed_map.values(), 
                    key=lambda x: ast_order_map.get(x.node_id, float('inf'))
                )
                
                payload = {
                    "ast_hash": current_ast_hash,
                    "nodes": [n.model_dump() for n in ordered_current_nodes]
                }
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
                os.replace(tmp_path, CHECKPOINT_FILE)
                logger.info("checkpoint_saved", extra={"extra_data": {"nodes_processed": len(processed_map)}})

    # --- Ensamblaje topológico final
    processed = list(processed_map.values())
    processed.sort(key=lambda x: ast_order_map.get(x.node_id, float('inf')))
    
    # --- Telemetría SOTA
    summary = metrics.summary()
    logger.info("metrics_summary", extra={"extra_data": summary})

    logger.info("5. Ensamblando LaTeX...")
    builder = TexBuilder()
    tex = builder.build(processed)
    
    debug_tex_path = "debug.tex"
    with open(debug_tex_path, "w", encoding="utf-8") as f:
        f.write(tex)
    
    logger.info("6. Compilando mediante Docker...")
    runner = DockerRunner()
    pdf_path = runner.compile(tex, output_filename="MVP_traduccion.pdf")
    
    total_time = time.time() - pipeline_start
    logger.info("pipeline_complete", extra={"extra_data": {
        "status": "success",
        "total_time_sec": round(total_time, 2),
        "artifact_path": pdf_path
    }})

if __name__ == "__main__":
    main()