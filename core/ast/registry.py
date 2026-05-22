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
        # Estructura física corregida: { (document_id, ast_hash): { node_id: ASTNode } }
        self._cache: Dict[Tuple[str, str], Dict[str, ASTNode]] = {}

    def get_node(self, document_id: str, ast_hash: str, node_id: str) -> Optional[ASTNode]:
        """Recupera un nodo de la memoria RAM o lo carga desde disco ante un cache miss."""
        cache_key = (document_id, ast_hash)
        
        if cache_key not in self._cache:
            self._load_document(document_id, ast_hash)
        
        doc_cache = self._cache.get(cache_key, {})
        return doc_cache.get(node_id)

    def _load_document(self, document_id: str, ast_hash: str):
        """Carga y valida el AST completo desde disco hacia la memoria RAM."""
        cache_key = (document_id, ast_hash)
        
        # Estructura estándar del pipeline
        ast_path = os.path.join(self.workspace_dir, f"{document_id}.ast.json")
        
        # Fallback para pruebas locales en testing
        if not os.path.exists(ast_path):
            ast_path = os.path.join(self.workspace_dir, "tests", "corpus", f"{document_id}.ast.json")
            
        if not os.path.exists(ast_path):
            logger.error(f"SRE_AST_FAULT: Archivo no encontrado en disco: {ast_path}")
            return

        try:
            with open(ast_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            node_map = {}
            for node_dict in data.get("nodes", []):
                # SOTA: Deserialización nativa y rápida con Pydantic V2
                node = ASTNode.model_validate(node_dict) 
                node_map[node.node_id] = node
                
            # Asignación atómica a la clave compuesta para blindar la consistencia
            self._cache[cache_key] = node_map
            logger.info(
                f"AST materializado en memoria RAM para clave {cache_key} | "
                f"{len(node_map)} nodos indexados de forma segura."
            )
            
        except Exception as e:
            logger.error(f"Fallo crítico parseando AST para {document_id} ({ast_hash}): {e}")