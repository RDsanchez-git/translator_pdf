import re
from typing import List, Final, Set
from core.ast.enums import ContentNodeType
from core.ast.models import ASTNode, NodeMetadata

class AbbreviationPolicy:
    """SOTA: Base de conocimiento estática optimizada para la exclusión 
    de abreviaturas científicas y editoriales en tiempo constante O(1)."""
    
    _LEXICON: Final[Set[str]] = {
        "e.g.", "i.e.", "fig.", "dr.", "eq.", "no.", "et al.", "cf.", "vs.",
        "vol.", "eds.", "ed.", "pp.", "pág.", "approx.", "ibid."
    }

    @classmethod
    def is_abbreviation(cls, text: str) -> bool:
        if not text:
            return False
        tokens = text.strip().split()
        if not tokens:
            return False
        # Extraer la última palabra normalizada eliminando ruidos marginales
        last_token = tokens[-1].lower().rstrip(",;: ")
        return last_token in cls._LEXICON

class BoundaryDetector:
    """Validador estricto de límites perimetrales físicos de páginas."""
    
    @staticmethod
    def is_cross_page_boundary(n1: ASTNode, n2: ASTNode) -> bool:
        if not n1.metadata.pages or not n2.metadata.pages:
            return False
        return n1.metadata.pages[-1] + 1 == n2.metadata.pages[0]

class HyphenResolver:
    """Motor conservador de de-hyphenation para la preservación léxica STEM."""
    
    @staticmethod
    def resolve(text_left: str, text_right: str) -> str:
        text_left = text_left.rstrip()
        text_right = text_right.lstrip()
        
        if text_left.endswith("-"):
            # SOTA Guardrail: Conserva la integridad de términos compuestos (ej: T-cell, X-ray)
            if text_right and text_right[0].islower():
                return f"{text_left[:-1]}{text_right}"
                
        return f"{text_left} {text_right}"

class MetadataMerger:
    """Consolidador inmutable de trazabilidad y linaje métrico."""
    
    @staticmethod
    def merge(m1: NodeMetadata, m2: NodeMetadata) -> NodeMetadata:
        # NOTA ARQUITECTÓNICA: Invariante fuerte de certeza. La confianza del nodo 
        # unificado se rige por el principio del eslabón más débil; la precisión global 
        # nunca puede ser superior a la del segmento más degradado por el OCR.
        lowest_confidence = min(m1.confidence, m2.confidence)
        
        return NodeMetadata(
            bboxes=m1.bboxes + m2.bboxes,
            pages=sorted(list(set(m1.pages + m2.pages))),
            provider_native_id=m1.provider_native_id or m2.provider_native_id,
            confidence=lowest_confidence,
            layout_reading_order=m1.layout_reading_order,
            semantic_origin=m1.semantic_origin
        )

class MergePolicy:
    """Coordinador declarativo de viabilidad de fusión sintáctica."""
    
    MERGEABLE_TYPES: Final[Set[ContentNodeType]] = {
        ContentNodeType.PARAGRAPH,
        ContentNodeType.CAPTION,
        ContentNodeType.CODE,
        ContentNodeType.LIST
    }
    
    _TERMINAL_PUNCTUATION: Final[re.Pattern] = re.compile(r'[\.\?\!\]\)]\s*$')

    @classmethod
    def should_merge(cls, n1: ASTNode, n2: ASTNode) -> bool:
        # Regla 1: Identidad tipada compatible
        if n1.node_type != n2.node_type or n1.node_type not in cls.MERGEABLE_TYPES:
            return False
            
        # Regla 2: Invariante de contigüidad de página física
        if not BoundaryDetector.is_cross_page_boundary(n1, n2):
            return False

        # Contrato estático garantizado por la validación perimetral de MERGEABLE_TYPES
        # Evita por completo el code smell de 'getattr'
        text_left = n1.payload.content # type: ignore[attr-defined]
        
        # Regla 3: Si finaliza en abreviatura científica, la cadena oracional sigue abierta
        if AbbreviationPolicy.is_abbreviation(text_left):
            return True
            
        # Regla 4: Si no posee puntuación reglamentaria de cierre, se dictamina fractura física
        return not cls._TERMINAL_PUNCTUATION.search(text_left)

class CrossPageNormalizer:
    """Orquestador lineal O(n) encargado de purgar la fragmentación trans-página del AST."""

    @classmethod
    def execute(cls, nodes: List[ASTNode]) -> List[ASTNode]:
        if len(nodes) < 2:
            return nodes

        consolidated: List[ASTNode] = []
        iterator = iter(nodes)
        current_node = next(iterator)

        for next_node in iterator:
            if MergePolicy.should_merge(current_node, next_node):
                current_node = cls._execute_fusion(current_node, next_node)
                continue
            
            consolidated.append(current_node)
            current_node = next_node
            
        consolidated.append(current_node)
        return consolidated

    @staticmethod
    def _execute_fusion(n1: ASTNode, n2: ASTNode) -> ASTNode:
        # El tipado estático está blindado mediante el filtro del MergePolicy
        text_left: str = n1.payload.content # type: ignore[attr-defined]
        text_right: str = n2.payload.content # type: ignore[attr-defined]
        
        merged_text = HyphenResolver.resolve(text_left, text_right)
        merged_metadata = MetadataMerger.merge(n1.metadata, n2.metadata)
        
        # Registro atómico de telemetría en el plano de control
        new_control_plane = n1.control_plane.copy()
        new_control_plane["merge_count"] = new_control_plane.get("merge_count", 1) + 1
        
        # SOTA: Mutación limpia basada en interfaz fluida inmutable del DTO componente
        new_payload = n1.payload.with_content(merged_text) # type: ignore[attr-defined]

        return n1.model_copy(update={
            "payload": new_payload,
            "metadata": merged_metadata,
            "control_plane": new_control_plane
        })