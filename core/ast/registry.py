import os
import json
import logging
from typing import Optional, Dict, Tuple, List

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

        # CORRECCION PUNTO 7 (Mejora Production-Grade): Mitigación de alertas ruidosas en logs
        if not os.path.exists(ast_path):
            logger.warning(f"Archivo de persistencia AST no encontrado para el documento {document_id} en ninguna ruta.")
            return

        try:
            with open(ast_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                
            # Soporte polimórfico para esquemas de lista plana o sobres estructurados
            if isinstance(raw_data, list):
                nodes_list = raw_data
            elif isinstance(raw_data, dict) and "nodes" in raw_data:
                nodes_list = raw_data.get("nodes", [])
            else:
                raise ValueError("Estructura de persistencia AST no reconocible o corrupta.")
                
            node_map = {}
            for node_dict in nodes_list:
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

    # En core/ast/registry.py, agregar método:
    def get_document_ast(self, document_id: str, ast_hash: str) -> List[ASTNode]:
        """
        Retorna todos los nodos del documento ordenados por sequence_id.

        NADR-06 §5.3: Contrato público para CQRSAssemblyContextResolver.
        """
        cache_key = (document_id, ast_hash)
        if cache_key not in self._cache:
            self._load_document(document_id, ast_hash)
        doc_cache = self._cache.get(cache_key, {})
        nodes = list(doc_cache.values())
        return sorted(nodes, key=lambda n: n.sequence_id)
    def get_verified_document_ast(self, document_id: str, ast_hash: str) -> List[ASTNode]:
        """Verify persisted product AST bytes and V2 semantic identity on every read.

        Not an oracle identity or replay authorization. Unlike the legacy
        get_document_ast(), this never accepts an unverifiable generation, an
        mismatched envelope, missing file, duplicate nodes, or stale hot cache.
        The product consumer must call this before binding a ChunkPlan to AST.
        """
        from core.ast.hashing import compute_ast_hash

        if not isinstance(document_id, str) or not document_id:
            raise ValueError("PPPR_G2_AST_DOCUMENT_ID_INVALID")
        if not isinstance(ast_hash, str) or len(ast_hash) != 64 or any(
            char not in "0123456789abcdef" for char in ast_hash
        ):
            raise ValueError("PPPR_G2_AST_GENERATION_ID_INVALID")
        path = os.path.join(self.ast_dir, f"{document_id}.{ast_hash}.ast.json")
        try:
            with open(path, "r", encoding="utf-8") as stream:
                payload = json.load(stream)
        except (OSError, ValueError) as exc:
            raise ValueError("PPPR_G2_AST_ARTIFACT_UNAVAILABLE") from exc
        if (
            not isinstance(payload, dict)
            or set(payload) != {"document_id", "ast_hash", "nodes"}
            or payload["document_id"] != document_id
            or payload["ast_hash"] != ast_hash
            or not isinstance(payload["nodes"], list)
            or not payload["nodes"]
        ):
            raise ValueError("PPPR_G2_AST_PERSISTED_ENVELOPE_MISMATCH")
        try:
            nodes = [ASTNode.model_validate(item) for item in payload["nodes"]]
        except Exception as exc:
            raise ValueError("PPPR_G2_AST_PERSISTED_NODE_INVALID") from exc
        if (
            len({node.node_id for node in nodes}) != len(nodes)
            or [node.sequence_id for node in nodes] != list(range(1, len(nodes) + 1))
        ):
            raise ValueError("PPPR_G2_AST_ORDER_OR_NODE_ID_DRIFT")
        if compute_ast_hash(nodes) != ast_hash:
            raise ValueError("PPPR_G2_AST_SEMANTIC_GENERATION_DRIFT")
        # Hydrate RAM only after successful verification; do not trust an
        # earlier cached copy when the persisted artifact may have changed.
        self._cache[(document_id, ast_hash)] = {node.node_id: node for node in nodes}
        return nodes
