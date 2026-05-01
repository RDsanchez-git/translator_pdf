import os
import sys
import time
import json
import hashlib
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ast.parser import load_mock_ast
from core.ast.models import ASTNode
from apps.llm_workers.gemini_client import GeminiClient
from apps.llm_workers.chunk_processor import ChunkProcessor
from apps.compiler.tex_builder import TexBuilder
from apps.compiler.docker_runner import DockerRunner

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

RATE_LIMIT_DELAY = 0.3  
CHECKPOINT_INTERVAL = 5
CHECKPOINT_FILE = "checkpoint.json"

def compute_ast_hash(ast: list[ASTNode]) -> str:
    # SOTA: Hash exclusivo de inputs inmutables para prevenir invalidación por mutación de estado
    raw = json.dumps([
        {"node_id": n.node_id, "type": n.type, "content": n.content}
        for n in ast
    ], sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def main():
    logger.info("1. Cargando AST...")
    ast = load_mock_ast()
    current_ast_hash = compute_ast_hash(ast)

    logger.info("2. Inicializando LLM...")
    client = GeminiClient()
    processor = ChunkProcessor(client)

    logger.info("3. Procesando nodos...")
    processed = []
    processed_ids = set()
    
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # SOTA: Validación de Deriva de AST
            if data.get("ast_hash") != current_ast_hash:
                logger.warning("Deriva de AST detectada. Hash no coincide. Ignorando checkpoint.")
            else:
                processed = [ASTNode(**n) for n in data.get("nodes", [])]
                processed_ids = {n.node_id for n in processed}
                logger.info(f"Retomando desde checkpoint. Nodos previamente procesados: {len(processed)}")
        except Exception as e:
            logger.warning(f"Fallo al leer checkpoint, iniciando desde cero: {e}")
            processed = []
            processed_ids = set()
    
    for index, node in enumerate(ast):
        if node.node_id in processed_ids:
            continue
            
        logger.info(f"Procesando nodo {node.node_id} ({node.type})")
        result_node = processor.process(node)
        processed.append(result_node)
        
        if (index + 1) % CHECKPOINT_INTERVAL == 0 or (index + 1) == len(ast):
            tmp_path = f"{CHECKPOINT_FILE}.tmp"
            payload = {
                "ast_hash": current_ast_hash,
                "nodes": [n.model_dump() for n in processed]
            }
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, CHECKPOINT_FILE)
            logger.info(f"Checkpoint atómico guardado ({len(processed)} nodos totales)")

        if node.type == "text_block":
            time.sleep(RATE_LIMIT_DELAY)

    # SOTA: Ordenamiento topológico estricto pre-ensamblaje
    ast_order_map = {n.node_id: idx for idx, n in enumerate(ast)}
    processed.sort(key=lambda x: ast_order_map.get(x.node_id, float('inf')))

    metrics = {"total": len(processed), "ok": 0, "fallback_empty": 0, "fallback_suspicious": 0, "error": 0}
    for n in processed:
        if n.status in metrics:
            metrics[n.status] += 1
            
    success_rate = (metrics['ok'] / metrics['total']) * 100 if metrics['total'] > 0 else 0
    
    logger.info("--- REPORTE DE MÉTRICAS ---")
    logger.info(f"Total Nodos: {metrics['total']}")
    logger.info(f"OK: {metrics['ok']} ({success_rate:.1f}%)")
    logger.info(f"Fallback (Vacío): {metrics['fallback_empty']}")
    logger.info(f"Fallback (Sospechoso): {metrics['fallback_suspicious']}")
    logger.info(f"Error (Fallo Terminal): {metrics['error']}")
    logger.info("---------------------------")

    logger.info("4. Ensamblando LaTeX...")
    builder = TexBuilder()
    tex = builder.build(processed)
    
    debug_tex_path = "debug.tex"
    with open(debug_tex_path, "w", encoding="utf-8") as f:
        f.write(tex)
    
    logger.info("5. Compilando mediante Docker...")
    runner = DockerRunner()
    pdf_path = runner.compile(tex, output_filename="MVP_traduccion.pdf")
    logger.info(f"✅ Pipeline exitoso. Artefacto generado en: {pdf_path}")

if __name__ == "__main__":
    main()