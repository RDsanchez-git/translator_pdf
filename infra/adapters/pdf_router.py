# infra/adapters/pdf_router.py
"""
NADR-02 §5.1 R1: Adaptador de infraestructura que implementa PdfTypeDetectorPort.
Encapsula el uso de fitz (PyMuPDF) fuera del dominio core.
"""

import logging
import fitz

logger = logging.getLogger(__name__)


class PyMuPdfTypeDetector:
    """
    Adaptador de infraestructura que implementa PdfTypeDetectorPort.
    Usa fitz para analizar densidad de caracteres por página.
    """
    
    def detect(self, pdf_path: str) -> tuple[str, list[int]]:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        if total_pages == 0:
            doc.close()
            raise ValueError("PDF vacío o corrupto.")
            
        digital_pages = 0
        empty_pages: list[int] = []
        
        for page_num in range(total_pages):
            page = doc[page_num]
            raw_text = page.get_text("text")
            text_str = raw_text if isinstance(raw_text, str) else ""
            
            if len(text_str.strip()) > 300:
                digital_pages += 1
            else:
                empty_pages.append(page_num)
                
        doc.close()
        
        ratio = digital_pages / total_pages
        logger.info(f"Análisis del Router: {digital_pages}/{total_pages} páginas digitales (Ratio: {ratio:.2f})")
        
        if ratio > 0.8:
            return "DIGITAL", empty_pages
        elif ratio > 0.2:
            return "HYBRID", empty_pages
        else:
            return "SCANNED", empty_pages