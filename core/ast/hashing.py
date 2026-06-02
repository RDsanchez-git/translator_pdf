import json
import hashlib
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple
from core.ast.models import ASTNode, ContentNodeType, StructuralNodeType, TokenEstimator, TranslationUnit

logger = logging.getLogger(__name__)

def compute_ast_hash(ast: List[ASTNode]) -> str:
    """SOTA: Generación determinística de firma para el árbol sintáctico completo."""
    def serialize_node(n: ASTNode) -> dict:
        type_str = n.type.value if hasattr(n.type, "value") else str(n.type)
        return {
            "node_id": n.node_id,
            "type": type_str,
            "content": n.content,
            "latex": getattr(n, "latex", None),
            "children": [serialize_node(c) for c in getattr(n, "children", [])] if getattr(n, "children", None) else []
        }
        
    raw = json.dumps(
        [serialize_node(n) for n in ast], 
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# --- FASE 10B: SEMANTIC PACKAGING LAYER ---

@dataclass(frozen=True)
class ChunkPolicy:
    """SOTA: Configuración externa parametrizada con inicialización segura de fábricas mutables."""
    max_tokens: int = 1500
    sliding_window_tokens: int = 150
    prompt_overhead_tokens: int = 100        
    structural_boundaries: set = field(default_factory=set)
    protected_content_types: set = field(default_factory=set)

class SemanticChunker:
    """Motor perimetral de segmentación determinista con Sliding Window inclusivo y acotado."""
    def __init__(self, estimator: TokenEstimator, policy: ChunkPolicy | None = None):
        self.estimator = estimator
        self.policy = policy if policy else ChunkPolicy()
        
        if self.policy.sliding_window_tokens + self.policy.prompt_overhead_tokens >= self.policy.max_tokens:
            raise ValueError(
                "Sliding window tokens + prompt overhead tokens must be strictly smaller than max_tokens"
            )
        
        self.boundaries = self.policy.structural_boundaries if self.policy.structural_boundaries else {
            StructuralNodeType.DOCUMENT,
            StructuralNodeType.PART,
            StructuralNodeType.CHAPTER,
            StructuralNodeType.SECTION,
            StructuralNodeType.SUBSECTION
        }
        self.protected_types = self.policy.protected_content_types if self.policy.protected_content_types else {
            ContentNodeType.EQUATION,
            ContentNodeType.INLINE_EQUATION,
            ContentNodeType.TABLE,
            ContentNodeType.CODE_BLOCK,
            ContentNodeType.ALGORITHM,
            ContentNodeType.FIGURE,
            ContentNodeType.IMAGE,
            ContentNodeType.COMPOSITE_BLOCK,
            ContentNodeType.UNKNOWN,
            ContentNodeType.CITATION,
            ContentNodeType.REFERENCE_ENTRY,
            ContentNodeType.BIBLIOGRAPHY
        }
        
        self._context_buffer = deque()
        self._buffer_tokens = 0

    def _add_to_buffer(self, content: str, tokens: int):
        self._context_buffer.append((content, tokens))
        self._buffer_tokens += tokens
        while self._buffer_tokens > (self.policy.sliding_window_tokens * 2) and self._context_buffer:
            _, t = self._context_buffer.popleft()
            self._buffer_tokens -= t

    def _build_reference_context(self) -> Tuple[str, int]:
        context_nodes = []
        accumulated_tokens = 0
        for content, token_count in reversed(self._context_buffer):
            if accumulated_tokens + token_count > self.policy.sliding_window_tokens:
                break
            context_nodes.insert(0, content)
            accumulated_tokens += token_count
        return "\n\n".join(context_nodes) if context_nodes else "", accumulated_tokens

    def chunk_document(self, ast: List[ASTNode]) -> List[TranslationUnit]:
        # SOTA: Garantizar pureza funcional e idempotencia limpiando el estado de la instancia
        self._context_buffer.clear()
        self._buffer_tokens = 0

        units = []
        current_nodes = []
        current_tokens = 0
        chunk_index = 1

        context_text, current_context_tokens = self._build_reference_context()
        available_payload_tokens = (
            self.policy.max_tokens 
            - current_context_tokens 
            - self.policy.prompt_overhead_tokens
        )

        def flush_translate_chunk():
            nonlocal chunk_index, current_nodes, current_tokens, context_text, current_context_tokens, available_payload_tokens
            if current_nodes:
                payload_text = "\n\n".join([n.content or "" for n in current_nodes])
                first_seq = current_nodes[0].sequence_id
                last_seq = current_nodes[-1].sequence_id
                
                full_hash = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
                short_hash = full_hash[:8]
                det_chunk_id = f"chunk_{chunk_index:04d}_{first_seq}_{last_seq}_{short_hash}"
                
                units.append(TranslationUnit(
                    chunk_index=chunk_index,
                    chunk_id=det_chunk_id,
                    chunk_type="translate",
                    source_sequence_range=(first_seq, last_seq),
                    node_count=len(current_nodes),
                    reference_context=context_text,
                    target_payload=payload_text,
                    estimated_tokens=current_tokens,
                    payload_sha256=full_hash
                ))
                chunk_index += 1
                
                for n in current_nodes:
                    if n.content:
                        n_tokens = self.estimator.estimate(n.content)
                        self._add_to_buffer(n.content, n_tokens)
                        
                current_nodes = []
                current_tokens = 0
                
                context_text, current_context_tokens = self._build_reference_context()
                available_payload_tokens = (
                    self.policy.max_tokens 
                    - current_context_tokens 
                    - self.policy.prompt_overhead_tokens
                )

        for node in ast:
            content = node.content or ""

            if node.type in self.boundaries:
                flush_translate_chunk()
                full_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                units.append(TranslationUnit(
                    chunk_index=chunk_index,
                    chunk_id=f"boundary_{chunk_index:04d}_{node.sequence_id}_{full_hash[:8]}",
                    chunk_type="passthrough",
                    source_sequence_range=(node.sequence_id, node.sequence_id),
                    node_count=1,
                    reference_context="",
                    target_payload=content,
                    estimated_tokens=self.estimator.estimate(content),
                    payload_sha256=full_hash
                ))
                chunk_index += 1
                
                context_text, current_context_tokens = self._build_reference_context()
                available_payload_tokens = (
                    self.policy.max_tokens 
                    - current_context_tokens 
                    - self.policy.prompt_overhead_tokens
                )
                continue

            if node.type in self.protected_types:
                flush_translate_chunk()
                full_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                units.append(TranslationUnit(
                    chunk_index=chunk_index,
                    chunk_id=f"passthrough_{chunk_index:04d}_{node.sequence_id}_{full_hash[:8]}",
                    chunk_type="passthrough",
                    source_sequence_range=(node.sequence_id, node.sequence_id),
                    node_count=1,
                    reference_context="",
                    target_payload=content,
                    estimated_tokens=self.estimator.estimate(content),
                    payload_sha256=full_hash
                ))
                chunk_index += 1
                
                context_text, current_context_tokens = self._build_reference_context()
                available_payload_tokens = (
                    self.policy.max_tokens 
                    - current_context_tokens 
                    - self.policy.prompt_overhead_tokens
                )
                continue

            if not content:
                continue

            node_tokens = self.estimator.estimate(content)
            
            if current_tokens + node_tokens > available_payload_tokens and current_nodes:
                flush_translate_chunk()

            current_nodes.append(node)
            current_tokens += node_tokens

        flush_translate_chunk()
        return units

def build_semantic_chunks_as_units(ast: List[ASTNode], estimator: TokenEstimator) -> List[TranslationUnit]:
    """Punto de entrada SOTA para la generación de unidades empaquetadas de la Fase 10B."""
    chunker = SemanticChunker(estimator, ChunkPolicy())
    return chunker.chunk_document(ast)