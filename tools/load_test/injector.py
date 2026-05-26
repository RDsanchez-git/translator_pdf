import sys
import time
import uuid
import argparse
from pathlib import Path

def launch_load_test(source_pdf: str, num_copies: int, target_inbox: str):
    source_path = Path(source_pdf)
    inbox_path = Path(target_inbox)
    
    if not source_path.exists():
        print(f"[ERROR] El PDF de control especificado no existe: {source_path.absolute()}", flush=True)
        sys.exit(1)
        
    if not inbox_path.exists():
        print(f"[INFO] Creando directorio Inbox objetivo: {inbox_path.absolute()}", flush=True)
        inbox_path.mkdir(parents=True, exist_ok=True)
        
    print("=" * 65, flush=True)
    print("        SOTA SRE LOAD INJECTOR - INICIALIZANDO FASE 8B PROFUNDA", flush=True)
    print("=" * 65, flush=True)
    print(f"PDF Origen:       {source_path.name} ({source_path.stat().st_size / 1024:.1f} KB)", flush=True)
    print(f"Copias a emitir:  {num_copies} (Mutación binaria unica activa)", flush=True)
    print(f"Destino (Inbox):  {inbox_path.absolute()}", flush=True)
    print("-" * 65, flush=True)
    
    start_time = time.time()
    print("[EJECUCIÓN] Inyectando rafaga concurrente con mutacion de hash...", flush=True)
    
    generated_files = []
    
    try:
        with open(source_path, "rb") as f:
            pdf_bytes = f.read()
    except IOError as err:
        print(f"[CRÍTICO] Fallo leyendo archivo origen: {err}", flush=True)
        sys.exit(1)
        
    for i in range(1, num_copies + 1):
        unique_id = uuid.uuid4().hex[:8]
        templated_name = f"LOAD_TEST_{unique_id}_{source_path.stem}.pdf"
        destination = inbox_path / templated_name
        
        try:
            salt = f"\n%%SRE_SALT_{unique_id}_{i}%%\n".encode("utf-8")
            with open(destination, "wb") as f_out:
                f_out.write(pdf_bytes)
                f_out.write(salt)
            generated_files.append(destination)
        except IOError as err:
            print(f"[CRÍTICO] Fallo de I/O escribiendo copia {i}: {err}", flush=True)
            sys.exit(1)
            
    delta_injection = time.time() - start_time
    print("-" * 65, flush=True)
    print("[OK] Inyeccion completada exitosamente.", flush=True)
    print(f"Tiempo de rafaga: {delta_injection:.4f} segundos.", flush=True)
    print(f"Throughput de Ingesta Local: {num_copies / (delta_injection if delta_injection > 0 else 0.001):.2f} docs/sec", flush=True)
    print("=" * 65, flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inyector de carga.")
    parser.add_argument("--source", type=str, default="input.pdf")
    parser.add_argument("--copies", type=int, default=5)
    parser.add_argument("--inbox", type=str, default="data/inbox")
    
    args = parser.parse_args()
    launch_load_test(source_pdf=args.source, num_copies=args.copies, target_inbox=args.inbox)