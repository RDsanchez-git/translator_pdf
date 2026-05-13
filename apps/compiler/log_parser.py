import re
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class ErrorType(str, Enum):
    MATH_MODE = "math_mode_failure"
    UNDEFINED_MACRO = "undefined_macro"
    UNBALANCED_ENV = "unbalanced_environment"
    AMSMATH_TAG_ERROR = "amsmath_tag_error"
    UNBALANCED_BRACKETS = "unbalanced_brackets"
    UNKNOWN = "unknown"
    EMPTY_DOCUMENT = "empty_document_error"

class ParsedError(BaseModel):
    type: ErrorType
    description: str
    line_number: Optional[int] = None
    raw_context: str

class LogParser:
    @staticmethod
    def parse(stderr: str) -> ParsedError:
        """SOTA: Analizador léxico determinista para errores de Tectonic/XeTeX."""
        
        # Extracción estricta de la línea de error (ej: "l.73" o "line 73")
        line_match = re.search(r'(?:l\.|line\s+)(\d+)', stderr, re.IGNORECASE)
        line_num = int(line_match.group(1)) if line_match else None
        
        # 1. Fallo de Modo Matemático
        if "Missing $ inserted" in stderr or "Display math should end with $$" in stderr:
            return ParsedError(
                type=ErrorType.MATH_MODE,
                description="Falta delimitador matemático ($). El texto plano rompió el entorno o una ecuación no se cerró.",
                line_number=line_num,
                raw_context=LogParser._extract_context(stderr, "Missing $")
            )
            
        # 2. Macros Inexistentes
        if "Undefined control sequence" in stderr:
            return ParsedError(
                type=ErrorType.UNDEFINED_MACRO,
                description="Se detectó un comando LaTeX no reconocido, probablemente mal escapado o inventado.",
                line_number=line_num,
                raw_context=LogParser._extract_context(stderr, "Undefined control sequence")
            )
            
        # 3. Entornos Rotos
        if "ended by \\end" in stderr and "\\begin" in stderr:
            return ParsedError(
                type=ErrorType.UNBALANCED_ENV,
                description="Desajuste crítico entre \\begin{} y \\end{}. Entorno no cerrado correctamente.",
                line_number=line_num,
                raw_context=LogParser._extract_context(stderr, "ended by \\end")
            )
            
        # 4. Llaves Desbalanceadas
        if "Missing } inserted" in stderr or "Missing { inserted" in stderr:
            return ParsedError(
                type=ErrorType.UNBALANCED_BRACKETS,
                description="Desbalance estructural en llaves { }.",
                line_number=line_num,
                raw_context=LogParser._extract_context(stderr, "Missing }")
            )
        
        if "\\tag not allowed here" in stderr:
            return ParsedError(
                type=ErrorType.AMSMATH_TAG_ERROR,
                description="El comando \\tag{} es ilegal fuera de entornos equation/align.",
                line_number=line_num,
                raw_context=LogParser._extract_context(stderr, "\\tag not allowed here")
            )
        
        # 5. Documento Vacío (Fallo en cascada de red)
        if "did not produce \"doc.xdv\"" in stderr or "your document is empty" in stderr:
            return ParsedError(
                type=ErrorType.EMPTY_DOCUMENT,
                description="Tectonic recibió un documento sin contenido. Todos los fragmentos fallaron en la red o en la validación.",
                line_number=line_num,
                raw_context=LogParser._extract_context(stderr, "doc.xdv")
            )

        # Fallback de captura genérica
        return ParsedError(
            type=ErrorType.UNKNOWN,
            description="Fallo de compilación no tipado por el analizador.",
            line_number=line_num,
            raw_context=stderr[-500:] if stderr else "Sin salida stderr."
        )

    @staticmethod
    def _extract_context(log: str, keyword: str) -> str:
        """Aísla la zona de impacto en el volcado de error para alimentar al LLM."""
        lines = log.split('\n')
        for i, line in enumerate(lines):
            if keyword in line:
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                return "\n".join(lines[start:end])
        return log[-300:] if len(log) > 300 else log