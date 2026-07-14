import json
import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import List, Tuple, Set, Optional

from core.ast.models import (
    ASTNode, TokenEstimator, TranslationUnit, 
    TranslationTaskType, OverflowPolicy, ChunkingReport
)
from core.ast.enums import ContentNodeType  # SOTA FIX: Importación desde el módulo de enums real
from core.ast.grouper import SemanticGroup, ContextAwareSemanticGrouper

logger = logging.getLogger(__name__)

def compute_ast_hash(ast: List[ASTNode]) -> str:
    """SOTA: Generación determinística de firma para el árbol sintáctico completo."""
    def serialize_node(n: ASTNode) -> dict:
        type_str = n.node_type.value if hasattr(n.node_type, "value") else str(n.node_type)
        return {
            "node_id": n.node_id,
            "type": type_str,
            # SOTA FIX: Uso de la fachada polimórfica inmutable para evitar colisiones con ImagePayload
            "content": n.text_content,
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

# --- FASE 13.00: SEMANTIC PACKAGING LAYER ---

@dataclass(frozen=True)
class ChunkPolicy:
    """SOTA: Configuración externa parametrizada con presupuestos duros."""
    max_tokens: int = 1500
    prompt_overhead_tokens: int = 100        
    overflow_policy: OverflowPolicy = OverflowPolicy.BY_SENTENCE
    structural_boundaries: Set[ContentNodeType] = field(default_factory=set)
    protected_content_types: Set[ContentNodeType] = field(default_factory=set)

class TokenBudgetChunker:
    """SOTA: Chunker de tiempo lineal O(N) que respeta fronteras de subgrafos semánticos."""
    
    def __init__(self, estimator: TokenEstimator, policy: Optional[ChunkPolicy] = None):
        self.estimator = estimator
        self.policy = policy if policy else ChunkPolicy()
        self.report = ChunkingReport()
        
        # SOTA FIX: Mapeo de fronteras jerárquicas al nuevo modelo de representación plana (Fase 16.6)
        self.boundaries = self.policy.structural_boundaries if self.policy.structural_boundaries else {
            ContentNodeType.HEADING
        }
        
        # SOTA FIX: Alineación con los tipos semánticos puros del AST V2
        self.protected_types = self.policy.protected_content_types if self.policy.protected_content_types else {
            ContentNodeType.DISPLAY_EQUATION, ContentNodeType.INLINE_EQUATION,
            ContentNodeType.CODE
        }
        
        self.partial_types = {ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX, ContentNodeType.IMAGE}

    def _split_by_sentence(self, text: str) -> List[str]:
        """Partición heurística ligera sin depender de NLP pesados (spaCy)."""
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_group(self, group: SemanticGroup, start_index: int) -> List[TranslationUnit]:
        units = []
        current_nodes: List[ASTNode] = []
        current_tokens = 0
        chunk_index = start_index
        available_payload_tokens = self.policy.max_tokens - self.policy.prompt_overhead_tokens

        def flush_translate_chunk():
            nonlocal chunk_index, current_nodes, current_tokens
            if not current_nodes:
                return
            
            payload_text = "\n\n".join([n.text_content or "" for n in current_nodes])
            first_seq = current_nodes[0].sequence_id
            last_seq = current_nodes[-1].sequence_id
            
            full_hash = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
            short_hash = full_hash[:8]
            det_chunk_id = f"chunk_{chunk_index:04d}_{first_seq}_{last_seq}_{short_hash}"
            fingerprint = hashlib.md5(f"{first_seq}-{last_seq}".encode()).hexdigest()
            
            units.append(TranslationUnit(
                chunk_index=chunk_index,
                chunk_id=det_chunk_id,
                chunk_fingerprint=fingerprint,
                chunk_type=TranslationTaskType.TRANSLATE,
                source_sequence_range=(first_seq, last_seq),
                node_count=len(current_nodes),
                context_id=group.context_id,
                context_depth=len(group.structural_path),
                target_payload=payload_text,
                estimated_tokens=current_tokens,
                payload_sha256=full_hash
            ))
            
            self.report.total_chunks += 1
            self.report.max_chunk_tokens = max(self.report.max_chunk_tokens, current_tokens)
            
            chunk_index += 1
            current_nodes = []
            current_tokens = 0

        for node in group.nodes:
            content = node.text_content or ""
            if not content:
                continue

            if node.node_type in self.protected_types or node.node_type in self.boundaries or node.node_type in self.partial_types:
                flush_translate_chunk()
                
                task_type = TranslationTaskType.PARTIAL if node.node_type in self.partial_types else TranslationTaskType.PRESERVE
                node_tokens = self.estimator.estimate(content)
                full_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                fingerprint = hashlib.md5(f"{node.sequence_id}-{node.sequence_id}".encode()).hexdigest()
                
                units.append(TranslationUnit(
                    chunk_index=chunk_index,
                    chunk_id=f"isolated_{chunk_index:04d}_{node.sequence_id}_{full_hash[:8]}",
                    chunk_fingerprint=fingerprint,
                    chunk_type=task_type,
                    source_sequence_range=(node.sequence_id, node.sequence_id),
                    node_count=1,
                    context_id=group.context_id,
                    context_depth=len(group.structural_path),
                    target_payload=content,
                    estimated_tokens=node_tokens,
                    payload_sha256=full_hash
                ))
                
                self.report.total_chunks += 1
                self.report.max_chunk_tokens = max(self.report.max_chunk_tokens, node_tokens)
                chunk_index += 1
                continue

            node_tokens = self.estimator.estimate(content)
            
            # --- OVERFLOW POLICY ---
            if node_tokens > available_payload_tokens:
                self.report.overflow_events += 1
                flush_translate_chunk()
                
                if self.policy.overflow_policy == OverflowPolicy.BY_SENTENCE:
                    sentences = self._split_by_sentence(content)
                    for sentence in sentences:
                        s_tokens = self.estimator.estimate(sentence)
                        if current_tokens + s_tokens > available_payload_tokens and current_nodes:
                            flush_translate_chunk()
                        
                        # SOTA FIX: Mapeo explícito y tipado de payloads para satisfacer a Pyright Strict Mode
                        from core.ast.models import (
                            HeadingPayload, ParagraphPayload, MathPayload, 
                            CodePayload, TablePayload, ListPayload, ASTPayload
                        )
                        
                        if node.node_type == ContentNodeType.HEADING:
                            new_payload: ASTPayload = HeadingPayload(content=sentence)
                        elif node.node_type in (ContentNodeType.PARAGRAPH, ContentNodeType.CAPTION):
                            new_payload = ParagraphPayload(content=sentence)
                        elif node.node_type in (ContentNodeType.DISPLAY_EQUATION, ContentNodeType.INLINE_EQUATION):
                            new_payload = MathPayload(content=sentence)
                        elif node.node_type == ContentNodeType.CODE:
                            new_payload = CodePayload(content=sentence)
                        elif node.node_type in (ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX):
                            new_payload = TablePayload(content=sentence)
                        elif node.node_type == ContentNodeType.LIST:
                            new_payload = ListPayload(content=sentence)
                        else:
                            new_payload = ParagraphPayload(content=sentence)

                        sub_node = ASTNode(
                            node_id=f"{node.node_id}_sub_{len(current_nodes)}",
                            sequence_id=node.sequence_id,
                            node_type=node.node_type,
                            payload=new_payload,
                            metadata=node.metadata,
                            control_plane=node.control_plane
                        )
                        current_nodes.append(sub_node)
                        current_tokens += s_tokens
                else:
                    current_nodes.append(node)
                    current_tokens += node_tokens
                    flush_translate_chunk()
                continue

            if current_tokens + node_tokens > available_payload_tokens and current_nodes:
                flush_translate_chunk()

            current_nodes.append(node)
            current_tokens += node_tokens

        flush_translate_chunk()
        return units

def build_semantic_chunks_as_units(ast: List[ASTNode], estimator: TokenEstimator) -> Tuple[List[TranslationUnit], ChunkingReport]:
    """Punto de entrada SOTA para la generación de unidades empaquetadas de la Fase 13.00."""
    semantic_groups = ContextAwareSemanticGrouper.group(ast)
    chunker = TokenBudgetChunker(estimator, ChunkPolicy())
    chunker.report.total_groups = len(semantic_groups)
    
    all_units = []
    current_index = 1
    
    for group in semantic_groups:
        group_units = chunker.chunk_group(group, start_index=current_index)
        all_units.extend(group_units)
        current_index += len(group_units)
        chunker.report.context_switches += 1
        
    if all_units:
        chunker.report.average_chunk_tokens = int(sum(u.estimated_tokens for u in all_units) / len(all_units))
        
    return all_units, chunker.report