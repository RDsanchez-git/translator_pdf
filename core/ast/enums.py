from enum import Enum

class ContentNodeType(str, Enum):
    """SOTA: Tipos semánticos puros del AST V2. Representación plana y secuencial."""
    COMPOSITE_BLOCK = "composite_block"  # SOTA: Bloque híbrido o ilegible irrompible
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    DISPLAY_EQUATION = "display_equation"
    INLINE_EQUATION = "inline_equation"
    TABLE_SIMPLE = "table_simple"
    TABLE_COMPLEX = "table_complex"
    IMAGE = "image"
    CAPTION = "caption"
    CODE = "code"
    LIST = "list"

class TranslationStrategy(str, Enum):
    """SOTA: Determinismo de procesamiento por estrategia de nodo."""
    TRANSLATE = "translate"
    PASSTHROUGH = "passthrough"
    KEEP_ORIGINAL = "keep_original"
    OMIT = "omit"
    DEFER = "defer"

class HeadingLevel(str, Enum):
    """Gobernanza de niveles jerárquicos relativos para el motor estructural."""
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    UNKNOWN = "unknown"

class SemanticOrigin(str, Enum):
    """Métrica de observabilidad para el control de confianza downstream."""
    PDF_TEXT = "pdf_text"
    OCR = "ocr"
    MERGED = "merged"
    SYNTHESIZED = "synthesized"