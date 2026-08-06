# core/ast/ports.py
"""
NADR-02 §5.1 R1: Puerto de dominio para detección de tipo de PDF.
El dominio define el contrato; la infraestructura lo implementa.
"""

from typing import Protocol


class PdfTypeDetectorPort(Protocol):
    """
    Puerto de dominio para detección de tipo de PDF.
    
    Retorna una tupla (tipo, páginas_vacías) donde tipo es uno de:
    "DIGITAL", "HYBRID", "SCANNED"
    """
    def detect(self, pdf_path: str) -> tuple[str, list[int]]: ...