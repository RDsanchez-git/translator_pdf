import re
from typing import List, Optional
from core.ast.models import ASTNode, ContentNodeType

class SemanticNodeClassifier:
    """
    Clasificador léxico determinista de nivel compilador para la enmienda de tipos del OCR.
    Valida el balanceo genérico de entornos controlando pertenencia O(1), calcula un scoring
    ponderado con indexación algebraica y aísla funciones matemáticas estándar.
    """
    
    EXPLICIT_MATH_ENVS = {
        "equation", "equation*", "align", "align*", "gather", "gather*", 
        "matrix", "pmatrix", "bmatrix", "Bmatrix", "Vmatrix", "vmatrix", 
        "array", "cases", "cases*", "split", "multline", "multline*", 
        "flalign", "flalign*", "subequations", "aligned", "aligned*", 
        "alignedat", "alignedat*"
    }

    def __init__(self, minimum_score: int = 6):
        self._minimum_score = minimum_score
        self._version = "12.00.5"
        
        self._TARGET_NODE_TYPES = {
            ContentNodeType.PARAGRAPH,
            ContentNodeType.UNKNOWN,
            ContentNodeType.MACRO_CHUNK
        }

        self._balanced_environment = re.compile(r'\\begin\{([a-zA-Z*]+)\}.*?\\end\{\1\}', re.DOTALL)
        self._display_math_balanced = re.compile(r'\$\$(.+?)\$\$', re.DOTALL)
        self._display_bracket_math = re.compile(r'\\\[(.+?)\\\]', re.DOTALL)
        self._inline_paren_math = re.compile(r'\\\((.+?)\\\)', re.DOTALL)

        self._greek_and_advanced_unicode = re.compile(
            r'[\u03B1-\u03C9\u2200-\u22FF\u2190-\u21FFℝℤℚℂ∈∉⊂⊆⇒⇔∂∇∞×÷±√]'
        )
        self._math_operators = re.compile(r'[=+\-*/]')
        self._inline_dollar_balanced = re.compile(r'\$[^$\n]+\$')
        self._latex_commands = re.compile(r'\\[a-zA-Z]+')
        self._algebraic_indexing = re.compile(r'\b[a-zA-Z](?:_[a-zA-Z0-9]+|\^[a-zA-Z0-9]+)')
        self._math_functions = re.compile(r'\b(sin|cos|tan|log|ln|exp|max|min|argmax|argmin)\b')

        self._financial_noise = re.compile(
            r'\b(USD|EUR|MM|M|B|Growth|Revenue|Q[1-4]|Profit|Turnover|Margin)\b', 
            re.IGNORECASE
        )

    def _infer_heading(self, node: ASTNode, text_stripped: str) -> Optional[ASTNode]:
        """Inferencia estructural SOTA integrada en la fase de clasificación."""
        if node.type == ContentNodeType.HEADING or text_stripped.startswith("#"):
            level = 1
            if text_stripped.startswith("#"):
                count = 0
                for char in text_stripped:
                    if char == "#":
                        count += 1
                    else:
                        break
                level = min(count, 6)
            
            new_metadata = dict(node.metadata) if node.metadata else {}
            new_metadata["heading_level"] = level
            
            return node.model_copy(update={
                "type": ContentNodeType.HEADING,
                "metadata": new_metadata
            })
        return None

    def classify_node(self, node: ASTNode) -> ASTNode:
        text = node.content or ""
        text_stripped = text.strip()
        
        # 1. EARLY GATE: Centralización de la clasificación jerárquica
        heading_node = self._infer_heading(node, text_stripped)
        if heading_node:
            return heading_node

        # Filtro de exclusión para procesamiento heurístico ordinario
        if node.type not in self._TARGET_NODE_TYPES or not text_stripped:
            return node

        # ESTRATEGIA NIVEL A: Evaluación Estructural Balanceada Inmediata
        env_match = self._balanced_environment.search(text_stripped)
        if env_match and env_match.group(1) in self.EXPLICIT_MATH_ENVS:
            return self._mutate_node_type(node, ContentNodeType.EQUATION, "explicit_latex_structure", 999)

        if (
            self._display_math_balanced.search(text_stripped) or
            self._display_bracket_math.search(text_stripped) or
            self._inline_paren_math.search(text_stripped)
        ):
            return self._mutate_node_type(node, ContentNodeType.EQUATION, "explicit_latex_structure", 999)

        # ESTRATEGIA NIVEL B: Scoring Ponderado con Aislamiento de Ruido
        greek_count = len(self._greek_and_advanced_unicode.findall(text_stripped))
        operator_count = len(self._math_operators.findall(text_stripped))
        latex_cmd_count = len(self._latex_commands.findall(text_stripped))
        algebraic_index_count = len(self._algebraic_indexing.findall(text_stripped))
        func_count = len(self._math_functions.findall(text_stripped))
        
        inline_dollar_count = 0
        for match in self._inline_dollar_balanced.finditer(text_stripped):
            inner_content = match.group(0).replace("$", "").strip()
            if not inner_content.isdigit():
                inline_dollar_count += 1

        calculated_score = (
            (greek_count * 3) +
            (operator_count * 2) +
            (latex_cmd_count * 3) +
            (inline_dollar_count * 4) +
            (algebraic_index_count * 3) +
            (func_count * 3)
        )

        if self._financial_noise.search(text_stripped) and calculated_score < self._minimum_score:
            return node

        strong_signal = (
            greek_count > 0 or 
            latex_cmd_count > 0 or 
            inline_dollar_count > 0 or 
            algebraic_index_count > 0 or
            func_count > 0
        )

        if strong_signal and calculated_score >= self._minimum_score:
            return self._mutate_node_type(node, ContentNodeType.EQUATION, "weighted_heuristic_score", calculated_score)

        return node

    def _mutate_node_type(self, node: ASTNode, new_type: ContentNodeType, reason: str, score: int) -> ASTNode:
        new_cp = dict(node.control_plane)
        new_cp["classifier_reclassified_from"] = node.type.value if hasattr(node.type, "value") else str(node.type)
        new_cp["classifier_reason"] = reason
        new_cp["classifier_score"] = score
        new_cp["classifier_version"] = self._version
        
        return node.model_copy(update={
            "type": new_type,
            "control_plane": new_cp
        })

    def classify_batch(self, nodes: List[ASTNode]) -> List[ASTNode]:
        return [self.classify_node(node) for node in nodes]