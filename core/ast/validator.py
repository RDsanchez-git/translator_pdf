import re
import logging
from typing import Dict
from core.ast.models import ASTNode
from core.ast.enums import ContentNodeType  # SOTA FIX: Importación unificada desde enums

logger = logging.getLogger(__name__)

LATEX_MATH_OPEN = re.compile(
    r'(\$\$|\\\[|\\begin\{(equation|align|aligned|gather|math|cases|matrix|tabular|array)\*?\})', 
    re.IGNORECASE
)
LATEX_MATH_CLOSE = re.compile(
    r'(\$\$|\\\]|\\end\{(equation|align|aligned|gather|math|cases|matrix|tabular|array)\*?\})', 
    re.IGNORECASE
)

class ASTValidationError(Exception):
    pass

class ASTHealthReport:
    """
    SOTA OBSERVABILITY: Monitorea densidad de caracteres, cobertura semántica pura y cobertura estructural de layout.
    """
    def __init__(self, stats: Dict[str, int], semantic_coverage: float, structural_coverage: float, total_nodes: int, payload_size: int) -> None:
        self.stats = stats
        self.semantic_coverage = semantic_coverage
        self.structural_coverage = structural_coverage
        self.total_nodes = total_nodes
        self.payload_size = payload_size

    @classmethod
    def from_ast(cls, ast: list[ASTNode]) -> "ASTHealthReport":
        stats = {
            "headings": 0, "paragraphs": 0, "equations": 0, "inline_equations": 0,
            "tables": 0, "images": 0, "captions": 0, "lists": 0, "sections": 0, 
            "unknown": 0, "composite": 0, "others": 0
        }
        
        payload_size = 0
        total_nodes = len(ast)
        
        for node in ast:
            t = node.node_type
            # SOTA FIX: Uso de la fachada de extracción polimórfica inmutable
            content_str = node.text_content or ""
            
            if content_str and t != ContentNodeType.IMAGE:
                payload_size += len(content_str)

            if t == ContentNodeType.HEADING:
                stats["headings"] += 1
            elif t == ContentNodeType.PARAGRAPH:
                stats["paragraphs"] += 1
            elif t == ContentNodeType.DISPLAY_EQUATION:  # SOTA FIX: Especialización de enums V2
                stats["equations"] += 1
            elif t == ContentNodeType.INLINE_EQUATION:
                stats["inline_equations"] += 1
            elif t in (ContentNodeType.TABLE_SIMPLE, ContentNodeType.TABLE_COMPLEX):  # SOTA FIX: Unión de tipos de tablas
                stats["tables"] += 1
            elif t == ContentNodeType.IMAGE:
                stats["images"] += 1
            elif t == ContentNodeType.CAPTION:
                stats["captions"] += 1
            elif t == ContentNodeType.LIST:
                stats["lists"] += 1
            elif t == ContentNodeType.COMPOSITE_BLOCK:
                stats["composite"] += 1
            else:
                stats["others"] += 1

        recognized_semantic = (stats["headings"] + stats["paragraphs"] + stats["equations"] + 
                               stats["inline_equations"] + stats["tables"] + stats["images"] + 
                               stats["captions"] + stats["lists"])
        
        total_content_nodes = recognized_semantic + stats["unknown"] + stats["composite"]
        semantic_coverage = (recognized_semantic / total_content_nodes) if total_content_nodes > 0 else 0.0
        
        # SOTA FIX: Se mantiene en 0.0 para retrocompatibilidad con dashboards FinOps/SRE
        structural_coverage = 0.0
        
        return cls(stats, semantic_coverage, structural_coverage, total_nodes, payload_size)

    def __str__(self) -> str:
        return (
            "\n" + "="*40 + "\n"
            "         AST HEALTH REPORT\n" +
            "="*40 + f"\n"
            f"Total Nodes:           {self.total_nodes}\n"
            f"Semantic Payload Size: {self.payload_size} chars\n"
            f"Semantic Coverage:     {self.semantic_coverage:.1%}\n"
            f"Structural Coverage:   {self.structural_coverage:.1%}\n"
            f"----------------------------------------\n"
            f"Headings:    {self.stats['headings']}\n"
            f"Paragraphs:  {self.stats['paragraphs']}\n"
            f"Equations:   {self.stats['equations']}\n"
            f"Inline Eq:   {self.stats['inline_equations']}\n"
            f"Tables:      {self.stats['tables']}\n"
            f"Images:      {self.stats['images']}\n"
            f"Captions:    {self.stats['captions']}\n"
            f"Lists:       {self.stats['lists']}\n"
            f"Sections:    {self.stats['sections']}\n"
            f"Unknown:     {self.stats['unknown']}\n"
            f"Composite:   {self.stats['composite']}\n"
            f"Others:      {self.stats['others']}\n"
            "========================================"
        )

class ASTValidator:
    """
    SOTA VALIDATION: Barrera contractual determinista pre-inferencia.
    """
    @staticmethod
    def validate(ast: list[ASTNode], unknown_count_floor: int = 5, max_unknown_ratio: float = 0.15) -> bool:
        if not ast:
            raise ASTValidationError("Falla de integridad: El AST provisto está vacío.")

        seen_ids = set()

        for node in ast:
            if node.node_id in seen_ids:
                raise ASTValidationError(f"Falla de integridad: ID duplicado detectado: {node.node_id}")
            seen_ids.add(node.node_id)

            # SOTA FIX: Validación de balanceo TeX exclusivamente sobre bloques matemáticos display reales
            if node.node_type == ContentNodeType.DISPLAY_EQUATION:
                content = node.text_content or ""
                has_open = bool(LATEX_MATH_OPEN.search(content))
                has_close = bool(LATEX_MATH_CLOSE.search(content))
                if has_open or has_close:
                    if not (has_open and has_close):
                        raise ASTValidationError(
                            f"Falla de sintaxis TeX: El entorno matemático en el nodo {node.node_id} "
                            f"carece de balance estructurado de apertura/cierre válido."
                        )

        return True