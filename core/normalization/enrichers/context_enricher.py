import hashlib
from typing import List, Dict, Tuple, Any
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType, HeadingLevel
from core.normalization.base import WarningEntry

class HierarchicalContextEnricher:
    """
    SOTA: Enriquecedor jerárquico de contextos efímeros en tiempo de ejecución.
    Implementa BLAKE2b e indexación estructural lógica inmune a mutaciones del parser.
    """
    def __init__(self, max_depth: int = 4):
        self._version = "12.00.8"
        self._max_depth = max_depth
        self._root_context = {"level": 0, "title": "[ROOT_DOCUMENT_CONTEXT]"}

    def _validate_registry(self, nodes: List[ASTNode], mappings: Dict[str, Any]) -> None:
        """Garantiza la consistencia interna y previene punteros huérfanos antes del Chunking."""
        for node in nodes:
            if node.node_type != ContentNodeType.HEADING:
                ctx_id = node.control_plane.get("context_id")
                if ctx_id and ctx_id not in mappings:
                    raise ValueError(f"CONTEXT_REGISTRY_CORRUPTION: Node {node.node_id} points to missing context {ctx_id}")

    def enrich_document(self, nodes: List[ASTNode]) -> Tuple[List[ASTNode], Dict[str, Any], List[WarningEntry], Dict[str, int]]:
        enriched_nodes: List[ASTNode] = []
        context_mappings: Dict[str, List[Dict[str, Any]]] = {}
        warnings: List[WarningEntry] = []
        
        hierarchy_stack: List[Dict[str, Any]] = []
        last_level = 0
        structural_index = 0
        
        context_switches = 0
        last_context_id = None

        for node in nodes:
            if node.node_type == ContentNodeType.HEADING:
                h_level_attr = getattr(node.payload, "heading_level", HeadingLevel.UNKNOWN)
                if h_level_attr == HeadingLevel.H1:
                    level = 1
                elif h_level_attr == HeadingLevel.H2:
                    level = 2
                elif h_level_attr == HeadingLevel.H3:
                    level = 3
                else:
                    level = 1

                title = (node.text_content or "Untitled").lstrip("#").strip()
                structural_index += 1

                if last_level > 0 and (level - last_level) > 1:
                    warnings.append(WarningEntry(
                        severity="WARNING",
                        message=f"HEADING_LEVEL_JUMP: Abrupt shift from H{last_level} to H{level} at structural index {structural_index}."
                    ))
                
                last_level = level
                hierarchy_stack = [h for h in hierarchy_stack if h["level"] < level]
                
                hierarchy_stack.append({
                    "level": level, 
                    "title": title, 
                    "index": structural_index
                })
                
                enriched_nodes.append(node)
                continue

            if hierarchy_stack:
                effective_stack = hierarchy_stack[-self._max_depth:]
                breadcrumbs = [{"level": h["level"], "title": h["title"]} for h in effective_stack]
                fingerprint_elements = [f"H{h['level']}_I{h['index']}:{h['title']}" for h in effective_stack]
                stack_fingerprint = ",".join(fingerprint_elements).encode("utf-8")
            else:
                breadcrumbs = [self._root_context]
                stack_fingerprint = b"ROOT"

            context_hash = hashlib.blake2b(stack_fingerprint, digest_size=6).hexdigest().upper()
            context_id = f"CTX_{context_hash}"

            if context_id not in context_mappings:
                context_mappings[context_id] = breadcrumbs

            if last_context_id is not None and context_id != last_context_id:
                context_switches += 1
            last_context_id = context_id

            new_cp = dict(node.control_plane)
            new_cp["context_id"] = context_id
            new_cp["context_depth"] = len(breadcrumbs)

            node = node.model_copy(update={
                "control_plane": new_cp
            })
            enriched_nodes.append(node)

        if structural_index == 0 and nodes:
            warnings.append(WarningEntry(
                severity="INFO",
                message="NO_CONTEXT_DOCUMENT: The document contains content but zero valid structural headings."
            ))

        structured_registry = {
            "schema_version": "1.0.1",
            "algorithm": "blake2b_ephemeral_runtime_v1",
            "mappings": context_mappings
        }

        self._validate_registry(enriched_nodes, context_mappings)
        metrics = {"context_switches": context_switches}

        return enriched_nodes, structured_registry, warnings, metrics