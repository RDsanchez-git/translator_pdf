import fitz
import time

def measure_pdf_density(pdf_path: str):
    print(f"=== Telemetría de Extracción: {pdf_path} ===")
    start_time = time.time()
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    char_counts: list[int] = []
    
    for i in range(total_pages):
        page = doc[i]
        # SOTA: Garantía estricta de tipo en tiempo de análisis estático
        raw_text = page.get_text("text")
        text_str = raw_text if isinstance(raw_text, str) else ""
        
        chars = len(text_str.strip())
        char_counts.append(chars)
        print(f"Página {i+1}: {chars} caracteres")
        
    doc.close()
    
    elapsed = time.time() - start_time
    avg_chars = sum(char_counts) / total_pages if total_pages else 0
    
    print("\n=== Resultados ===")
    print(f"Páginas totales: {total_pages}")
    print(f"Promedio general: {avg_chars:.0f} chars/página")
    print(f"Página más vacía: {min(char_counts)} chars")
    print(f"Página más densa: {max(char_counts)} chars")
    print(f"Tiempo de lectura I/O: {elapsed:.4f} segundos")

if __name__ == "__main__":
    measure_pdf_density("tests/fixtures/sample_3_pages.pdf")