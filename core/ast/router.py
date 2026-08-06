# core/ast/router.py
"""
NADR-02 §5.1 R1: Enrutador de dominio agnóstico a infraestructura.

TRANSICIONAL: Este módulo preserva la API pública existente mientras
los consumidores migran al puerto PdfTypeDetectorPort directamente.
Retirar en Gate 3 cuando no existan consumidores (DF-10).
"""

import logging
from core.ast.ports import PdfTypeDetectorPort

logger = logging.getLogger(__name__)


class PDFRouter:
    """
    Enrutador de ingesta determinista.
    
    NADR-02 §5.1 R1: No importa fitz directamente.
    Delega la detección a un adaptador inyectado por constructor.
    
    NOTA TRANSICIONAL: Esta clase preserva compatibilidad con consumidores
    existentes. Una vez que todos migren al puerto directamente, se elimina.
    Ver DF-10 en el Deferred Findings Register.
    """
    
    def __init__(self, detector: PdfTypeDetectorPort):
        self._detector = detector
    
    def detect_pdf_type(self, pdf_path: str) -> tuple[str, list[int]]:
        """
        Detecta el tipo de PDF delegando al adaptador inyectado.
        Retorna (tipo, páginas_vacías) donde tipo es DIGITAL/HYBRID/SCANNED.
        """
        return self._detector.detect(pdf_path)