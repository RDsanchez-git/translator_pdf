import os
import json
import logging
from hashlib import sha256
from typing import Optional, Dict, Tuple, List, Sequence

from core.ast.models import ASTNode 

logger = logging.getLogger(__name__)

def _artifact_sha256(document_id: str, ast_hash: str, nodes: Sequence[object]) -> str:
    """Independent durable artifact digest, including IDs, strategy and geometry.

    Distinct from AST semantic identity and from EN→ES generation identity.
    Detects accidental persisted changes; not a digital signature against an
    attacker capable of rewriting both data and its digest.
    """
    canonical = json.dumps(
        {"contract": "PPPR_G2_AST_ARTIFACT_V1",
         "document_id": document_id, "ast_hash": ast_hash, "nodes": nodes},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


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
        """Publish a complete durable AST once; never replace the same key.

        The semantic hash intentionally excludes operational/physical fields.
        Therefore two semantically equal ASTs can be distinct durable artifacts.
        Link a fully written temporary file with O_EXCL-like, atomic no-clobber
        semantics; concurrent publishers cannot overwrite the winning file.
        Identical retries are allowed only when the existing envelope matches.
        The hot cache is changed exclusively after successful publication/retry.
        """
        import tempfile
        from core.ast.hashing import compute_ast_hash

        if compute_ast_hash(ast_nodes) != ast_hash:
            raise ValueError("PPPR_G2_AST_REGISTRATION_SEMANTIC_DRIFT")
        cache_key = (document_id, ast_hash)
        final_path = os.path.join(self.ast_dir, f"{document_id}.{ast_hash}.ast.json")
        nodes_data = [node.model_dump(mode="json") for node in ast_nodes]
        payload = {
            "document_id": document_id,
            "ast_hash": ast_hash,
            "nodes": nodes_data,
            "artifact_sha256": _artifact_sha256(document_id, ast_hash, nodes_data),
        }

        fd, temp_path = tempfile.mkstemp(dir=self.ast_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                # Atomic hard-link creation succeeds for exactly one concurrent
                # writer. os.replace would silently destroy earlier bindings.
                os.link(temp_path, final_path)
            except FileExistsError:
                if os.path.islink(final_path):
                    raise ValueError("PPPR_G2_AST_ARTIFACT_CONFLICT")
                try:
                    with open(final_path, "r", encoding="utf-8") as stream:
                        existing = json.load(stream)
                except (OSError, ValueError) as exc:
                    raise ValueError("PPPR_G2_AST_EXISTING_ARTIFACT_INVALID") from exc
                if existing != payload:
                    raise ValueError("PPPR_G2_AST_ARTIFACT_CONFLICT")
                # Identical durable artifact: idempotent retry.
            self._cache[cache_key] = {node.node_id: node for node in ast_nodes}
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        logger.info("AST persistido o confirmado idempotente: %s", document_id[:12])

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
            or set(payload) != {"document_id", "ast_hash", "nodes", "artifact_sha256"}
            or payload["document_id"] != document_id
            or payload["ast_hash"] != ast_hash
            or not isinstance(payload["nodes"], list)
            or not payload["nodes"]
        ):
            raise ValueError("PPPR_G2_AST_PERSISTED_ENVELOPE_MISMATCH")
        # ASTNode's discriminator model_validator transforms the input dict.
        # Fingerprint ORIGINAL JSON before validation, never the mutated alias.
        observed_artifact_sha256 = _artifact_sha256(
            document_id, ast_hash, payload["nodes"]
        )
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
        if payload["artifact_sha256"] != observed_artifact_sha256:
            raise ValueError("PPPR_G2_AST_ARTIFACT_INTEGRITY_DRIFT")
        # Hydrate RAM only after successful verification; do not trust an
        # earlier cached copy when the persisted artifact may have changed.
        self._cache[(document_id, ast_hash)] = {node.node_id: node for node in nodes}
        return nodes
