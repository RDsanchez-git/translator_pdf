import re
from typing import Type, Any, List, Optional, Pattern
from core.layout.base import LayoutStage, PipelineContext
from core.layout.models import LayoutBlockCollection

class LogicalClassifier(LayoutStage[LayoutBlockCollection, LayoutBlockCollection]):
    """Sub-etapa de la Fase 16.1: Infiere el tipo lógico (LayoutBlockType) de cada bloque 
    analizando firmas textuales, sintaxis matemática y metadatos nativos del OCR."""

    INPUT_TYPE: Type[Any] = LayoutBlockCollection
    OUTPUT_TYPE: Type[Any] = LayoutBlockCollection

    # Compilación estática de patrones SOTA para alto rendimiento O(n)
    MATH_PATTERNS: List[Pattern[str]] = [
        re.compile(r"\\begin\{(equation|align|gather|amsfonts|matrix|bmatrix|vmatrix)\}"),
        re.compile(r"\$\$.*?\$\$", re.DOTALL),
        re.compile(r"^\s*([Δ∑∏∫∬≡≈∝√─┬┴├┤┼═║╚╝╔╗]+|[a-zA-Z0-9_\+\-\*\/\\=\(\)\s\.,]{2,})\s*=\s*.+$"),
        re.compile(r"^\s*\\\[.*\\\]\s*$", re.DOTALL)
    ]

    CODE_PATTERNS: List[Pattern[str]] = [
        re.compile(r"^\s*(def|class|import|from|return|if\s+.*:|for\s+.*in.*:)\s+"),
        re.compile(r"[{};\.].*\n?.*[{};\.]")
    ]

    LIST_PATTERNS: List[Pattern[str]] = [
        re.compile(r"^\s*(\d+[\.\)]|-\s+|\*\s+|\[\s*[xX\s]\s*\])\s+"),
        re.compile(r"^\s*\([a-zA-Z0-9]\)\s+")
    ]

    @property
    def stage_name(self) -> str:
        return "logical_classifier"

    @property
    def supports_parallel_execution(self) -> bool:
        return True

    def _execute(self, data: LayoutBlockCollection, context: PipelineContext) -> LayoutBlockCollection:
        classified_blocks = []
        
        for block in data.blocks:
            # 1. Intentar clasificar usando metadatos nativos del proveedor de extracción
            inferred_type = self._resolve_from_provider(block.provider_native_id)
            
            # 2. Si el proveedor es laxo, aplicar motor de firmas estructurales
            if not inferred_type:
                inferred_type = self._infer_from_content(block.content)
            
            classified_blocks.append(block.model_copy(
                update={"logical_type": inferred_type}
            ))
            
        return LayoutBlockCollection(blocks=classified_blocks)

    def _resolve_from_provider(self, provider_id: Optional[str]) -> Optional[str]:
        """Mapea tipos de bloques explícitos inyectados por APIs avanzadas (Azure/Docling)."""
        if not provider_id:
            return None
            
        pid = provider_id.upper()
        if "TITLE" in pid or "HEADING" in pid:
            return "TITLE"
        if "TABLE" in pid:
            return "TABLE"
        if "IMAGE" in pid or "FIGURE" in pid:
            return "IMAGE"
        if "FORMULA" in pid or "EQUATION" in pid:
            return "DISPLAY_EQUATION"
        return None

    def _infer_from_content(self, content: str) -> str:
        """Aplica la batería de expresiones regulares compiladas sobre el cuerpo del texto."""
        cleaned = content.strip()
        if not cleaned:
            return "PARAGRAPH"

        # Detección heurística de títulos basada en fisonomía de longitud
        if len(cleaned) < 120 and cleaned.isupper() and not cleaned.endswith((".", ":", ";")):
            return "TITLE"

        # Bucle de evaluación O(1) por categoría debido a límites estáticos
        for pattern in self.MATH_PATTERNS:
            if pattern.search(cleaned):
                return "DISPLAY_EQUATION"

        for pattern in self.CODE_PATTERNS:
            if pattern.search(cleaned):
                return "CODE"

        for pattern in self.LIST_PATTERNS:
            if pattern.search(cleaned):
                return "LIST"

        return "PARAGRAPH"