import os
import json
import logging
from typing import Optional, Dict, Tuple

from core.ast.models import ASTNode 

logger = logging.getLogger(__name__)

class ASTRegistry:
    """
    SOTA: Registro de AST en memoria con Lazy Loading e inmunidad a mutaciones de contenido.
    Utiliza claves compuestas (document_id, ast_hash) para evitar servir datos obsoletos.
    """
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = workspace_dir
        # Estructura en RAM local O(1)
        self._cache: Dict[Tuple[str, str], Dict[str, ASTNode]] = {}
        # Centralización de la ruta física del AST
        self.ast_dir = os.path.join(self.workspace_dir, "data", "ast_cache")
        os.makedirs(self.ast_dir, exist_ok=True)

    def get_node(self, document_id: str, ast_hash: str, node_id: str) -> Optional[ASTNode]:
        """Recupera un nodo de la memoria RAM o lo carga desde disco ante un cache miss."""
        cache_key = (document_id, ast_hash)
        
        if cache_key not in self._cache:
            self._load_document(document_id, ast_hash)
        
        doc_cache = self._cache.get(cache_key, {})
        return doc_cache.get(node_id)

    def _load_document(self, document_id: str, ast_hash: str):
        cache_key = (document_id, ast_hash)
        ast_path = os.path.join(self.ast_dir, f"{document_id}.{ast_hash}.ast.json")
        
        if not os.path.exists(ast_path):
            ast_path = os.path.join(self.workspace_dir, "tests", "corpus", f"{document_id}.{ast_hash}.ast.json")

        try:
            with open(ast_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            node_map = {}
            for node_dict in data.get("nodes", []):
                node = ASTNode.model_validate(node_dict) 
                node_map[node.node_id] = node
                
            self._cache[cache_key] = node_map
            logger.info(f"AST hidratado en RAM desde almacenamiento persistente: {document_id[:12]}")
            
        except Exception as e:
            logger.error(f"Fallo crítico parseando AST para {document_id}: {e}")

    def register_ast(self, document_id: str, ast_hash: str, ast_nodes: list[ASTNode]) -> None:
        """
        SOTA Pragmática: Persistencia atómica del AST (Inmune a cortes/OOM)
        e hidratación inmediata de la caché RAM local.
        """
        import tempfile
        cache_key = (document_id, ast_hash)
        
        # 1. Sincronización en caché RAM local
        self._cache[cache_key] = {n.node_id: n for n in ast_nodes}
        
        # 2. Preparación del payload respetando tu raíz "nodes"
        final_path = os.path.join(self.ast_dir, f"{document_id}.{ast_hash}.ast.json")
        payload = {
            "document_id": document_id,
            "ast_hash": ast_hash,
            "nodes": [n.model_dump() for n in ast_nodes]
        }
        
        # 3. Escritura Atómica en el mismo sistema de archivos (POSIX/Windows Safe)
        fd, temp_path = tempfile.mkstemp(dir=self.ast_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            # Reemplazo a nivel de Kernel (Atomic Swap)
            os.replace(temp_path, final_path)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Fallo persistiendo AST atómico para {document_id}: {e}")
            raise e
            
        logger.info(f"AST persistido atómicamente en disco: {document_id[:12]}.ast.json")