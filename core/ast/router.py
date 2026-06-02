import fitz
import logging

logger = logging.getLogger(__name__)

class PDFRouter:
    """Enrutador de ingesta determinista basado en densidad de caracteres por página."""
    
    @staticmethod
    def detect_pdf_type(pdf_path: str) -> tuple[str, list[int]]:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        if total_pages == 0:
            raise ValueError("PDF vacío o corrupto.")
            
        digital_pages = 0
        empty_pages: list[int] = []
        
        for page_num in range(total_pages):
            page = doc[page_num]
            # SOTA: Garantía estricta de tipo en tiempo de análisis estático
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