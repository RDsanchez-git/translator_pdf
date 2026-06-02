from core.ast.models import NodeType, ContentNodeType, StructuralNodeType

class TranslationRouter:
    """Contrato semántico descentralizado de aplicación. Aísla las reglas de ruteo del worker."""
    _POLICY_MAP = {
        # --- PRESERVE (Passthrough directo) ---
        ContentNodeType.EQUATION: "PRESERVE",
        ContentNodeType.INLINE_EQUATION: "PRESERVE",
        ContentNodeType.TABLE: "PRESERVE",
        ContentNodeType.CODE_BLOCK: "PRESERVE",
        ContentNodeType.ALGORITHM: "PRESERVE",
        ContentNodeType.FIGURE: "PRESERVE",
        ContentNodeType.IMAGE: "PRESERVE",
        ContentNodeType.COMPOSITE_BLOCK: "PRESERVE",
        ContentNodeType.UNKNOWN: "PRESERVE",
        ContentNodeType.CITATION: "PRESERVE",
        ContentNodeType.REFERENCE_ENTRY: "PRESERVE",
        ContentNodeType.BIBLIOGRAPHY: "PRESERVE",
        
        # --- TRANSLATE (Inferencia LLM) ---
        ContentNodeType.PARAGRAPH: "TRANSLATE",
        ContentNodeType.MACRO_CHUNK: "TRANSLATE",
        ContentNodeType.CAPTION: "TRANSLATE",
        ContentNodeType.LIST: "TRANSLATE",
        ContentNodeType.LIST_ITEM: "TRANSLATE",
        ContentNodeType.FOOTNOTE: "TRANSLATE",
        
        # --- FALLBACKS ESTRUCTURALES ---
        StructuralNodeType.DOCUMENT: "PRESERVE",
        StructuralNodeType.PART: "PRESERVE",
        StructuralNodeType.CHAPTER: "PRESERVE",
        StructuralNodeType.SECTION: "PRESERVE",
        StructuralNodeType.SUBSECTION: "PRESERVE"
    }

    @classmethod
    def get_strategy(cls, node_type: NodeType) -> str:
        """Devuelve la estrategia operativa abstrayendo al invocador de las reglas del negocio."""
        return cls._POLICY_MAP.get(node_type, "PRESERVE")